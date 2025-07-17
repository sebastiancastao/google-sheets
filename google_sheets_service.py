"""
Google Sheets Service for BOL Processor
Python Flask service that receives CSV data and adds it to Google Sheets
Uses service account authentication (no CORS, no popups)
Works with both .env files (development) and system environment variables (production)
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
import gspread
from google.oauth2.service_account import Credentials
import json
import os
import csv
import io
from datetime import datetime
import logging
from dotenv import load_dotenv

# Load environment variables from .env file if it exists
if os.path.exists('.env'):
    load_dotenv()

# Configure logging
log_level = os.getenv('LOG_LEVEL', 'INFO')
logging.basicConfig(level=getattr(logging, log_level.upper()))
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)  # Enable CORS for all domains

# Configuration
SCOPES = [
    'https://www.googleapis.com/auth/spreadsheets',
    'https://www.googleapis.com/auth/drive'
]

def get_service_account_info():
    """Build service account info from environment variables"""
    required_env_vars = [
        'GOOGLE_PROJECT_ID',
        'GOOGLE_PRIVATE_KEY_ID', 
        'GOOGLE_PRIVATE_KEY',
        'GOOGLE_CLIENT_EMAIL',
        'GOOGLE_CLIENT_ID'
    ]
    
    # Check if all required environment variables are present
    missing_vars = [var for var in required_env_vars if not os.getenv(var)]
    if missing_vars:
        raise ValueError(f"Missing required environment variables: {', '.join(missing_vars)}")
    
    return {
        "type": "service_account",
        "project_id": os.getenv('GOOGLE_PROJECT_ID'),
        "private_key_id": os.getenv('GOOGLE_PRIVATE_KEY_ID'),
        "private_key": os.getenv('GOOGLE_PRIVATE_KEY'),
        "client_email": os.getenv('GOOGLE_CLIENT_EMAIL'),
        "client_id": os.getenv('GOOGLE_CLIENT_ID'),
        "auth_uri": "https://accounts.google.com/o/oauth2/auth",
        "token_uri": "https://oauth2.googleapis.com/token",
        "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
        "client_x509_cert_url": f"https://www.googleapis.com/oauth2/v1/certs/{os.getenv('GOOGLE_CLIENT_EMAIL').replace('@', '%40')}"
    }

def get_config():
    """Get configuration from environment variables"""
    # Allura configuration
    spreadsheet_id = os.getenv('SPREADSHEET_ID')
    sheet_name = os.getenv('SHEET_NAME')
    
    # IHL configuration
    ihl_spreadsheet_id = os.getenv('IHL_SPREADSHEET_ID')
    ihl_sheet_name = os.getenv('IHL_SHEET_NAME')
    
    if not spreadsheet_id:
        raise ValueError("SPREADSHEET_ID environment variable is required")
    if not sheet_name:
        raise ValueError("SHEET_NAME environment variable is required")
    if not ihl_spreadsheet_id:
        raise ValueError("IHL_SPREADSHEET_ID environment variable is required")
    if not ihl_sheet_name:
        raise ValueError("IHL_SHEET_NAME environment variable is required")
    
    # Use PORT from cloud platforms (like Render) if available, otherwise fall back to FLASK_PORT
    port = os.getenv('PORT') or os.getenv('FLASK_PORT', '5550')
    
    return {
        'spreadsheet_id': spreadsheet_id,
        'sheet_name': sheet_name,
        'ihl_spreadsheet_id': ihl_spreadsheet_id,
        'ihl_sheet_name': ihl_sheet_name,
        'flask_host': os.getenv('FLASK_HOST', '0.0.0.0'),
        'flask_port': int(port),
        'flask_debug': os.getenv('FLASK_DEBUG', 'True').lower() == 'true'
    }

# Get configuration
try:
    config = get_config()
    SPREADSHEET_ID = config['spreadsheet_id']
    SHEET_NAME = config['sheet_name']
    IHL_SPREADSHEET_ID = config['ihl_spreadsheet_id']
    IHL_SHEET_NAME = config['ihl_sheet_name']
    logger.info("✅ Configuration loaded successfully")
    logger.info(f"📊 Allura Target Sheet: {SPREADSHEET_ID} - '{SHEET_NAME}'")
    logger.info(f"📊 IHL Target Sheet: {IHL_SPREADSHEET_ID} - '{IHL_SHEET_NAME}'")
    if os.path.exists('.env'):
        logger.info("📁 Using .env file for configuration (development mode)")
    else:
        logger.info("🌐 Using system environment variables (production mode)")
except Exception as e:
    logger.error(f"❌ Configuration error: {str(e)}")
    raise

# Initialize Google Sheets client
def get_sheets_client():
    """Initialize and return Google Sheets client"""
    try:
        service_account_info = get_service_account_info()
        credentials = Credentials.from_service_account_info(
            service_account_info, 
            scopes=SCOPES
        )
        client = gspread.authorize(credentials)
        logger.info("✅ Google Sheets client initialized successfully")
        return client
    except Exception as e:
        logger.error(f"❌ Failed to initialize Google Sheets client: {str(e)}")
        raise

def get_worksheet(data_type='allura'):
    """Get the appropriate worksheet based on data type"""
    try:
        client = get_sheets_client()
        
        if data_type.lower() == 'ihl':
            spreadsheet = client.open_by_key(IHL_SPREADSHEET_ID)
            worksheet = spreadsheet.worksheet(IHL_SHEET_NAME)
            logger.info(f"📊 Connected to IHL sheet: {worksheet.title}")
        else:  # default to allura
            spreadsheet = client.open_by_key(SPREADSHEET_ID)
            worksheet = spreadsheet.worksheet(SHEET_NAME)
            logger.info(f"📊 Connected to Allura sheet: {worksheet.title}")
        
        return client, spreadsheet, worksheet
    except Exception as e:
        logger.error(f"❌ Failed to get {data_type} worksheet: {str(e)}")
        raise

def column_number_to_letter(column_number):
    """Convert column number to Excel column letter (1=A, 27=AA, etc.)"""
    column_letter = ""
    while column_number > 0:
        column_number -= 1  # Make it 0-based
        column_letter = chr(column_number % 26 + ord('A')) + column_letter
        column_number //= 26
    return column_letter

def parse_csv_content(csv_content):
    """Parse CSV content into rows"""
    try:
        # Handle different line endings
        csv_content = csv_content.replace('\r\n', '\n').replace('\r', '\n')
        
        # Split into lines and filter empty ones
        lines = [line.strip() for line in csv_content.split('\n') if line.strip()]
        
        if len(lines) <= 1:
            raise ValueError("CSV must contain at least header and one data row")
        
        # Parse each line as CSV
        parsed_rows = []
        csv_reader = csv.reader(lines)
        
        for row in csv_reader:
            if row:  # Skip empty rows
                # Clean and strip each cell
                cleaned_row = [cell.strip() for cell in row]
                parsed_rows.append(cleaned_row)
        
        # Separate header and data
        header = parsed_rows[0] if parsed_rows else []
        data_rows = parsed_rows[1:] if len(parsed_rows) > 1 else []
        
        logger.info(f"📊 Parsed CSV: {len(data_rows)} data rows, {len(header)} columns")
        return header, data_rows
        
    except Exception as e:
        logger.error(f"❌ CSV parsing failed: {str(e)}")
        raise ValueError(f"Invalid CSV format: {str(e)}")

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'service': 'Google Sheets BOL Processor',
        'allura_config': {
            'spreadsheet_id': SPREADSHEET_ID,
            'sheet_name': SHEET_NAME
        },
        'ihl_config': {
            'spreadsheet_id': IHL_SPREADSHEET_ID,
            'sheet_name': IHL_SHEET_NAME
        },
        'timestamp': datetime.now().isoformat()
    })

def test_connection_generic(data_type='allura'):
    """Generic function to test Google Sheets connection"""
    try:
        client, spreadsheet, worksheet = get_worksheet(data_type)
        
        # Get basic sheet info
        sheet_info = {
            'spreadsheet_title': spreadsheet.title,
            'sheet_name': worksheet.title,
            'row_count': worksheet.row_count,
            'col_count': worksheet.col_count,
            'last_row_with_data': len(worksheet.get_all_values()),
            'data_type': data_type.upper()
        }
        
        logger.info(f"✅ {data_type.upper()} Google Sheets connection test successful")
        return jsonify({
            'success': True,
            'message': f'{data_type.upper()} Google Sheets connection successful',
            'sheet_info': sheet_info,
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"❌ {data_type.upper()} Google Sheets connection test failed: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e),
            'data_type': data_type.upper(),
            'timestamp': datetime.now().isoformat()
        }), 500

@app.route('/test', methods=['GET'])
def test_connection():
    """Test Allura Google Sheets connection (default)"""
    return test_connection_generic('allura')

@app.route('/test-ihl', methods=['GET'])
def test_connection_ihl():
    """Test IHL Google Sheets connection"""
    return test_connection_generic('ihl')

def upload_csv_generic(data_type='allura'):
    """Generic function to upload CSV data to Google Sheets"""
    try:
        # Get CSV content from request
        data = request.get_json()
        
        if not data or 'csvContent' not in data:
            return jsonify({
                'success': False,
                'error': 'No CSV content provided'
            }), 400
        
        csv_content = data['csvContent']
        
        if not csv_content or not csv_content.strip():
            return jsonify({
                'success': False,
                'error': 'Empty CSV content'
            }), 400
        
        logger.info(f"📥 Received {data_type.upper()} CSV upload request ({len(csv_content)} characters)")
        
        # Parse CSV content
        header, data_rows = parse_csv_content(csv_content)
        
        if not data_rows:
            return jsonify({
                'success': False,
                'error': 'No data rows to add'
            }), 400
        
        # Connect to appropriate Google Sheet
        client, spreadsheet, worksheet = get_worksheet(data_type)
        
        # Find next empty row
        all_values = worksheet.get_all_values()
        last_row = len(all_values)
        start_row = last_row + 1
        
        # Add data to sheet (skip header - assume it already exists)
        logger.info(f"📍 Adding {len(data_rows)} rows starting at row {start_row}")
        
        # Determine the correct column range based on actual data width
        # SHIFT DATA ONE COLUMN TO THE RIGHT - START AT COLUMN B INSTEAD OF A
        max_columns = max(len(row) for row in data_rows) if data_rows else 1
        start_column = "B"  # Changed from "A" to "B"
        end_column = column_number_to_letter(max_columns + 1)  # Add 1 to account for B start
        
        # Batch update for better performance with dynamic range
        cell_range = f"{start_column}{start_row}:{end_column}{start_row + len(data_rows) - 1}"
        logger.info(f"📊 Writing to range: {cell_range} (for {max_columns} columns, shifted to start at B)")
        
        worksheet.update(cell_range, data_rows)
        
        end_row = start_row + len(data_rows) - 1
        
        logger.info(f"✅ Successfully added {len(data_rows)} rows to {data_type.upper()} Google Sheets")
        
        return jsonify({
            'success': True,
            'message': f'Successfully added {len(data_rows)} rows to {data_type.upper()} Google Sheets',
            'rowsAdded': len(data_rows),
            'startRow': start_row,
            'endRow': end_row,
            'sheetName': worksheet.title,
            'spreadsheetId': spreadsheet.id,
            'dataType': data_type.upper(),
            'timestamp': datetime.now().isoformat()
        })
        
    except ValueError as ve:
        logger.error(f"❌ {data_type.upper()} validation error: {str(ve)}")
        return jsonify({
            'success': False,
            'error': str(ve),
            'dataType': data_type.upper(),
            'timestamp': datetime.now().isoformat()
        }), 400
        
    except Exception as e:
        logger.error(f"❌ {data_type.upper()} upload failed: {str(e)}")
        return jsonify({
            'success': False,
            'error': f'Upload failed: {str(e)}',
            'dataType': data_type.upper(),
            'timestamp': datetime.now().isoformat()
        }), 500

@app.route('/upload-csv', methods=['POST'])
def upload_csv():
    """Upload CSV data to Allura Google Sheets (default)"""
    return upload_csv_generic('allura')

@app.route('/upload-csv-ihl', methods=['POST'])
def upload_csv_ihl():
    """Upload CSV data to IHL Google Sheets"""
    return upload_csv_generic('ihl')

def get_sheet_info_generic(data_type='allura'):
    """Generic function to get information about the target sheet"""
    try:
        client, spreadsheet, worksheet = get_worksheet(data_type)
        
        # Get sheet data
        all_values = worksheet.get_all_values()
        header = all_values[0] if all_values else []
        data_rows = all_values[1:] if len(all_values) > 1 else []
        
        sheet_info = {
            'spreadsheet_title': spreadsheet.title,
            'spreadsheet_id': spreadsheet.id,
            'sheet_name': worksheet.title,
            'total_rows': len(all_values),
            'data_rows': len(data_rows),
            'columns': len(header),
            'header': header,
            'last_5_rows': data_rows[-5:] if len(data_rows) >= 5 else data_rows,
            'data_type': data_type.upper()
        }
        
        return jsonify({
            'success': True,
            'sheet_info': sheet_info,
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"❌ Failed to get {data_type.upper()} sheet info: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e),
            'data_type': data_type.upper(),
            'timestamp': datetime.now().isoformat()
        }), 500

@app.route('/sheet-info', methods=['GET'])
def get_sheet_info():
    """Get information about the Allura target sheet (default)"""
    return get_sheet_info_generic('allura')

@app.route('/sheet-info-ihl', methods=['GET'])
def get_sheet_info_ihl():
    """Get information about the IHL target sheet"""
    return get_sheet_info_generic('ihl')

def clear_test_data_generic(data_type='allura'):
    """Generic function to clear test data from the sheet (rows containing 'TEST')"""
    try:
        client, spreadsheet, worksheet = get_worksheet(data_type)
        
        # Get all data
        all_values = worksheet.get_all_values()
        
        # Find rows to delete (containing 'TEST')
        rows_to_delete = []
        for i, row in enumerate(all_values):
            if any('TEST' in str(cell) for cell in row):
                rows_to_delete.append(i + 1)  # 1-based indexing
        
        if not rows_to_delete:
            return jsonify({
                'success': True,
                'message': f'No test data found to clear in {data_type.upper()} sheet',
                'rows_deleted': 0,
                'data_type': data_type.upper()
            })
        
        # Delete rows (from bottom to top to avoid index shifting)
        for row_num in reversed(rows_to_delete):
            worksheet.delete_rows(row_num)
        
        logger.info(f"✅ Deleted {len(rows_to_delete)} test rows from {data_type.upper()} sheet")
        
        return jsonify({
            'success': True,
            'message': f'Cleared {len(rows_to_delete)} test rows from {data_type.upper()} sheet',
            'rows_deleted': len(rows_to_delete),
            'data_type': data_type.upper(),
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"❌ Failed to clear {data_type.upper()} test data: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e),
            'data_type': data_type.upper(),
            'timestamp': datetime.now().isoformat()
        }), 500

@app.route('/clear-test-data', methods=['POST'])
def clear_test_data():
    """Clear test data from the Allura sheet (default)"""
    return clear_test_data_generic('allura')

@app.route('/clear-test-data-ihl', methods=['POST'])
def clear_test_data_ihl():
    """Clear test data from the IHL sheet"""
    return clear_test_data_generic('ihl')

if __name__ == '__main__':
    # Load configuration for development
    try:
        config = get_config()
        logger.info(f"🚀 Starting Flask server on {config['flask_host']}:{config['flask_port']}")
        logger.info(f"📊 Debug mode: {config['flask_debug']}")
        
        app.run(
            debug=config['flask_debug'],
            host=config['flask_host'],
            port=config['flask_port']
        )
    except Exception as e:
        logger.error(f"❌ Failed to start server: {str(e)}")
        exit(1) 