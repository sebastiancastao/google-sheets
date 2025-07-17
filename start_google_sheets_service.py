#!/usr/bin/env python3
"""
Google Sheets Service Startup Script
Simple script to start the Google Sheets service for BOL processing
Works with both .env files (development) and system environment variables (production)
"""

import os
import sys
import subprocess
from dotenv import load_dotenv

def check_dependencies():
    """Check if required Python packages are installed"""
    required_packages = [
        'flask',
        'flask-cors', 
        'gspread',
        'google-auth',
        'google-auth-oauthlib',
        'google-api-python-client',
        'requests',
        'python-dotenv'
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package.replace('-', '_'))
        except ImportError:
            missing_packages.append(package)
    
    return missing_packages

def install_dependencies(packages):
    """Install missing Python packages"""
    print(f"📦 Installing missing packages: {', '.join(packages)}")
    
    try:
        subprocess.check_call([
            sys.executable, '-m', 'pip', 'install', '--user'
        ] + packages)
        print("✅ Dependencies installed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install dependencies: {e}")
        return False

def check_environment_variables():
    """Check if required environment variables are set"""
    # Try to load .env file if it exists (for development)
    if os.path.exists('.env'):
        print("📁 Found .env file, loading environment variables...")
        load_dotenv()
    else:
        print("🌐 No .env file found, using system environment variables (production mode)")
    
    required_vars = [
        'GOOGLE_PROJECT_ID',
        'GOOGLE_PRIVATE_KEY_ID',
        'GOOGLE_PRIVATE_KEY',
        'GOOGLE_CLIENT_EMAIL',
        'GOOGLE_CLIENT_ID',
        'SPREADSHEET_ID',
        'SHEET_NAME',
        'IHL_SPREADSHEET_ID',
        'IHL_SHEET_NAME'
    ]
    
    missing_vars = []
    for var in required_vars:
        if not os.getenv(var):
            missing_vars.append(var)
    
    return missing_vars

def main():
    print("🚀 Starting Google Sheets Service for BOL Processing")
    print("=" * 60)
    
    # Check if service file exists
    service_file = 'google_sheets_service.py'
    if not os.path.exists(service_file):
        print(f"❌ Service file '{service_file}' not found!")
        print("💡 Make sure you're running this from the correct directory")
        return False

    # Check environment variables (works with or without .env file)
    print("🔍 Checking environment variables...")
    missing_vars = check_environment_variables()
    if missing_vars:
        print(f"❌ Missing environment variables: {', '.join(missing_vars)}")
        if os.path.exists('.env'):
            print("💡 Please check your .env file and ensure all required variables are set.")
            print("   See environment_variables.txt for the template.")
        else:
            print("💡 For production deployment, set these environment variables in your hosting platform:")
            for var in missing_vars:
                print(f"   - {var}")
            print("\n📖 Refer to your hosting platform's documentation for setting environment variables.")
        return False
    
    print("✅ Environment variables loaded successfully")

    # Check dependencies
    print("🔍 Checking dependencies...")
    
    # Load configuration to display info (try .env first, then system env)
    if os.path.exists('.env'):
        load_dotenv()
    
    # Allura configuration
    spreadsheet_id = os.getenv('SPREADSHEET_ID')
    sheet_name = os.getenv('SHEET_NAME')
    
    # IHL configuration
    ihl_spreadsheet_id = os.getenv('IHL_SPREADSHEET_ID')
    ihl_sheet_name = os.getenv('IHL_SHEET_NAME')
    
    flask_host = os.getenv('FLASK_HOST', '0.0.0.0')
    # Use PORT from cloud platforms (like Render) if available, otherwise fall back to FLASK_PORT
    flask_port = os.getenv('PORT') or os.getenv('FLASK_PORT', '5550')
    
    # Start the service
    print("\n🔄 Starting Google Sheets service...")
    print(f"🌐 Service will be available at: http://{flask_host}:{flask_port}")
    print(f"📊 Allura Target Sheet: {spreadsheet_id} - '{sheet_name}'")
    print(f"📊 IHL Target Sheet: {ihl_spreadsheet_id} - '{ihl_sheet_name}'")
    print("\n🔧 Available endpoints:")
    print(f"   GET  http://{flask_host}:{flask_port}/health - Health check (both sheets)")
    print(f"   GET  http://{flask_host}:{flask_port}/test - Test Allura connection")
    print(f"   GET  http://{flask_host}:{flask_port}/test-ihl - Test IHL connection")
    print(f"   POST http://{flask_host}:{flask_port}/upload-csv - Upload CSV to Allura sheet")
    print(f"   POST http://{flask_host}:{flask_port}/upload-csv-ihl - Upload CSV to IHL sheet")
    print(f"   GET  http://{flask_host}:{flask_port}/sheet-info - Get Allura sheet info")
    print(f"   GET  http://{flask_host}:{flask_port}/sheet-info-ihl - Get IHL sheet info")
    print(f"   POST http://{flask_host}:{flask_port}/clear-test-data - Clear Allura test data")
    print(f"   POST http://{flask_host}:{flask_port}/clear-test-data-ihl - Clear IHL test data")
    print("\n💡 Test from browser console:")
    print("   await bolProcessor.testPythonService()")
    print("\n🛑 Press Ctrl+C to stop the service")
    print("=" * 60)
    
    try:
        # Import and run the service
        from google_sheets_service import app, get_config
        config = get_config()
        app.run(
            debug=config['flask_debug'],
            host=config['flask_host'],
            port=config['flask_port']
        )
    except ImportError as e:
        print(f"❌ Failed to import service: {e}")
        print("💡 Make sure google_sheets_service.py is in the current directory")
        return False
    except ValueError as e:
        print(f"❌ Configuration error: {e}")
        print("💡 Please check your environment variables configuration")
        return False
    except KeyboardInterrupt:
        print("\n\n🛑 Service stopped by user")
        return True
    except Exception as e:
        print(f"❌ Service failed to start: {e}")
        return False

if __name__ == '__main__':
    success = main()
    if not success:
        sys.exit(1) 