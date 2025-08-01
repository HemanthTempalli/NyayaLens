# NyayaLens
*"Clarity into Cases. Justice in Focus."*

A Flask web application that scrapes Indian court data, allowing users to search case information and download legal documents from court websites.

## 🏛️ Target Court

**Delhi High Court** (https://delhihighcourt.nic.in/)

This application specifically targets the Delhi High Court website for case information retrieval. The choice was made due to:
- Reliable public access to case search functionality
- Structured data presentation
- Consistent URL patterns for document access

## 🚀 Features

- **Simple Search Interface**: Easy-to-use form with dropdowns for Case Type, Case Number, and Filing Year
- **Real-time Data Scraping**: Fetches live data from Delhi High Court website
- **Comprehensive Case Details**: Extracts parties' names, filing dates, hearing dates, and case status
- **PDF Download**: Direct download links for court orders and judgments
- **Query Logging**: SQLite database stores all search queries and responses
- **Error Handling**: User-friendly error messages for invalid cases and site downtime
- **Responsive Design**: Bootstrap-based UI that works on all devices

## 🛠️ Tech Stack

**Backend:**
- Flask (Python web framework)
- Flask-SQLAlchemy (Database ORM)
- BeautifulSoup4 (HTML parsing)
- Requests (HTTP client)
- SQLite (Database)

**Frontend:**
- HTML5 & Bootstrap 5
- Vanilla JavaScript
- Font Awesome icons
- Custom CSS

## 📋 Setup Instructions

### Prerequisites
- Python 3.8+
- pip (Python package installer)

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd court-data-fetcher
   ```

2. **Install dependencies**
   ```bash
   pip install flask flask-sqlalchemy requests beautifulsoup4 lxml
   ```

3. **Set environment variables**
   ```bash
   export SESSION_SECRET="your-secret-key-here"
   export DATABASE_URL="sqlite:///court_data.db"
   ```

4. **Run the application**
   ```bash
   python app.py
   ```

5. **Access the application**
   Open your browser and navigate to: `http://127.0.0.1:5000`

## 🔐 CAPTCHA Strategy

### Multi-Tier Bypass Approach
The application implements a comprehensive, legally compliant strategy for handling CAPTCHAs:

#### **Tier 1: Primary Detection & Analysis**
- **Automatic Detection**: Scans for CAPTCHA images, audio elements, and verification text
- **Smart Recognition**: Identifies Delhi High Court's specific CAPTCHA patterns (`audio.jpg`, verification forms)
- **Response Logging**: Documents CAPTCHA encounters for pattern analysis

#### **Tier 2: Fallback Court Systems**
- **District Court Failover**: Automatically switches to New Delhi District Court when High Court CAPTCHA detected
- **Alternative Endpoints**: Uses backup URLs (`newdelhi.dcourts.gov.in`) with potentially different CAPTCHA requirements
- **Cross-System Search**: Maintains search capability across multiple court portals

#### **Tier 3: User Guidance & Manual Options**
- **Direct Website Links**: Provides users with direct URLs to court websites for manual searching
- **Timing Strategies**: Suggests retry timing when CAPTCHA requirements may be relaxed
- **Alternative Case Types**: Recommends trying different case classification if available

### Technical Implementation

**CAPTCHA Detection Code:**
```python
# Multi-method detection approach
captcha_elements = soup.find_all(['img', 'audio'], attrs={
    'src': re.compile(r'captcha|verification|audio', re.I)
}) or soup.find_all(text=re.compile(r'captcha|verification', re.I))

if captcha_elements or 'audio.jpg' in response.text:
    # Trigger fallback strategy
```

**Fallback Execution:**
```python
# Automatic fallback when CAPTCHA detected
if not result['success'] and result.get('captcha_detected'):
    district_scraper = DistrictCourtScraper()
    result = district_scraper.search_case(case_type, case_number, filing_year)
```

### Legal & Ethical Compliance
- **No Automated Solving**: Never attempts to programmatically solve CAPTCHAs
- **Respectful Retry Logic**: Implements delays and reasonable retry limits
- **Public Data Only**: Accesses only publicly available case information
- **Terms of Service**: Respects all court website terms and conditions
- **Transparency**: Clearly documents all bypass methods used

### Success Metrics
- **Fallback Success Rate**: District Court system often provides results when High Court is CAPTCHA-protected
- **User Experience**: Seamless switching between court systems maintains functionality
- **Data Availability**: Combined approach significantly improves case data retrieval success

### Future Enhancements
- **Manual CAPTCHA Interface**: Optional user-solvable CAPTCHA integration
- **Additional Court Systems**: Integration with more district courts across Delhi
- **Intelligent Timing**: Machine learning to predict optimal search timing
- **API Integration**: Direct court API usage where available

## 📊 Database Schema

### CaseQuery Table
- `id`: Primary key
- `case_type`: Type of case (e.g., W.P.(C), CRL.A.)
- `case_number`: Case number
- `filing_year`: Year of filing
- `query_timestamp`: When the search was performed
- `success`: Boolean indicating if search was successful
- `error_message`: Error details if search failed
- `raw_response`: Raw HTML response from court website
- Parsed data fields: `parties_plaintiff`, `parties_defendant`, `filing_date`, `next_hearing_date`, `case_status`

### CaseOrder Table
- `id`: Primary key
- `query_id`: Foreign key to CaseQuery
- `order_date`: Date of the order
- `order_title`: Title/description of the order
- `pdf_url`: URL to PDF document
- `order_type`: Type of document (Order, Judgment, etc.)

## 🎯 Usage Examples

### Search Parameters
- **Case Type**: W.P.(C) (Writ Petition Civil)
- **Case Number**: 1234
- **Filing Year**: 2023
- **Result**: Searches for W.P.(C) 1234/2023

### Supported Case Types
- W.P.(C) - Writ Petition (Civil)
- CRL.A. - Criminal Appeal
- CS(OS) - Civil Suit (Original Side)
- CRL.M.C. - Criminal Misc. Case
- W.P.(CRL) - Writ Petition (Criminal)
- FAO - First Appeal from Order
- RFA - Regular First Appeal
- ARB.P. - Arbitration Petition
- CONT.CAS - Contempt Case
- CRL.REV.P. - Criminal Revision Petition

## 🔧 Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `SESSION_SECRET` | Flask session secret key | Required for production |
| `DATABASE_URL` | Database connection string | `sqlite:///court_data.db` |

## 🚨 Error Handling

The application provides comprehensive error handling for:

- **Invalid Case Numbers**: Clear validation messages
- **Network Issues**: Timeout and connection error handling
- **CAPTCHA Protection**: Graceful degradation with user guidance
- **Site Downtime**: Informative error messages
- **Parsing Failures**: Fallback extraction methods

## 📈 Features Roadmap

### Immediate Enhancements
- [ ] Support for additional courts (District Courts)
- [ ] Enhanced PDF viewer integration
- [ ] Export functionality (CSV, JSON)
- [ ] Advanced search filters

### Future Development
- [ ] User authentication and saved searches
- [ ] Email notifications for case updates
- [ ] API endpoints for programmatic access
- [ ] Mobile app companion

## 🛡️ Security Considerations

- No hard-coded secrets in source code
- Environment variable-based configuration
- SQL injection protection via SQLAlchemy ORM
- XSS protection through template escaping
- Rate limiting considerations for court website requests

## 📜 Legal Disclaimer

This application is developed for educational and research purposes. Users should:

- Verify all information directly from official court websites
- Respect the terms of service of court websites
- Use the tool responsibly and ethically
- Consult legal professionals for official legal proceedings

## 🤝 Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.



---

**Note**: This application targets public court data only and respects all legal and ethical boundaries in web scraping activities.
