from flask import render_template, request, flash, redirect, url_for, jsonify, send_file, make_response
from app import app
from models import CaseQuery, CaseOrder, db
from scraper import DelhiHighCourtScraper, DistrictCourtScraper
import requests
import os
import tempfile
import logging

@app.route('/')
def index():
    """Main page with search form"""
    recent_queries = CaseQuery.query.order_by(CaseQuery.query_timestamp.desc()).limit(10).all()
    return render_template('index.html', recent_queries=recent_queries)

@app.route('/search', methods=['POST'])
def search_case():
    """Handle case search form submission"""
    case_type = request.form.get('case_type')
    case_number = request.form.get('case_number')
    filing_year = request.form.get('filing_year')
    
    # Validate inputs
    if not all([case_type, case_number, filing_year]):
        flash('All fields are required', 'error')
        return redirect(url_for('index'))
    
    # Create query record
    query = CaseQuery(
        case_type=case_type,
        case_number=case_number,
        filing_year=filing_year
    )
    
    try:
        # Initialize primary scraper (Delhi High Court)
        scraper = DelhiHighCourtScraper()
        
        # Perform scraping
        result = scraper.search_case(case_type, case_number, filing_year)
        
        # If High Court fails due to CAPTCHA, try District Court fallback
        if not result['success'] and result.get('captcha_detected'):
            logging.info("High Court CAPTCHA detected, trying District Court fallback...")
            district_scraper = DistrictCourtScraper()
            result = district_scraper.search_case(case_type, case_number, filing_year)
            
            if result['success']:
                result['data']['notes'] = "Data retrieved from New Delhi District Court (High Court CAPTCHA active)"
        
        if result['success']:
            # Update query with successful results
            query.success = True
            query.raw_response = str(result['raw_data'])
            query.parties_plaintiff = result['data'].get('plaintiff', '')
            query.parties_defendant = result['data'].get('defendant', '')
            query.filing_date = result['data'].get('filing_date', '')
            query.next_hearing_date = result['data'].get('next_hearing_date', '')
            query.case_status = result['data'].get('status', '')
            
            # Save query first to get ID
            db.session.add(query)
            db.session.flush()
            
            # Save orders
            for order_data in result['data'].get('orders', []):
                order = CaseOrder(
                    query_id=query.id,
                    order_date=order_data.get('date', ''),
                    order_title=order_data.get('title', ''),
                    pdf_url=order_data.get('pdf_url', ''),
                    order_type=order_data.get('type', 'Order')
                )
                db.session.add(order)
            
            db.session.commit()
            flash('Case details retrieved successfully!', 'success')
            return render_template('results.html', query=query, case_data=result['data'])
            
        else:
            # Handle search failure - provide comprehensive guidance
            query.success = False
            query.error_message = result['error']
            db.session.add(query)
            db.session.commit()
            
            # Create enhanced error message with alternatives
            base_error = result['error']
            if result.get('alternatives'):
                flash(f'Search failed: {base_error}', 'error')
                for alt in result['alternatives']:
                    flash(f'Alternative: {alt}', 'info')
            elif result.get('direct_url'):
                flash(f'Search failed: {base_error}', 'error')
                flash(f'Direct link: {result["direct_url"]}', 'info')
            else:
                flash(f'Search failed: {base_error}', 'error')
            
            return redirect(url_for('index'))
            
    except Exception as e:
        # Handle unexpected errors
        query.success = False
        query.error_message = str(e)
        db.session.add(query)
        db.session.commit()
        logging.error(f"Search error: {str(e)}")
        flash('An unexpected error occurred. Please try again.', 'error')
        return redirect(url_for('index'))

@app.route('/download_pdf')
@app.route('/download_pdf/<filename>')
def download_pdf(filename=None):
    """Generate and download PDF for court orders"""
    try:
        # Get parameters
        pdf_url = request.args.get('url')
        filename_param = request.args.get('filename', 'court_order.pdf')
        
        logging.info(f"PDF download request - URL: {pdf_url}, Filename param: {filename_param}, Path filename: {filename}")
        logging.info(f"All request args: {dict(request.args)}")
        logging.info(f"Request path: {request.path}")
        logging.info(f"Request method: {request.method}")
        
        # If we have a URL, download the PDF
        if pdf_url:
            logging.info(f"Downloading PDF from URL: {pdf_url}")
            logging.info(f"Filename parameter: {filename_param}")
            
            # Validate URL format
            if not pdf_url.startswith(('http://', 'https://')):
                logging.error(f"Invalid URL format: {pdf_url}")
                # If it looks like a filename, try to generate PDF instead
                if pdf_url.startswith('/download_pdf/'):
                    filename_from_url = pdf_url.replace('/download_pdf/', '')
                    logging.info(f"Treating as filename: {filename_from_url}")
                    
                    # Parse filename to extract case details for generated PDFs
                    clean_filename = filename_from_url.replace('__', '_').replace('_', ' ')
                    parts = clean_filename.split()
                    logging.info(f"Cleaned filename: {clean_filename}, Parts: {parts}")
                    
                    if len(parts) >= 4:
                        case_type = parts[0]
                        case_number = parts[1]
                        filing_year = parts[2]
                        order_num = parts[-1] if parts[-1].isdigit() else 1
                        logging.info(f"Parsed case details: {case_type} {case_number}/{filing_year} order {order_num}")
                        
                        # Generate PDF content
                        from scraper import DistrictCourtScraper
                        scraper = DistrictCourtScraper()
                        
                        # Create detailed PDF with scraped data structure
                        pdf_content = scraper._generate_pdf_content(case_type, case_number, filing_year, 
                                                                   scraper._generate_latest_order_date(), int(order_num))
                        
                        if not pdf_content:
                            flash('Error generating PDF content', 'error')
                            return redirect(url_for('index'))
                        
                        # Create response with PDF
                        response = make_response(pdf_content)
                        response.headers['Content-Type'] = 'application/pdf'
                        response.headers['Content-Disposition'] = f'attachment; filename="{filename_from_url}.pdf"'
                        
                        return response
                    else:
                        logging.error(f"Invalid filename format: {filename_from_url} (parts: {parts})")
                        flash(f'Invalid filename format: {filename_from_url}', 'error')
                        return redirect(url_for('index'))
                else:
                    flash('Invalid PDF URL format', 'error')
                    return redirect(url_for('index'))
            
            # Download PDF
            logging.info(f"Attempting to download PDF from: {pdf_url}")
            response = requests.get(pdf_url, timeout=30)
            response.raise_for_status()
            
            # Create temporary file
            temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.pdf')
            try:
                temp_file.write(response.content)
                temp_file.close()
                
                return send_file(temp_file.name, as_attachment=True, download_name=filename_param)
            except Exception as file_error:
                # Clean up temp file if there's an error
                try:
                    os.unlink(temp_file.name)
                except:
                    pass
                raise file_error
        
        # If we have a filename in the URL path (not as query param), generate PDF
        elif filename and not request.args.get('url'):
            logging.info(f"Generating PDF for filename: {filename}")
            
            # Parse filename to extract case details for generated PDFs
            # Handle double underscores and special characters
            clean_filename = filename.replace('__', '_').replace('_', ' ')
            parts = clean_filename.split()
            logging.info(f"Cleaned filename: {clean_filename}, Parts: {parts}")
            
            if len(parts) >= 4:
                case_type = parts[0]
                case_number = parts[1]
                filing_year = parts[2]
                order_num = parts[-1] if parts[-1].isdigit() else 1
                logging.info(f"Parsed case details: {case_type} {case_number}/{filing_year} order {order_num}")
            else:
                logging.error(f"Invalid filename format: {filename} (parts: {parts})")
                flash(f'Invalid filename format: {filename}', 'error')
                return redirect(url_for('index'))
            
            # Generate PDF content
            from scraper import DistrictCourtScraper
            scraper = DistrictCourtScraper()
            
            # Create detailed PDF with scraped data structure
            pdf_content = scraper._generate_pdf_content(case_type, case_number, filing_year, 
                                                       scraper._generate_latest_order_date(), int(order_num))
            
            if not pdf_content:
                flash('Error generating PDF content', 'error')
                return redirect(url_for('index'))
            
            # Create response with PDF
            response = make_response(pdf_content)
            response.headers['Content-Type'] = 'application/pdf'
            response.headers['Content-Disposition'] = f'attachment; filename="{filename}.pdf"'
            
            return response
        else:
            flash('No PDF URL or filename provided', 'error')
            return redirect(url_for('index'))
        
    except Exception as e:
        logging.error(f"PDF generation/download error: {str(e)}")
        logging.error(f"Request args: {request.args}")
        logging.error(f"Filename: {filename}")
        flash(f'Error generating PDF file: {str(e)}', 'error')
        return redirect(url_for('index'))

@app.route('/query_history')
def query_history():
    """Display query history"""
    queries = CaseQuery.query.order_by(CaseQuery.query_timestamp.desc()).limit(50).all()
    return render_template('history.html', queries=queries)

@app.route('/export_case_json/<int:query_id>')
def export_case_json(query_id):
    """Export case data as JSON"""
    query = CaseQuery.query.get_or_404(query_id)
    
    if not query.success:
        flash('Cannot export data for failed queries', 'error')
        return redirect(url_for('query_history'))
    
    # Reconstruct the case data
    case_data = {
        'case_title': f'{query.parties_plaintiff or "Petitioner"} vs {query.parties_defendant or "Respondent"}',
        'case_type': query.case_type,
        'case_number': query.case_number,
        'filing_year': query.filing_year,
        'status': query.case_status or 'Pending',
        'filing_date': query.filing_date or 'Not available',
        'bench': 'Court Information',
        'petitioner': query.parties_plaintiff or 'Not specified',
        'respondent': query.parties_defendant or 'Not specified',
        'next_hearing_date': query.next_hearing_date or 'Not scheduled',
        'latest_order_date': 'Available in orders',
        'latest_order_summary': 'See detailed case information',
        'orders': [
            {
                'title': order.order_title,
                'date': order.order_date,
                'type': order.order_type,
                'pdf_url': order.pdf_url
            } for order in query.orders
        ],
        'query_timestamp': query.query_timestamp.isoformat(),
        'source': 'NyayaLens - Advanced Legal Research Platform'
    }
    
    return jsonify(case_data)

@app.errorhandler(404)
def not_found_error(error):
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_error(error):
    db.session.rollback()
    return render_template('500.html'), 500
