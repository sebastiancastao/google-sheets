# Google Sheets Service

A Python Flask service that receives CSV data and adds it to Google Sheets using service account authentication. **Now supports dual sheet processing for both Allura and IHL data.**

**✨ Production Ready**: Works with both `.env` files (development) and system environment variables (production platforms like Render, Heroku, etc.)

## 📊 Supported Data Types

- **Allura Data**: Default processing for Allura combined data files
- **IHL Data**: Specialized processing for IHL combined data files with "IHL Test" tab

## 🤖 Smart Auto-Detection

The service now includes intelligent data type detection! When you upload CSV data to `/upload-csv`, it automatically:

- **Analyzes CSV content** for IHL-specific keywords like "sensual", "intimate", "lingerie", etc.
- **Scans header columns** for intimate apparel terminology  
- **Routes data automatically** to the correct Google Sheet (Allura or IHL)
- **Falls back to Allura** if detection is uncertain

**Detection Keywords**: `ihl`, `sensual`, `sensuelle`, `intimate`, `intimates`, `lingerie`, `bra`, `panty`, `panties`, `sleepwear`, `nightwear`, `hosiery`, `shapewear`, `bodysuit`

## 🚀 Quick Setup

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Set Up Environment Variables

1. Copy the content from `environment_variables.txt` to a new file called `.env`
2. Update the values in `.env` with your actual credentials

```bash
# Copy template to .env file
cp environment_variables.txt .env

# Edit .env with your actual values
# (Use your preferred text editor)
```

### 3. Configure Your `.env` File

The `.env` file should contain:

```env
# Google Service Account Configuration
GOOGLE_PROJECT_ID=your-project-id
GOOGLE_PRIVATE_KEY_ID=your-private-key-id
GOOGLE_PRIVATE_KEY="-----BEGIN PRIVATE KEY-----\nyour-private-key-here\n-----END PRIVATE KEY-----\n"
GOOGLE_CLIENT_EMAIL=your-service-account@your-project.iam.gserviceaccount.com
GOOGLE_CLIENT_ID=your-client-id

# Allura Google Sheets Configuration
SPREADSHEET_ID=your-allura-spreadsheet-id
SHEET_NAME=Allura Test

# IHL Google Sheets Configuration
IHL_SPREADSHEET_ID=your-ihl-spreadsheet-id
IHL_SHEET_NAME=IHL Test

# Flask Server Configuration
FLASK_HOST=0.0.0.0
FLASK_PORT=5550
FLASK_DEBUG=True

# Logging Configuration
LOG_LEVEL=INFO
```

### 4. Start the Service

```bash
# Using the startup script (recommended)
python start_google_sheets_service.py

# Or directly
python google_sheets_service.py
```

## 📊 API Endpoints

### General Endpoints
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/health` | Health check for both Allura and IHL sheets |

### Smart Upload Endpoint
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/upload-csv` | **🤖 Smart Upload** - Automatically detects data type (IHL/Allura) and routes to correct sheet |

### Allura Data Endpoints
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/test` | Test Allura Google Sheets connection |
| POST | `/upload-csv-allura` | Upload CSV data to Allura sheet (explicit) |
| GET | `/sheet-info` | Get Allura sheet information |
| POST | `/clear-test-data` | Clear test data from Allura sheet |

### IHL Data Endpoints
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/test-ihl` | Test IHL Google Sheets connection |
| POST | `/upload-csv-ihl` | Upload CSV data to IHL sheet (explicit) |
| GET | `/sheet-info-ihl` | Get IHL sheet information |
| POST | `/clear-test-data-ihl` | Clear test data from IHL sheet |

## 🔧 Configuration Options

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `GOOGLE_PROJECT_ID` | Google Cloud project ID | Required |
| `GOOGLE_PRIVATE_KEY_ID` | Service account private key ID | Required |
| `GOOGLE_PRIVATE_KEY` | Service account private key | Required |
| `GOOGLE_CLIENT_EMAIL` | Service account email | Required |
| `GOOGLE_CLIENT_ID` | Service account client ID | Required |
| `SPREADSHEET_ID` | Allura Google Sheets ID | Required |
| `SHEET_NAME` | Allura sheet name | Required |
| `IHL_SPREADSHEET_ID` | IHL Google Sheets ID | Required |
| `IHL_SHEET_NAME` | IHL sheet name (typically "IHL Test") | Required |
| `FLASK_HOST` | Flask server host | `0.0.0.0` |
| `FLASK_PORT` | Flask server port | `5550` |
| `FLASK_DEBUG` | Enable debug mode | `True` |
| `LOG_LEVEL` | Logging level | `INFO` |

## 🛡️ Security

- **Never commit your `.env` file** - it contains sensitive credentials
- The `.env` file is already in `.gitignore` 
- Keep your service account key secure
- Use least privilege principle for Google Sheets permissions

## 🔍 Testing

### Test Allura connection:
```bash
curl http://localhost:5550/test
```

### Test IHL connection:
```bash
curl http://localhost:5550/test-ihl
```

### Smart Upload (Automatic Detection):
```bash
# This will automatically detect if data is IHL or Allura and route accordingly
curl -X POST http://localhost:5550/upload-csv \
  -H "Content-Type: application/json" \
  -d '{"csvContent": "Name,Age,City\nJohn,30,NYC\nJane,25,LA"}'
```

### Upload CSV data to specific sheets:
```bash
# Explicit Allura upload
curl -X POST http://localhost:5550/upload-csv-allura \
  -H "Content-Type: application/json" \
  -d '{"csvContent": "Name,Age,City\nJohn,30,NYC\nJane,25,LA"}'

# Explicit IHL upload
curl -X POST http://localhost:5550/upload-csv-ihl \
  -H "Content-Type: application/json" \
  -d '{"csvContent": "Product,Category,Brand\nSensual Bra,Intimates,Brand"}'
```

### Get sheet information:
```bash
# Allura sheet info
curl http://localhost:5550/sheet-info

# IHL sheet info
curl http://localhost:5550/sheet-info-ihl
```

## 🐛 Troubleshooting

### Common Issues:

1. **"Missing environment variables"**
   - Make sure your `.env` file exists and contains all required variables
   - Check that variable names match exactly

2. **"Google Sheets connection failed"**
   - Verify your service account credentials
   - Ensure the service account has access to the target spreadsheet
   - Check that the spreadsheet ID and sheet name are correct

3. **"Port already in use"**
   - Change the `FLASK_PORT` in your `.env` file
   - Or stop any other services using port 5550

### Getting Help:

- Check the console output for detailed error messages
- Verify your Google Cloud service account setup
- Ensure the target spreadsheet is shared with your service account email

## 🌐 Production Deployment

For production deployment to cloud platforms like Render.com, see the detailed guide:

**📖 [Production Deployment Guide](./PRODUCTION_DEPLOY.md)**

Key points for production:
- No `.env` file needed - uses system environment variables
- Automatically detects cloud platform ports (PORT environment variable)
- Set `FLASK_DEBUG=False` for production
- Configure all environment variables in your hosting platform's dashboard

## 📝 Development

The service automatically loads environment variables from `.env` file on startup. Any changes to environment variables require a restart.

For development, you can set `FLASK_DEBUG=True` in your `.env` file to enable hot reloading. 