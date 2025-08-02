# app.py
"""
Main Streamlit Application for Bangladesh Legal RAG Assistant
"""

import streamlit as st
import os
import json
import pandas as pd
from datetime import datetime
import logging
from pathlib import Path
from dotenv import load_dotenv

# Import custom modules
from utils.data_processor import LegalDataProcessor
from utils.rag_system import LegalRAGSystem
from components.ui_components import (
    render_sidebar_filters,
    render_chat_interface,
    render_mode_explanation,
    render_statistics_dashboard, 
    render_search_results,
    render_legal_topics_explorer,
    render_quick_help,
    render_footer
)

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/app.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Page configuration
st.set_page_config(
    page_title="Bangladesh Legal Assistant",
    page_icon="⚖️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        background: linear-gradient(90deg, #1e3c72 0%, #2a5298 100%);
        padding: 1rem;
        border-radius: 10px;
        color: white;
        text-align: center;
        margin-bottom: 2rem;
    }
    
    .chat-message {
        padding: 1rem;
        border-radius: 10px;
        margin: 1rem 0;
        border-left: 4px solid #2a5298;
    }
    
    .source-card {
        background: #f8f9fa;
        padding: 1rem;
        border-radius: 8px;
        border-left: 3px solid #28a745;
        margin: 0.5rem 0;
    }
    
    .stButton > button {
        width: 100%;
        border-radius: 20px;
        border: none;
        background: linear-gradient(90deg, #1e3c72 0%, #2a5298 100%);
        color: white;
    }
    
    .mode-info {
        background: #e3f2fd;
        padding: 1rem;
        border-radius: 8px;
        border-left: 4px solid #2196f3;
    }
</style>
""", unsafe_allow_html=True)

def initialize_system():
    """Initialize the RAG system"""
    try:
        # Get API key
        api_key = os.getenv('GOOGLE_API_KEY')
        if not api_key or api_key == 'your_gemini_api_key_here':
            st.error("⚠️ Google API key not configured. Please add your actual Google Gemini API key to the .env file")
            st.info("🔗 Get your API key from: https://makersuite.google.com/app/apikey")
            st.code("GOOGLE_API_KEY=your_actual_api_key_here", language="bash")
            st.stop()
        
        # Initialize RAG system (cached separately)
        if 'rag_system' not in st.session_state:
            st.session_state.rag_system = LegalRAGSystem(
                google_api_key=api_key,
                vector_store_path=os.getenv('VECTOR_STORE_PATH', './vectorstore')
            )
        
        rag_system = st.session_state.rag_system
        
        # Try to load existing vector store
        if rag_system.load_vector_store():
            logger.info("Loaded existing vector store")
            return rag_system, True
        else:
            logger.info("No existing vector store found")
            return rag_system, False
            
    except Exception as e:
        logger.error(f"Error initializing system: {str(e)}")
        st.error(f"Failed to initialize system: {str(e)}")
        st.stop()

@st.cache_data
def load_legal_data():
    """Load and process legal data with caching"""
    try:
        # Look for CSV files in data directory
        data_dir = Path("data")
        csv_files = list(data_dir.glob("*.csv"))
        
        if not csv_files:
            st.error("⚠️ No CSV files found in data/ directory. Please add your legal database CSV file.")
            st.stop()
        
        # Use the first CSV file found (or let user select)
        csv_file = csv_files[0]
        logger.info(f"Loading data from {csv_file}")
        
        # Load data
        processor = LegalDataProcessor(str(csv_file))
        df = processor.load_data()
        stats = processor.get_act_statistics()
        
        return df, processor, stats
        
    except Exception as e:
        logger.error(f"Error loading data: {str(e)}")
        st.error(f"Failed to load legal data: {str(e)}")
        st.stop()

def build_vector_store_ui(rag_system, processor):
    """UI for building vector store"""
    st.warning("🏗️ Vector store not found. Building new vector store...")
    
    if not st.session_state.building_vector_store:
        if st.button("🚀 Start Building Vector Store"):
            st.session_state.building_vector_store = True
            st.rerun()
    else:
        with st.spinner("Processing legal documents and building search index..."):
            try:
                # Process documents
                documents = processor.process_all_acts()
                
                # Build vector store
                rag_system.build_vector_store(documents)
                
                st.success("✅ Vector store built successfully!")
                st.session_state.building_vector_store = False
                st.session_state.vector_store_built = True
                st.rerun()
                
            except Exception as e:
                st.error(f"Failed to build vector store: {str(e)}")
                logger.error(f"Vector store build error: {str(e)}")
                st.session_state.building_vector_store = False

def main():
    """Main application"""
    
    # Initialize session state
    if 'messages' not in st.session_state:
        st.session_state.messages = []
    if 'building_vector_store' not in st.session_state:
        st.session_state.building_vector_store = False
    if 'vector_store_built' not in st.session_state:
        st.session_state.vector_store_built = False
    
    # Header
    st.markdown("""
    <div class="main-header">
        <h1>⚖️ Bangladesh Legal Assistant</h1>
        <p>AI-Powered Legal Research & Advisory System</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Initialize system
    rag_system, vector_store_loaded = initialize_system()
    
    # Load data
    df, processor, stats = load_legal_data()
    
    # Build vector store if needed
    if not vector_store_loaded:
        build_vector_store_ui(rag_system, processor)
        return
    
    # Sidebar filters
    filters = render_sidebar_filters()
    
    # Chat input (outside tabs to avoid Streamlit restriction)
    prompt = st.chat_input("Ask your legal question here...", key="main_chat")
    
    # Handle example queries
    if 'example_query' in st.session_state:
        prompt = st.session_state['example_query']
        del st.session_state['example_query']
    
    # Main navigation
    tab1, tab2, tab3, tab4 = st.tabs(["💬 Chat Assistant", "📊 Database Stats", "🗂️ Browse Topics", "💡 Help"])
    
    with tab1:
        # Chat Assistant Tab
        col1, col2 = st.columns([2, 1])
        
        with col2:
            # Mode explanation
            render_mode_explanation(filters['mode'])
        
        with col1:
            # Chat interface
            st.subheader("💬 Legal Chat Assistant")
            
            # Process chat input if provided
            if prompt:
                # Add user message to chat history
                if 'messages' not in st.session_state:
                    st.session_state.messages = []
                st.session_state.messages.append({"role": "user", "content": prompt})
                
                # Display user message
                with st.chat_message("user"):
                    st.markdown(prompt)
                
                # Generate assistant response
                with st.chat_message("assistant"):
                    with st.spinner("Researching legal documents..."):
                        try:
                            # Prepare filters for RAG
                            rag_filters = {}
                            if 'year_range' in filters:
                                rag_filters['year_range'] = filters['year_range']
                            if 'is_repealed' in filters:
                                rag_filters['is_repealed'] = filters['is_repealed']
                            if 'language' in filters:
                                rag_filters['language'] = filters['language']
                            if 'keywords' in filters:
                                rag_filters['keywords'] = filters['keywords']
                            
                            # Get response from RAG system
                            response, sources = rag_system.get_chat_response(
                                query=prompt,
                                mode=filters['mode'],
                                filters=rag_filters,
                                conversation_history=st.session_state.get('messages', [])[-10:],  # Last 10 messages
                                top_k=filters.get('top_k', 5)
                            )
                            
                            # Display response
                            st.markdown(response)
                            
                            # Display sources
                            if sources:
                                with st.expander(f"📚 Sources ({len(sources)} documents)", expanded=False):
                                    for i, source in enumerate(sources, 1):
                                        st.markdown(f"""
                                        **{i}. {source.metadata.get('act_title', 'Unknown Act')}**
                                        - Year: {source.metadata.get('act_year', 'N/A')}
                                        - Section: {source.metadata.get('section_title', 'Overview')}
                                        - Relevance: {source.score:.3f}
                                        - Status: {'🔴 Repealed' if source.metadata.get('is_repealed') else '🟢 Active'}
                                        
                                        **Content Preview:**
                                        {source.content[:400] + "..." if len(source.content) > 400 else source.content}
                                        """)
                                        st.markdown("---")
                            
                            # Add assistant message to chat history
                            if 'messages' not in st.session_state:
                                st.session_state.messages = []
                            st.session_state.messages.append({
                                "role": "assistant",
                                "content": response,
                                "sources": sources
                            })
                            
                        except Exception as e:
                            error_msg = f"I apologize, but I encountered an error: {str(e)}"
                            st.error(error_msg)
                            logger.error(f"Chat error: {str(e)}")
                            
                            if 'messages' not in st.session_state:
                                st.session_state.messages = []
                            st.session_state.messages.append({
                                "role": "assistant",
                                "content": error_msg
                            })
        
        # Display chat history
        st.markdown("---")
        if st.session_state.get('messages', []):
            st.subheader("💬 Conversation History")
            
            # Clear chat button
            if st.button("🗑️ Clear Chat History"):
                st.session_state.messages = []
                st.rerun()
            
            # Display messages (excluding the current ones already shown)
            messages = st.session_state.get('messages', [])
            for i, message in enumerate(messages[:-2] if len(messages) > 2 else []):
                with st.chat_message(message["role"]):
                    st.markdown(message["content"])
                    
                    if message["role"] == "assistant" and "sources" in message:
                        st.write(f"**Sources ({len(message['sources'])}):**")
                        for j, source in enumerate(message["sources"], 1):
                            st.write(f"  {j}. {source.metadata.get('act_title', 'Unknown')}")
    
    with tab2:
        # Database Statistics Tab
        render_statistics_dashboard(stats)
        
        # Additional statistics
        st.subheader("📈 Detailed Statistics")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.write("**Top 10 Most Recent Acts:**")
            if 'act_year' in df.columns:
                try:
                    # Convert act_year to numeric, handling non-numeric values
                    df_copy = df.copy()
                    df_copy['act_year_numeric'] = pd.to_numeric(df_copy['act_year'], errors='coerce')
                    recent_acts = df_copy[df_copy['act_year_numeric'].notna()].nlargest(10, 'act_year_numeric')
                    for _, row in recent_acts.iterrows():
                        st.write(f"• {row.get('act_title', 'Unknown')} ({row.get('act_year', 'N/A')})")
                except Exception as e:
                    st.write("• Unable to display recent acts (data format issue)")
        
        with col2:
            st.write("**Database Coverage:**")
            st.write(f"• Total Documents: {len(df):,}")
            st.write(f"• Searchable Chunks: {stats.get('total_chunks', 0):,}")
            st.write(f"• Years Covered: {stats.get('years_coverage', {}).get('latest', 0) - stats.get('years_coverage', {}).get('earliest', 0)} years")
            st.write(f"• Average Sections per Act: {df['total_sections'].mean():.1f}" if 'total_sections' in df.columns else "")
    
    with tab3:
        # Browse Topics Tab  
        render_legal_topics_explorer(df)
    
    with tab4:
        # Help Tab
        render_quick_help()
        
        # System information
        st.subheader("🔧 System Information")
        col1, col2 = st.columns(2)
        
        with col1:
            st.write("**Current Settings:**")
            st.write(f"• Mode: {filters['mode'].title()}")
            st.write(f"• Results: {filters.get('top_k', 5)}")
            st.write(f"• Year Range: {filters.get('year_range', 'All')}")
            
        with col2:
            st.write("**Database Info:**")
            st.write(f"• Total Acts: {len(df):,}")
            st.write(f"• Vector Store: {'✅ Loaded' if vector_store_loaded else '❌ Not loaded'}")
            st.write(f"• Last Updated: {datetime.now().strftime('%Y-%m-%d')}")
    
    # Footer
    render_footer()

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        st.error(f"Application error: {str(e)}")
        logger.error(f"Main application error: {str(e)}")
        
        # Debug information
        if os.getenv('DEBUG', 'False').lower() == 'true':
            st.exception(e)