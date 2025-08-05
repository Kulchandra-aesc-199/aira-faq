# 🔐 Security Setup Guide

## API Key Configuration

### ⚠️ Important Security Notice
Never commit API keys or sensitive credentials to version control. This project uses Streamlit secrets for secure credential management.

## Setup Instructions

### 1. Create Streamlit Secrets File
```bash
# Create the .streamlit directory if it doesn't exist
mkdir -p .streamlit

# Copy the example template
cp .streamlit/secrets.toml.example .streamlit/secrets.toml
```

### 2. Add Your OpenAI API Key
Edit `.streamlit/secrets.toml` and replace the placeholder:

```toml
# OpenAI API Configuration
OPENAI_API_KEY = "sk-proj-your-actual-api-key-here"

# Optional configurations
# OPENAI_ORG_ID = "your_org_id_here"
# OPENAI_MODEL = "gpt-3.5-turbo"
```

### 3. Verify Security
- ✅ `.streamlit/secrets.toml` is in `.gitignore`
- ✅ API key is not in `.env` file
- ✅ No API keys in source code
- ✅ Secrets file is not committed to git

## How It Works

### Priority Order
The application looks for API keys in this order:
1. **Streamlit Secrets** (most secure) - `st.secrets['OPENAI_API_KEY']`
2. **Environment Variables** (fallback) - `os.getenv('OPENAI_API_KEY')`

### Local Development
For local development, you can either:
- Use Streamlit secrets (recommended)
- Set environment variable: `export OPENAI_API_KEY="your-key"`

### Production Deployment
For production (Streamlit Cloud, etc.):
- Add secrets through the platform's secret management
- Never include API keys in deployed code

## Troubleshooting

### AI Features Not Working?
1. Check if API key is properly set in `.streamlit/secrets.toml`
2. Verify the API key is valid and has credits
3. Check the AI Status indicator in the sidebar
4. Look for error messages in the Streamlit interface

### File Not Found Error?
If you get a secrets file error:
```bash
# Make sure the secrets file exists
ls -la .streamlit/secrets.toml

# If not, copy from template
cp .streamlit/secrets.toml.example .streamlit/secrets.toml
```

## Security Best Practices

### ✅ Do:
- Use Streamlit secrets for API keys
- Keep `.streamlit/secrets.toml` in `.gitignore`
- Regularly rotate API keys
- Use environment-specific configurations

### ❌ Don't:
- Commit API keys to version control
- Share secrets files
- Hardcode credentials in source code
- Use production keys in development

## Additional Security

### Environment Variables (Alternative)
If you prefer environment variables:
```bash
# Add to your shell profile (.bashrc, .zshrc, etc.)
export OPENAI_API_KEY="your-api-key-here"

# Or create a local .env file (not committed)
echo "OPENAI_API_KEY=your-api-key-here" > .env
```

### API Key Management
- Get your API key from: https://platform.openai.com/api-keys
- Monitor usage at: https://platform.openai.com/usage
- Set usage limits to prevent unexpected charges
- Use separate keys for development and production

## Support

If you encounter security-related issues:
1. Check this guide first
2. Verify your API key setup
3. Test with a simple API call
4. Check Streamlit logs for errors

Remember: Security is paramount when handling API keys and user data!
