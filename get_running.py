import subprocess
import sys
import os
from pathlib import Path

def emergency_setup():
    """Emergency setup with minimal dependencies"""
    
    print("🚨 Emergency Setup for Legal RAG Assistant")
    print("=" * 50)
    
    # Step 1: Install absolutely essential packages
    print("📦 Installing essential packages...")
    essential_packages = [
        "streamlit",
        "pandas", 
        "python-dotenv",
        "google-generativeai",
        "scikit-learn",
        "matplotlib",
        "plotly"
    ]
    
    for package in essential_packages:
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", package])
            print(f"✅ {package}")
        except:
            print(f"❌ {package} - continuing anyway...")
    
    # Step 2: Create minimal working app
    create_minimal_app()
    
    # Step 3: Setup environment
    create_minimal_env()
    
    print("\n✅ Emergency setup complete!")
    print("🚀 Run: streamlit run app_minimal.py")

def create_minimal_app():
    """Create absolutely minimal working app"""
    
    app_code = '''import streamlit as st
import pandas as pd
import os
from dotenv import load_dotenv

# Load environment
load_dotenv()

# Page setup
st.set_page_config(page_title="Legal Assistant", page_icon="⚖️", layout="wide")

st.markdown("""
# ⚖️ Bangladesh Legal Assistant (Minimal)
**Basic Legal Search System**
""")

# Check for API key
api_key = os.getenv('GOOGLE_API_KEY', '')
if not api_key or api_key == 'your_gemini_api_key_here':
    st.error("⚠️ Please add your Google Gemini API key to the .env file")
    st.info("Get your API key from: https://makersuite.google.com/app/apikey")
    st.code("GOOGLE_API_KEY=your_actual_api_key_here")
    st.stop()

# Initialize Gemini
try:
    import google.generativeai as genai
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel('gemini-1.5-flash')
    st.success("✅ Gemini AI connected successfully!")
except Exception as e:
    st.error(f"❌ Gemini connection failed: {e}")
    st.stop()

# Data loading
st.sidebar.header("📁 Data")
data_path = st.sidebar.text_input("CSV file path:", "data/bangladesh_laws.csv")

@st.cache_data
def load_data(file_path):
    try:
        df = pd.read_csv(file_path, encoding='utf-8-sig')
        return df
    except Exception as e:
        return None

# Load data
if os.path.exists(data_path):
    df = load_data(data_path)
    if df is not None:
        st.sidebar.success(f"✅ Loaded {len(df)} acts")
        
        # Display basic stats
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Total Acts", len(df))
        with col2:
            active_acts = len(df[~df.get('is_repealed', False)]) if 'is_repealed' in df.columns else len(df)
            st.metric("Active Acts", active_acts)
        with col3:
            if 'act_year' in df.columns:
                years = df['act_year'].dropna()
                year_range = f"{years.min()}-{years.max()}" if len(years) > 0 else "N/A"
                st.metric("Year Range", year_range)
    else:
        st.error("❌ Failed to load CSV file")
        df = None
else:
    st.warning(f"⚠️ CSV file not found: {data_path}")
    df = None

# Search interface
st.header("💬 Legal Assistant")

# Mode selection
mode = st.selectbox("Assistant Mode:", 
    ["general", "lawyer", "simple"],
    format_func=lambda x: {"general": "🤖 General", "lawyer": "⚖️ Professional", "simple": "👤 Simple"}[x]
)

# Query input
query = st.text_input("Ask your legal question:", 
    placeholder="What is the punishment for theft in Bangladesh?")

if st.button("🔍 Get Answer", type="primary") and query:
    if df is None:
        st.error("Please load a CSV file first")
    else:
        with st.spinner("Generating response..."):
            
            # Simple search in dataframe
            search_results = []
            query_lower = query.lower()
            
            for _, row in df.iterrows():
                score = 0
                title = str(row.get('act_title', '')).lower()
                content = str(row.get('sections_summary', '') + ' ' + row.get('preamble', '')).lower()
                
                # Simple keyword matching
                for word in query_lower.split():
                    if word in title:
                        score += 3
                    if word in content:
                        score += 1
                
                if score > 0:
                    search_results.append((score, row))
            
            # Sort by relevance
            search_results.sort(reverse=True)
            top_results = search_results[:3]
            
            if top_results:
                # Build context for Gemini
                context = "Relevant Bangladesh Legal Information:\\n\\n"
                for i, (score, row) in enumerate(top_results, 1):
                    context += f"""
Document {i}:
Title: {row.get('act_title', 'N/A')}
Year: {row.get('act_year', 'N/A')}
Status: {'Repealed' if row.get('is_repealed', False) else 'Active'}
Content: {str(row.get('sections_summary', ''))[:300]}
                    """
                
                # Create prompt based on mode
                if mode == "lawyer":
                    prompt = f"""You are a Bangladesh legal expert. Provide comprehensive legal analysis for: {query}
                    
{context}

Provide detailed legal analysis with citations and professional recommendations."""
                
                elif mode == "simple":
                    prompt = f"""Explain this legal question in simple terms anyone can understand: {query}
                    
{context}

Use plain language and avoid legal jargon."""
                
                else:
                    prompt = f"""Answer this legal question based on Bangladesh law: {query}
                    
{context}

Provide clear information with relevant legal references."""
                
                try:
                    # Generate response
                    response = model.generate_content(prompt)
                    
                    # Display response
                    st.subheader("💬 Response")
                    st.write(response.text)
                    
                    # Show sources
                    with st.expander(f"📚 Sources ({len(top_results)} documents)"):
                        for i, (score, row) in enumerate(top_results, 1):
                            st.write(f"""
                            **{i}. {row.get('act_title', 'Unknown')}**
                            - Year: {row.get('act_year', 'N/A')}
                            - Score: {score}
                            - Status: {'🔴 Repealed' if row.get('is_repealed', False) else '🟢 Active'}
                            """)
                
                except Exception as e:
                    st.error(f"Error generating response: {e}")
            
            else:
                st.warning("No relevant documents found for your query.")

# Instructions
with st.expander("📖 How to Use"):
    st.markdown("""
    **Setup:**
    1. Get Gemini API key from: https://makersuite.google.com/app/apikey
    2. Add to .env file: `GOOGLE_API_KEY=your_key_here`
    3. Place CSV file in data/ directory
    
    **Usage:**
    - Select assistant mode (General/Professional/Simple)
    - Type your legal question
    - Click "Get Answer"
    
    **Example Questions:**
    - What is the punishment for theft?
    - How to register a company?
    - Explain contract law in simple terms
    """)

# Footer
st.markdown("---")
st.markdown("⚖️ **Bangladesh Legal Assistant (Minimal Version)** - For educational purposes only")
'''
    
    with open('app_minimal.py', 'w', encoding='utf-8') as f:
        f.write(app_code)
    
    print("✅ Created minimal app: app_minimal.py")

def create_minimal_env():
    """Create minimal .env file"""
    env_content = """# Google Gemini API Key
GOOGLE_API_KEY=your_gemini_api_key_here

# Get your API key from: https://makersuite.google.com/app/apikey
"""
    
    if not os.path.exists('.env'):
        with open('.env', 'w') as f:
            f.write(env_content)
        print("✅ Created .env file")
    else:
        print("✅ .env file already exists")

def check_system():
    """Quick system check"""
    print("\n🔍 System Check:")
    
    # Check Python version
    python_version = sys.version_info
    print(f"Python: {python_version.major}.{python_version.minor}.{python_version.micro}")
    
    # Check essential imports
    imports_to_check = [
        ('streamlit', 'Streamlit'),
        ('pandas', 'Pandas'),
        ('google.generativeai', 'Gemini AI'),
    ]
    
    for module, name in imports_to_check:
        try:
            __import__(module)
            print(f"✅ {name}")
        except ImportError:
            print(f"❌ {name}")
    
    # Check data directory
    if os.path.exists('data'):
        csv_files = list(Path('data').glob('*.csv'))
        print(f"📁 Data files: {len(csv_files)} CSV files found")
    else:
        print("📁 Data directory: Not found")
    
    # Check .env file
    if os.path.exists('.env'):
        print("📄 .env file: Found")
    else:
        print("📄 .env file: Not found")

def main():
    """Main emergency setup"""
    try:
        emergency_setup()
        check_system()
        
        print(f"\n{'='*50}")
        print("🎉 EMERGENCY SETUP COMPLETE!")
        print(f"{'='*50}")
        print("\n📋 Next Steps:")
        print("1. Get Gemini API key: https://makersuite.google.com/app/apikey")
        print("2. Edit .env file and add your API key")
        print("3. Put your CSV file in data/ directory")
        print("4. Run: streamlit run app_minimal.py")
        print("\n💡 This minimal version uses basic search instead of advanced embeddings")
        
    except Exception as e:
        print(f"\n❌ Emergency setup failed: {e}")
        print("\n📞 Manual steps:")
        print("1. pip install streamlit pandas google-generativeai python-dotenv")
        print("2. Create app_minimal.py with the code provided")
        print("3. Add API key to .env file")
        print("4. streamlit run app_minimal.py")

if __name__ == "__main__":
    main()