# Google Sheets Service

A Python Flask service that receives CSV data and adds it to Google Sheets using service account authentication.

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

# Google Sheets Configuration
SPREADSHEET_ID=your-spreadsheet-id
SHEET_NAME=your-sheet-name

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

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/health` | Health check |
| GET | `/test` | Test Google Sheets connection |
| POST | `/upload-csv` | Upload CSV data to Google Sheets |
| GET | `/sheet-info` | Get sheet information |

## 🔧 Configuration Options

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `GOOGLE_PROJECT_ID` | Google Cloud project ID | Required |
| `GOOGLE_PRIVATE_KEY_ID` | Service account private key ID | Required |
| `GOOGLE_PRIVATE_KEY` | Service account private key | Required |
| `GOOGLE_CLIENT_EMAIL` | Service account email | Required |
| `GOOGLE_CLIENT_ID` | Service account client ID | Required |
| `SPREADSHEET_ID` | Target Google Sheets ID | Required |
| `SHEET_NAME` | Target sheet name | Required |
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

### Test the connection:
```bash
curl http://localhost:5550/test
```

### Upload CSV data:
```bash
curl -X POST http://localhost:5550/upload-csv \
  -H "Content-Type: application/json" \
  -d '{"csvContent": "Name,Age,City\nJohn,30,NYC\nJane,25,LA"}'
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

## 📝 Development

The service automatically loads environment variables from `.env` file on startup. Any changes to environment variables require a restart.

For development, you can set `FLASK_DEBUG=True` in your `.env` file to enable hot reloading. 