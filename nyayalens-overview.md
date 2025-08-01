# NyayaLens
*"Clarity into Cases. Justice in Focus."*

## Overview

NyayaLens is an advanced legal research platform that provides comprehensive case information from Indian courts. Built with Flask and featuring sophisticated web scraping capabilities, the application offers multi-tier CAPTCHA bypass strategies, real PDF document generation, and structured JSON data export. The platform targets Delhi High Court as primary source with automatic fallback to multiple District Court systems, ensuring maximum case information accessibility while maintaining legal compliance.

## User Preferences

Preferred communication style: Simple, everyday language.

## System Architecture

### Frontend Architecture
The application uses a traditional server-side rendered architecture with:
- **Template Engine**: Jinja2 templates with Flask for dynamic HTML generation
- **UI Framework**: Bootstrap 5 with dark theme for responsive design
- **JavaScript**: Vanilla JavaScript for form validation, loading states, and PDF downloads
- **Styling**: Custom CSS for enhanced user experience and form interactions
- **Icons**: Font Awesome for consistent iconography

### Backend Architecture
Built on Flask with the following components:
- **Web Framework**: Flask with SQLAlchemy ORM for database operations
- **Application Structure**: Modular design with separate files for models, routes, and scraper logic
- **Session Management**: Flask sessions with configurable secret key
- **Middleware**: ProxyFix for handling proxy headers in deployment environments
- **Logging**: Python logging module for debugging and monitoring

### Data Layer
- **Database**: SQLite for local development with PostgreSQL support for production
- **Models**: Two main entities - CaseQuery for storing search requests and CaseOrder for storing case documents
- **ORM**: SQLAlchemy with relationship mapping between queries and their associated orders
- **Connection Management**: Connection pooling with automatic reconnection on failures

### Web Scraping Architecture
- **Target Site**: Delhi High Court (delhihighcourt.nic.in) chosen for reliable public access
- **HTTP Client**: Requests library with session management for cookie persistence
- **HTML Parsing**: BeautifulSoup4 for extracting structured data from court website responses
- **Error Handling**: Comprehensive error handling for CAPTCHA challenges, site downtime, and invalid case numbers
- **Browser Simulation**: User-agent headers and session handling to mimic legitimate browser requests

### Data Processing
- **Input Validation**: Server-side validation for case types, numbers, and filing years
- **Data Extraction**: Pattern-based parsing to extract parties' names, dates, and document links
- **Response Logging**: Complete request/response logging for debugging and audit trails
- **PDF Handling**: Direct URL extraction for court documents with download capabilities

### Security Considerations
- **Environment Variables**: Configurable secret keys and database URLs
- **Input Sanitization**: Form validation to prevent injection attacks
- **Rate Limiting**: Session-based requests to avoid overwhelming the court website
- **Error Boundaries**: User-friendly error messages without exposing system internals

## External Dependencies

### Core Framework Dependencies
- **Flask**: Python web framework for application structure
- **Flask-SQLAlchemy**: Database ORM and query builder
- **Werkzeug**: WSGI utilities and ProxyFix middleware

### Web Scraping Dependencies
- **Requests**: HTTP client library for making requests to court websites
- **BeautifulSoup4**: HTML/XML parsing library for data extraction
- **urllib.parse**: URL manipulation for handling court website links

### Frontend Dependencies
- **Bootstrap 5**: CSS framework hosted via CDN for responsive design
- **Font Awesome**: Icon library hosted via CDN for UI elements
- **Custom CSS/JS**: Local static files for application-specific styling and functionality

### Database
- **SQLite**: Default local database for development and small deployments
- **PostgreSQL**: Production database option (configurable via DATABASE_URL)

### Target External Service
- **Delhi High Court Website** (delhihighcourt.nic.in): Primary data source for case information
  - Public case search functionality
  - Document download endpoints
  - No official API - relies on web scraping
  - Potential CAPTCHA protection requiring manual intervention
