import os
import sys
import subprocess
from pathlib import Path

def create_directory_structure():
    """Create necessary directories"""
    directories = [
        "data",
        "vectorstore", 
        "components",
        "utils",
        "assets",
        "logs"
    ]
    
    for directory in directories:
        Path(directory).mkdir(exist_ok=True)
        print(f"[OK] Created directory: {directory}")

def install_requirements():
    """Install required packages"""
    requirements = [
        "streamlit==1.29.0",
        "google-generativeai==0.3.2",
        "langchain==0.1.0",
        "faiss-cpu==1.7.4",
        "sentence-transformers==2.7.0",
        "huggingface-hub>=0.30.0,<1.0",
        "transformers==4.36.2",
        "pandas==2.1.4",
        "numpy==1.24.3",
        "python-dotenv==1.0.0",
        "plotly==5.17.0",
        "wordcloud==1.9.2",
        "beautifulsoup4==4.12.2",
        "python-dateutil==2.8.2",
        "matplotlib==3.7.0",
        "regex==2023.10.3",
        "pytz==2023.3"
    ]
    
    print("[INFO] Installing required packages...")
    for package in requirements:
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", package])
            print(f"[OK] Installed: {package}")
        except subprocess.CalledProcessError:
            print(f"[ERROR] Failed to install: {package}")

def create_env_file():
    """Create .env file template"""
    env_content = """# Google Gemini API Configuration
GOOGLE_API_KEY=your_gemini_api_key_here

# Application Configuration
APP_NAME=Bangladesh Legal Assistant
APP_VERSION=1.0.0
DEBUG=True

# Vector Store Configuration
VECTOR_STORE_PATH=./vectorstore
CHUNK_SIZE=1000
CHUNK_OVERLAP=200
TOP_K_RESULTS=5

# Logging
LOG_LEVEL=INFO
LOG_FILE=./logs/app.log
"""
    
    with open('.env', 'w') as f:
        f.write(env_content)
    
    print("[OK] Created .env file template")
    print("[WARNING] Please add your Google Gemini API key to the .env file")

def create_init_files():
    """Create __init__.py files"""
    init_dirs = ["components", "utils"]
    
    for directory in init_dirs:
        init_file = Path(directory) / "__init__.py"
        init_file.touch()
        print(f"[OK] Created: {init_file}")

def main():
    """Main setup function"""
    print("[SETUP] Setting up Bangladesh Legal RAG Assistant")
    print("=" * 50)
    
    create_directory_structure()
    create_init_files()
    install_requirements()
    create_env_file()
    
    print("\n" + "=" * 50)
    print("[OK] Setup completed successfully!")
    print("\n[NEXT STEPS]:")
    print("1. Add your Google Gemini API key to .env file")
    print("2. Place your CSV file in the data/ directory")
    print("3. Run: streamlit run app.py")
    print("\n[INFO] Get Gemini API key: https://makersuite.google.com/app/apikey")

if __name__ == "__main__":
    main()

# ---

# run_app.py
"""
Script to run the Legal RAG Assistant with proper setup
"""

import os
import sys
import subprocess
from pathlib import Path
from dotenv import load_dotenv

def check_requirements():
    """Check if all requirements are installed"""
    required_packages = [
        'streamlit',
        'google-generativeai', 
        'sentence_transformers',
        'faiss',
        'pandas',
        'numpy',
        'python-dotenv',
        'plotly'
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package.replace('-', '_'))
        except ImportError:
            missing_packages.append(package)
    
    if missing_packages:
        print(f"❌ Missing packages: {', '.join(missing_packages)}")
        print("Run: python setup.py")
        return False
    
    return True

def check_env_file():
    """Check if .env file exists and has API key"""
    if not Path('.env').exists():
        print("❌ .env file not found")
        print("Run: python setup.py")
        return False
    
    load_dotenv()
    api_key = os.getenv('GOOGLE_API_KEY')
    
    if not api_key or api_key == 'your_gemini_api_key_here':
        print("❌ Google API key not configured in .env file")
        print("Please add your Gemini API key to .env file")
        return False
    
    return True

def check_data_files():
    """Check if data files exist"""
    data_dir = Path('data')
    
    if not data_dir.exists():
        print("❌ data/ directory not found")
        return False
    
    csv_files = list(data_dir.glob('*.csv'))
    
    if not csv_files:
        print("❌ No CSV files found in data/ directory")
        print("Please place your legal database CSV file in data/")
        return False
    
    print(f"✅ Found {len(csv_files)} CSV file(s) in data/")
    return True

def run_streamlit():
    """Run the Streamlit application"""
    try:
        subprocess.run([sys.executable, "-m", "streamlit", "run", "app.py"], check=True)
    except subprocess.CalledProcessError:
        print("❌ Failed to run Streamlit app")
        return False
    except KeyboardInterrupt:
        print("\n👋 Application stopped by user")
    
    return True

def main():
    """Main run function"""
    print("[START] Starting Bangladesh Legal RAG Assistant")
    print("=" * 50)
    
    # Check requirements
    if not check_requirements():
        return
    
    # Check configuration
    if not check_env_file():
        return
    
    # Check data files
    if not check_data_files():
        return
    
    print("✅ All checks passed!")
    print("🌐 Starting Streamlit server...")
    print("📱 The app will open in your default browser")
    print("⏹️  Press Ctrl+C to stop the server")
    print("-" * 50)
    
    # Run the app
    run_streamlit()

if __name__ == "__main__":
    main()

# ---

# build_vectorstore.py
"""
Script to pre-build vector store for faster startup
"""

import os
import json
from pathlib import Path
from dotenv import load_dotenv
from utils.data_processor import LegalDataProcessor
from utils.rag_system import LegalRAGSystem

def main():
    """Build vector store from CSV data"""
    print("🏗️  Building Vector Store for Legal RAG Assistant")
    print("=" * 60)
    
    # Load environment
    load_dotenv()
    
    # Check API key
    api_key = os.getenv('GOOGLE_API_KEY')
    if not api_key or api_key == 'your_gemini_api_key_here':
        print("❌ Please configure your Google API key in .env file")
        return
    
    # Find CSV files
    data_dir = Path('data')
    csv_files = list(data_dir.glob('*.csv'))
    
    if not csv_files:
        print("❌ No CSV files found in data/ directory")
        return
    
    csv_file = csv_files[0]
    print(f"📄 Using CSV file: {csv_file}")
    
    try:
        # Initialize data processor
        print("📊 Loading and processing legal data...")
        processor = LegalDataProcessor(str(csv_file))
        df = processor.load_data()
        
        # Process documents
        print("🔄 Creating document chunks...")
        documents = processor.process_all_acts()
        
        # Get statistics
        stats = processor.get_act_statistics()
        print(f"✅ Processed {stats['total_acts']} acts into {len(documents)} searchable chunks")
        
        # Initialize RAG system
        print("🤖 Initializing RAG system...")
        rag_system = LegalRAGSystem(
            google_api_key=api_key,
            vector_store_path=os.getenv('VECTOR_STORE_PATH', './vectorstore')
        )
        
        # Build vector store
        print("🔍 Building vector store (this may take a few minutes)...")
        rag_system.build_vector_store(documents)
        
        print("✅ Vector store built successfully!")
        print(f"📁 Saved to: {rag_system.vector_store_path}")
        
        # Test the system
        print("\n🧪 Testing the system...")
        test_query = "What is the punishment for theft?"
        response, sources = rag_system.get_chat_response(test_query, top_k=3)
        
        print(f"Test Query: {test_query}")
        print(f"Found {len(sources)} relevant sources")
        print(f"Response length: {len(response)} characters")
        
        print("\n🎉 Vector store build completed successfully!")
        print("You can now run the app with: streamlit run app.py")
        
    except Exception as e:
        print(f"❌ Error building vector store: {str(e)}")
        raise

if __name__ == "__main__":
    main()

# ---

# test_system.py
"""
Script to test the Legal RAG system components
"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv

def test_imports():
    """Test if all required modules can be imported"""
    print("🧪 Testing imports...")
    
    try:
        import streamlit
        print("✅ Streamlit")
        
        import google.generativeai
        print("✅ Google Generative AI")
        
        import sentence_transformers
        print("✅ Sentence Transformers")
        
        import faiss
        print("✅ FAISS")
        
        import pandas
        print("✅ Pandas")
        
        from utils.data_processor import LegalDataProcessor
        print("✅ Data Processor")
        
        from utils.rag_system import LegalRAGSystem
        print("✅ RAG System")
        
        from components.ui_components import render_sidebar_filters
        print("✅ UI Components")
        
        return True
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False

def test_data_loading():
    """Test data loading functionality"""
    print("\n🧪 Testing data loading...")
    
    try:
        data_dir = Path('data')
        csv_files = list(data_dir.glob('*.csv'))
        
        if not csv_files:
            print("❌ No CSV files found")
            return False
        
        csv_file = csv_files[0]
        print(f"📄 Testing with: {csv_file}")
        
        from utils.data_processor import LegalDataProcessor
        processor = LegalDataProcessor(str(csv_file))
        df = processor.load_data()
        
        print(f"✅ Loaded {len(df)} acts")
        print(f"✅ Columns: {list(df.columns)}")
        
        # Test processing
        chunks = processor.process_all_acts()
        print(f"✅ Created {len(chunks)} document chunks")
        
        return True
        
    except Exception as e:
        print(f"❌ Data loading error: {e}")
        return False

def test_api_connection():
    """Test Google API connection"""
    print("\n🧪 Testing API connection...")
    
    try:
        load_dotenv()
        api_key = os.getenv('GOOGLE_API_KEY')
        
        if not api_key or api_key == 'your_gemini_api_key_here':
            print("❌ API key not configured")
            return False
        
        import google.generativeai as genai
        genai.configure(api_key=api_key)
        
        model = genai.GenerativeModel('gemini-1.5-flash')
        response = model.generate_content("Hello, this is a test.")
        
        if response.text:
            print("✅ API connection successful")
            print(f"✅ Response: {response.text[:50]}...")
            return True
        else:
            print("❌ No response from API")
            return False
            
    except Exception as e:
        print(f"❌ API connection error: {e}")
        return False

def main():
    """Run all tests"""
    print("🔬 Testing Bangladesh Legal RAG Assistant")
    print("=" * 50)
    
    tests = [
        ("Import Test", test_imports),
        ("Data Loading Test", test_data_loading), 
        ("API Connection Test", test_api_connection)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        print(f"\n🧪 {test_name}")
        print("-" * 30)
        result = test_func()
        results.append((test_name, result))
    
    # Summary
    print("\n📊 Test Summary")
    print("=" * 30)
    
    passed = 0
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{test_name}: {status}")
        if result:
            passed += 1
    
    print(f"\nOverall: {passed}/{len(tests)} tests passed")
    
    if passed == len(tests):
        print("🎉 All tests passed! System is ready to run.")
        print("Run: streamlit run app.py")
    else:
        print("⚠️  Some tests failed. Please check the errors above.")

if __name__ == "__main__":
    main()