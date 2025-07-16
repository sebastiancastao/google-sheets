# Production Deployment Guide

## 🚀 Deploying to Render.com

### 1. Set Environment Variables in Render Dashboard

Since `.env` files cannot be pushed to production (and shouldn't be for security), you need to set environment variables in your Render dashboard.

#### Steps:

1. Go to your Render service dashboard
2. Navigate to **Environment** tab
3. Add the following environment variables:

| Variable Name | Value | Notes |
|---------------|-------|-------|
| `GOOGLE_PROJECT_ID` | `upheld-dragon-464217-e8` | Your Google Cloud project ID |
| `GOOGLE_PRIVATE_KEY_ID` | `76dcf136614e5266b1e1f4031f79cd60b1a733b4` | Service account private key ID |
| `GOOGLE_PRIVATE_KEY` | `-----BEGIN PRIVATE KEY-----\nMIIEvgIBADANBgkqhkiG9w0BAQEFAASCBKgwggSkAgEAAoIBAQCr9CIQOeD7s7oR\n9NPhalbVUNs0hqOloTtd8YbpGoatGDBRXNLUANvI0goKaxeJCoxeCAJKGsqW6n8u\nuZB3vVPn0igSPgtM//XLYg878ZhDieG39Fpt/A/x185zK1EaQJ9IaIuNPcsWDqdm\nsispQR3p77661bVXvi1a8tvpIwuLaNoQpMu6cEiGk0VswegnfqOkGDmNV8rtr8Uy\nzxi41SstbJiXIQraCyz37BWBwB2VIEb8QoBiSQpB5tNTlhjJ7GqY6dF8yP1xhJ7V\nS1qwVmuM7CSik0KZdllTiXA6oBcYWFtGExH8txXpsSvR35t39MAbubSdUKPiTpNK\nIy9zXmMJAgMBAAECggEAAc4Izv6Kht3Mr8xP7oNjGK9V86vPmykRclObCMaRYA77\nT9lPca/2Hpocxp334+V3UnPXUU+NbY7VyafjNSyIrUvahZF+5R6hJfK4KfcH0/qm\nIrwG+HVPNgi/txv+6I2B1nzZbSC3SVqbRXPMiezv61ELwZKFah+6AmS+6+glIoAR\ncCrjNTB5sC2uqBkA3JiElsCug8L2NZ/hWXpWOKOGJnk7IU5m6vwH9GnaclW/jG6G\nF9wk+pbYA4OEIOE8q9QhXpyOkaxNu4eRVS15pmUqM0uq3ll88LkeIX4n5ysYb5Ow\nZCdBd92mNI8B8bsJSj2uZbyd7ABWBZflml7yCvFTMQKBgQDm60GtjI1xVnYCRGMk\niirS74nSnKIfuG0wMbL0Lky0YgcnkYVbCYBaNNmpT03qp1mfapbq/C312vgruyY2\n7oRsBRIsWKMty1lIS4kNnjjPVOmrqe390pAiLNnq3JTq4Jk0xR3+AUwBQdnB51Ae\nfT6r+HG3p46alaV2DtgTwdEWmQKBgQC+oVXEOjE52KiDBMTv9TO9n9jf0g/J+OPg\nd1dV0KP9SPOdY2F0CDMEGArkVbqUvXYSj9xNt6zJ7g/dFfOnlujT6+6m3rGvhO9s\nxsWTOYpimFr8Vm/ZSJNe+kq0R0vAFmRO/QSp3v9QT1/DVQ1dJkPGG421jeAsNz6+\nI1FH7eQl8QKBgQDcq0ykMICqIlm7aOblcDPkR4yJe61iarfNKnE871HVvyffJC0w\nBjBmA8NNDMAE0c/Pi+iUvlCddZdbEwk9zUk2gNIRFtM5W+4CLEzYeq8HUrnKliUc\nPjAGuJ221vxoSCGgUA6NQWgEe41Aw2/I8x8E7/Kb8r9P8lmgLCdJGhpZYQKBgGjL\nEfXkM4lkNAaKSaTLu5zDUZqAxJM4EjUkBcuz/WJQhzN/HWSG2Vynxt0Mz5vSpyS/\nFtFWZlM/XlMgLSh0yhstuKzdAPrG7kNy5cvwNsXKkUHkVmow/mqY1xZRly/KX2wY\npUaowtuoNrGPgOAzF9DA9t7WVmSYHhKyIY2UFfZRAoGBAJzQ2Q8vnyfgrHoeK32H\nDchF37Wy28wASEdipcsnmbNkNah7kPpYqgxDNugGytUcfI2HmHQb/BkhFguxvTcw\n+dRGfZVdHNEoXmvlKhvbs87NMRHxyuN7dM0q5IuPj5VWKw4nFLQFLlJep7wp8x3b\nwD1wLfgfpJnCuBJ2LAs9kSXv\n-----END PRIVATE KEY-----\n` | Full private key with newlines |
| `GOOGLE_CLIENT_EMAIL` | `midas-371@upheld-dragon-464217-e8.iam.gserviceaccount.com` | Service account email |
| `GOOGLE_CLIENT_ID` | `108604986820777256452` | Service account client ID |
| `SPREADSHEET_ID` | `1NMrh29v0eOJLNBHGdy2T6NLSnc3zalg2Wj_O0ZSJ97g` | Target spreadsheet ID |
| `SHEET_NAME` | `Allura Test` | Target sheet name |
| `FLASK_HOST` | `0.0.0.0` | Server host (leave as default) |
| `FLASK_PORT` | `5550` | Server port (or use PORT if Render provides it) |
| `FLASK_DEBUG` | `False` | Set to False for production |
| `LOG_LEVEL` | `INFO` | Logging level |

### 2. Important Notes for Render

#### Port Configuration
- Render may provide a `PORT` environment variable
- If so, update your `FLASK_PORT` to use that value
- Or modify the code to check for `PORT` first, then fall back to `FLASK_PORT`

#### Private Key Formatting
- Make sure the `GOOGLE_PRIVATE_KEY` includes the literal `\n` characters for line breaks
- In Render's environment variable editor, it should look exactly like:
  ```
  -----BEGIN PRIVATE KEY-----\nMIIEvgIBADANBgkqhkiG9w0BAQEFAASCBKgwggSkAgEAAoIBAQCr9CIQOeD7s7oR\n...rest of key...\n-----END PRIVATE KEY-----\n
  ```

### 3. Deploy Commands

Make sure your Render service is configured with:

- **Build Command**: `pip install -r requirements.txt`
- **Start Command**: `python start_google_sheets_service.py`

### 4. Verification

After deployment, your service logs should show:
```
🚀 Starting Google Sheets Service for BOL Processing
🌐 No .env file found, using system environment variables (production mode)
🔍 Checking environment variables...
✅ Environment variables loaded successfully
✅ Configuration loaded successfully
🌐 Using system environment variables (production mode)
📊 Target Sheet: 1NMrh29v0eOJLNBHGdy2T6NLSnc3zalg2Wj_O0ZSJ97g - 'Allura Test'
🔄 Starting Google Sheets service...
```

### 5. Testing Production Deployment

Once deployed, test your endpoints:

- Health check: `https://your-render-url.onrender.com/health`
- Connection test: `https://your-render-url.onrender.com/test`

### 6. Security Best Practices

✅ **DO:**
- Set environment variables in Render dashboard
- Use `FLASK_DEBUG=False` in production
- Keep your service account key secure
- Regularly rotate your service account keys

❌ **DON'T:**
- Push `.env` files to your repository
- Use debug mode in production
- Share your private keys in chat or email
- Commit credentials to version control

## 🐛 Troubleshooting

### "Missing environment variables" Error
1. Check that all variables are set in Render dashboard
2. Verify variable names match exactly (case-sensitive)
3. Check for extra spaces in variable values

### "Google Sheets connection failed" Error
1. Verify your service account has access to the spreadsheet
2. Check that the spreadsheet ID and sheet name are correct
3. Ensure the private key format is correct with `\n` for line breaks

### Port Issues
- Render may assign a different port
- Check if Render provides a `PORT` environment variable
- Update your configuration accordingly 