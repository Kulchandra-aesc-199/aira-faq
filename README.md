# 🤖 AIRA FAQ Manager - Simplified

A focused, AI-powered FAQ management system. Create and edit FAQs with AI enhancement.

## ✨ Core Features

- 📖 **View FAQs** - Browse and search your FAQ collection
- ➕ **Create FAQ** - Manual input or AI-assisted creation
- ✏️ **Edit FAQ** - Modify existing entries with AI enhancement
- 🤖 **AI Enhancement** - Improve questions and answers with AI
- 💡 **AI Suggestions** - Generate FAQs from topics or questions

## 🏗️ Project Structure

```
aira-faq/
├── app.py                 # Main application
├── models.py              # FAQ data management
├── ai_helper.py           # OpenAI integration
├── pages/
│   └── add_faq.py         # Create FAQ page
├── faq.json              # FAQ data storage
├── .env                  # Environment variables
├── requirements.txt      # Dependencies
└── venv/                 # Virtual environment
```

## 🚀 Quick Start

### 1. Setup Environment

```bash
# Create and activate virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Configure API Key (Optional)

```bash
# Copy environment template
cp .env.example .env

# Edit .env file and add your OpenAI API key
OPENAI_API_KEY=sk-your_actual_api_key_here
```

### 3. Run the Application

```bash
streamlit run app.py
```

The app will be available at `http://localhost:8501`

## 📋 Usage Guide

### Adding FAQs

The enhanced "Add New FAQ" page offers three input modes:

1. **📝 Manual Input**
   - Traditional form-based input
   - Real-time character counting
   - Optional AI enhancement

2. **🤖 AI-Assisted**
   - Generate FAQs from topics
   - Auto-generate answers for questions
   - Smart suggestions based on existing content

3. **📋 Template-Based**
   - Pre-built templates for common FAQ types
   - How-to guides, troubleshooting, features, policies
   - Customizable templates

### Workflow Steps

1. **📝 Input** - Choose your input method and create content
2. **👀 Preview** - Review and validate your FAQ
3. **✅ Complete** - Save and choose next action

### Search & Filter

- 🔍 **Text Search** - Search across questions and answers
- 📏 **Length Filters** - Filter by question/answer length
- 🔤 **Sorting Options** - Sort by length, alphabetical, or default
- 📄 **Pagination** - Navigate large FAQ collections
- 👁️ **View Modes** - Questions-only or full FAQ display

## 🔧 Configuration

### Environment Variables

| Variable | Description | Required |
|----------|-------------|----------|
| `OPENAI_API_KEY` | OpenAI API key for AI features | Optional |
| `OPENAI_MODEL` | Model to use (default: gpt-3.5-turbo) | Optional |

### File Structure

- `faq.json` - Main FAQ data storage
- `faq_backup_*.json` - Automatic backups created on changes
- `.streamlit/` - Streamlit configuration (auto-created)

## 🛠️ Development

### Code Organization

- **models.py** - Data models and business logic
- **ai_helper.py** - AI integration and OpenAI API calls
- **ui_components.py** - Reusable Streamlit components
- **pages/** - Individual page modules for better maintainability

### Key Classes

- `FAQ` - Individual FAQ data model with validation
- `FAQManager` - FAQ collection management and persistence
- `AIHelper` - OpenAI integration and AI-powered features

### Adding New Pages

1. Create a new file in `pages/` directory
2. Implement a `render_*` function
3. Add the page to the navigation in `app.py`
4. Update the routing logic in `main()`

## 🔒 Security

- API keys stored in environment variables
- `.env` file excluded from version control
- Automatic backup creation before data changes
- Input validation and sanitization

## 📊 Data Management

### Backup System
- Automatic backups created before any changes
- Timestamped backup files
- Manual export functionality

### Data Format
```json
[
  {
    "question": "Your question here?",
    "answer": "Your detailed answer here."
  }
]
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## 📄 License

This project is open source and available under the MIT License.

## 🆘 Support

For issues, questions, or contributions:
- Check the FAQ section in the app
- Review the code documentation
- Create an issue in the repository

---

**Built with ❤️ using Streamlit and OpenAI**
