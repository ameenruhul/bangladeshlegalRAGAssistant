# 🏛️ Bangladesh Legal RAG Assistant

An AI-powered legal research and advisory system for Bangladesh law, built with Streamlit and Google Gemini AI.

## ✨ Features

- 🤖 **AI-Powered Legal Analysis** - Get comprehensive legal advice using Google Gemini AI
- 📚 **2049+ Legal Documents** - Searchable database of Bangladesh laws and acts
- 🔍 **Smart Document Retrieval** - RAG (Retrieval-Augmented Generation) system for accurate legal citations
- 🎯 **Multiple AI Modes** - Lawyer, Research, Simple, and Argument modes for different use cases
- 🇧🇩 **Bengali Language Support** - Full support for Bengali legal terminology
- 📊 **Interactive Dashboard** - Statistics and insights about the legal database
- 💬 **Chat Interface** - Natural conversation with legal AI assistant

## 🚀 Quick Start

### Prerequisites
- Python 3.10+
- Google Gemini API key ([Get one here](https://makersuite.google.com/app/apikey))

### Installation

1. **Clone the repository:**
   ```bash
   git clone https://github.com/yourusername/bangladesh-legal-rag.git
   cd bangladesh-legal-rag
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up environment variables:**
   ```bash
   cp .env.example .env
   # Edit .env and add your Google Gemini API key
   ```

4. **Run the setup:**
   ```bash
   python setup.py
   ```

5. **Start the application:**
   ```bash
   streamlit run app.py
   ```

6. **Open your browser** and go to `http://localhost:8501`

## 🐳 Docker Deployment

### Using Docker Compose (Recommended)

1. **Set your API key:**
   ```bash
   export GOOGLE_API_KEY="your_gemini_api_key_here"
   ```

2. **Run with Docker Compose:**
   ```bash
   docker-compose up -d
   ```

3. **Access the application** at `http://localhost:8501`

### Using Docker directly

```bash
# Build the image
docker build -t bangladesh-legal-rag .

# Run the container
docker run -p 8501:8501 -e GOOGLE_API_KEY="your_api_key" bangladesh-legal-rag
```

## 📁 Project Structure

```
bangladesh-legal-rag/
├── app.py                 # Main Streamlit application
├── setup.py              # Setup and installation script
├── requirements.txt       # Python dependencies
├── .env                  # Environment variables (create from .env.example)
├── Dockerfile            # Docker configuration
├── docker-compose.yml    # Docker Compose configuration
├── DEPLOYMENT_GUIDE.md   # Comprehensive deployment guide
├── components/           # UI components
│   ├── __init__.py
│   └── ui_components.py
├── utils/               # Core utilities
│   ├── __init__.py
│   ├── data_processor.py # Legal data processing
│   └── rag_system.py    # RAG system implementation
├── data/               # Legal database (CSV files)
├── vectorstore/        # Vector embeddings storage
├── logs/              # Application logs
└── assets/            # Static assets
```

## 🎯 AI Modes

### 🏛️ Lawyer Mode
- Comprehensive legal analysis
- Formal legal language
- Specific act and section citations
- Legal strategies and implications

### 🔬 Research Mode
- Extensive legal research
- Historical context and amendments
- Cross-references and related acts
- Legislative intent analysis

### 💡 Simple Mode
- Easy-to-understand explanations
- Non-technical language
- Practical examples
- Citizen-friendly guidance

### ⚖️ Argument Mode
- Legal arguments for both sides
- Evidence and precedent suggestions
- Strengths and weaknesses analysis
- Court strategy insights

## 📊 Database

The system includes a comprehensive database of Bangladesh legal documents:
- **2049+ Acts and Laws**
- **Searchable by year, status, and content**
- **Bengali and English language support**
- **Regular updates and amendments**

## 🔧 Configuration

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `GOOGLE_API_KEY` | Google Gemini API key | Required |
| `VECTOR_STORE_PATH` | Path to vector store | `./vectorstore` |
| `CHUNK_SIZE` | Document chunk size | `1000` |
| `CHUNK_OVERLAP` | Chunk overlap size | `200` |
| `TOP_K_RESULTS` | Number of search results | `5` |
| `LOG_LEVEL` | Logging level | `INFO` |
| `DEBUG` | Debug mode | `False` |

## 🚀 Deployment Options

1. **Streamlit Community Cloud** (Free, recommended for testing)
2. **Docker + Cloud Run/AWS Fargate** (Production ready)
3. **VPS/Server deployment** (Full control)
4. **Heroku** (Easy deployment)

See [`DEPLOYMENT_GUIDE.md`](DEPLOYMENT_GUIDE.md) for detailed deployment instructions.

## 🔒 Security

- ✅ Environment variable protection for API keys
- ✅ Input validation and sanitization
- ✅ Rate limiting capabilities
- ✅ HTTPS support in production deployments
- ✅ Docker security best practices

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🆘 Support

If you encounter any issues:

1. Check the [Deployment Guide](DEPLOYMENT_GUIDE.md)
2. Review the application logs in the `logs/` directory
3. Ensure your Google Gemini API key is valid and has sufficient quota
4. Verify all dependencies are installed correctly

## 🙏 Acknowledgments

- **Google Gemini AI** for powerful language model capabilities
- **Streamlit** for the amazing web framework
- **FAISS** for efficient vector similarity search
- **Sentence Transformers** for document embeddings
- **Bangladesh Government** for making legal documents accessible

---

**Made with ❤️ for the Bangladesh legal community**

🌟 **Star this repository if you find it helpful!**