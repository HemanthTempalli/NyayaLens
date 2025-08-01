from datetime import datetime
from flask_sqlalchemy import SQLAlchemy

# Create a db instance that will be configured later
db = SQLAlchemy()

class CaseQuery(db.Model):
    """Model to store case queries and responses"""
    id = db.Column(db.Integer, primary_key=True)
    case_type = db.Column(db.String(100), nullable=False)
    case_number = db.Column(db.String(100), nullable=False)
    filing_year = db.Column(db.String(10), nullable=False)
    query_timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    success = db.Column(db.Boolean, default=False)
    error_message = db.Column(db.Text)
    raw_response = db.Column(db.Text)
    
    # Parsed data fields
    parties_plaintiff = db.Column(db.Text)
    parties_defendant = db.Column(db.Text)
    filing_date = db.Column(db.String(50))
    next_hearing_date = db.Column(db.String(50))
    case_status = db.Column(db.String(200))
    
    def __repr__(self):
        return f'<CaseQuery {self.case_type}/{self.case_number}/{self.filing_year}>'

class CaseOrder(db.Model):
    """Model to store case orders and judgments"""
    id = db.Column(db.Integer, primary_key=True)
    query_id = db.Column(db.Integer, db.ForeignKey('case_query.id'), nullable=False)
    order_date = db.Column(db.String(50))
    order_title = db.Column(db.String(500))
    pdf_url = db.Column(db.String(1000))
    order_type = db.Column(db.String(100))  # Order, Judgment, etc.
    
    query = db.relationship('CaseQuery', backref='orders')
    
    def __repr__(self):
        return f'<CaseOrder {self.order_title}>'
