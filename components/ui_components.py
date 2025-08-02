import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, date
from typing import List, Dict, Any, Optional
import pandas as pd
from wordcloud import WordCloud
import matplotlib.pyplot as plt

def render_sidebar_filters() -> Dict[str, Any]:
    """Render sidebar filters and return filter values"""
    
    st.sidebar.header("🔍 Search Filters")
    
    filters = {}
    
    # Mode selection
    st.sidebar.subheader("Assistant Mode")
    mode = st.sidebar.selectbox(
        "Choose Assistant Mode:",
        ["general", "lawyer", "argument", "research", "simple"],
        format_func=lambda x: {
            "general": "🤖 General Assistant",
            "lawyer": "⚖️ Legal Professional",
            "argument": "🎯 Argument Builder", 
            "research": "📚 Legal Researcher",
            "simple": "👤 Simple Explanation"
        }[x],
        help="Select the type of legal assistance you need"
    )
    filters['mode'] = mode
    
    # Year range filter
    st.sidebar.subheader("Year Range")
    col1, col2 = st.sidebar.columns(2)
    with col1:
        start_year = st.number_input("From", min_value=1800, max_value=2024, value=1971)
    with col2:
        end_year = st.number_input("To", min_value=1800, max_value=2024, value=2024)
    
    if start_year <= end_year:
        filters['year_range'] = (start_year, end_year)
    
    # Act status filter
    st.sidebar.subheader("Act Status")
    status_filter = st.sidebar.radio(
        "Show acts:",
        ["All", "Active Only", "Repealed Only"],
        help="Filter by whether acts are currently active or have been repealed"
    )
    
    if status_filter == "Active Only":
        filters['is_repealed'] = False
    elif status_filter == "Repealed Only":
        filters['is_repealed'] = True
    
    # Language filter
    st.sidebar.subheader("Content Language")
    language_filter = st.sidebar.selectbox(
        "Preferred Language:",
        ["Any", "English", "Bengali", "Mixed"],
        help="Filter by content language"
    )
    
    if language_filter != "Any":
        filters['language'] = language_filter.lower()
    
    # Keywords filter
    st.sidebar.subheader("Keywords")
    keywords_input = st.sidebar.text_input(
        "Keywords (comma separated):",
        placeholder="contract, property, criminal",
        help="Add specific keywords to focus the search"
    )
    
    if keywords_input:
        keywords = [kw.strip() for kw in keywords_input.split(',') if kw.strip()]
        filters['keywords'] = keywords
    
    # Number of results
    st.sidebar.subheader("Search Results")
    top_k = st.sidebar.slider("Number of results:", min_value=1, max_value=20, value=5)
    filters['top_k'] = top_k
    
    return filters

def render_chat_interface():
    """Render the main chat interface"""
    
    # Initialize chat history
    if "messages" not in st.session_state:
        st.session_state.messages = []
    
    # Display chat history
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
            
            # Show sources if available
            if message["role"] == "assistant" and "sources" in message:
                with st.expander(f"📚 Sources ({len(message['sources'])} documents)"):
                    for i, source in enumerate(message["sources"], 1):
                        st.write(f"**{i}. {source.metadata.get('act_title', 'Unknown Act')}**")
                        st.write(f"Year: {source.metadata.get('act_year', 'N/A')}")
                        st.write(f"Section: {source.metadata.get('section_title', 'Overview')}")
                        st.write(f"Relevance Score: {source.score:.3f}")
                        with st.expander("View Content"):
                            st.text(source.content[:500] + "..." if len(source.content) > 500 else source.content)
                        st.divider()
    
    return st.session_state.messages

def render_mode_explanation(mode: str):
    """Render explanation for selected mode"""
    
    mode_info = {
        "general": {
            "icon": "🤖",
            "title": "General Legal Assistant",
            "description": "Provides balanced legal information with clear explanations and relevant citations.",
            "best_for": "General legal questions, understanding laws, basic legal guidance"
        },
        "lawyer": {
            "icon": "⚖️", 
            "title": "Legal Professional Mode",
            "description": "Comprehensive legal analysis with formal language, citations, and professional insights.",
            "best_for": "Complex legal analysis, professional legal research, detailed legal opinions"
        },
        "argument": {
            "icon": "🎯",
            "title": "Argument Builder",
            "description": "Helps build legal arguments and counterarguments with supporting evidence.",
            "best_for": "Case preparation, debate preparation, understanding different legal perspectives"
        },
        "research": {
            "icon": "📚",
            "title": "Legal Researcher", 
            "description": "Comprehensive research with historical context, cross-references, and extensive citations.",
            "best_for": "Academic research, legislative history, comprehensive legal analysis"
        },
        "simple": {
            "icon": "👤",
            "title": "Simple Explanation Mode",
            "description": "Explains legal concepts in plain language that anyone can understand.",
            "best_for": "Learning legal basics, understanding rights, citizen-friendly explanations"
        }
    }
    
    info = mode_info.get(mode, mode_info["general"])
    
    st.info(f"""
    **{info['icon']} {info['title']}**
    
    {info['description']}
    
    **Best for:** {info['best_for']}
    """)

def render_statistics_dashboard(stats: Dict[str, Any]):
    """Render statistics dashboard"""
    
    st.header("📊 Legal Database Statistics")
    
    # Key metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Acts", stats.get('total_acts', 0))
    
    with col2:
        st.metric("Active Acts", stats.get('active_acts', 0))
    
    with col3:
        st.metric("Repealed Acts", stats.get('repealed_acts', 0))
    
    with col4:
        st.metric("Search Documents", stats.get('total_chunks', 0))
    
    # Year coverage
    years_coverage = stats.get('years_coverage', {})
    if years_coverage.get('earliest') and years_coverage.get('latest'):
        st.subheader("📅 Time Coverage")
        st.write(f"**Coverage:** {years_coverage['earliest']} - {years_coverage['latest']}")
        st.write(f"**Span:** {years_coverage['latest'] - years_coverage['earliest']} years")
    
    # Charts
    col1, col2 = st.columns(2)
    
    with col1:
        # Acts by decade
        acts_by_decade = stats.get('acts_by_decade', {})
        if acts_by_decade:
            st.subheader("📈 Acts by Decade")
            
            decades = list(acts_by_decade.keys())
            counts = list(acts_by_decade.values())
            
            fig = px.bar(
                x=decades, 
                y=counts,
                title="Number of Acts by Decade",
                labels={'x': 'Decade', 'y': 'Number of Acts'}
            )
            fig.update_layout(showlegend=False)
            st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        # Language distribution
        lang_dist = stats.get('language_distribution', {})
        if lang_dist:
            st.subheader("🌐 Language Distribution")
            
            fig = px.pie(
                values=list(lang_dist.values()),
                names=list(lang_dist.keys()),
                title="Content Language Distribution"
            )
            st.plotly_chart(fig, use_container_width=True)

def render_search_results(results: List, query: str):
    """Render search results in an organized way"""
    
    if not results:
        st.warning("No relevant documents found for your query.")
        return
    
    st.subheader(f"🔍 Search Results for: '{query}'")
    st.write(f"Found {len(results)} relevant documents")
    
    for i, result in enumerate(results, 1):
        with st.expander(f"📄 {i}. {result.metadata.get('act_title', 'Unknown Act')} (Score: {result.score:.3f})"):
            
            # Metadata
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.write(f"**Year:** {result.metadata.get('act_year', 'N/A')}")
                st.write(f"**Act ID:** {result.metadata.get('act_id', 'N/A')}")
            
            with col2:
                st.write(f"**Status:** {'🔴 Repealed' if result.metadata.get('is_repealed') else '🟢 Active'}")
                st.write(f"**Type:** {result.chunk_type.title()}")
            
            with col3:
                st.write(f"**Language:** {result.metadata.get('language_detected', 'Unknown')}")
                st.write(f"**Sections:** {result.metadata.get('total_sections', 'N/A')}")
            
            # Content preview
            st.write("**Content Preview:**")
            preview = result.content[:300] + "..." if len(result.content) > 300 else result.content
            st.text(preview)
            
            # Full content toggle
            if st.button(f"Show Full Content {i}", key=f"full_content_{i}"):
                st.text_area("Full Content:", result.content, height=200, key=f"content_area_{i}")
            
            # URL if available
            if result.metadata.get('url'):
                st.write(f"**Source:** [{result.metadata['url']}]({result.metadata['url']})")

def render_legal_topics_explorer(df: pd.DataFrame):
    """Render legal topics explorer"""
    
    st.header("🗂️ Legal Topics Explorer")
    
    if df is None or df.empty:
        st.warning("No data available for exploration.")
        return
    
    # Topic analysis based on act titles
    if 'act_title' in df.columns:
        st.subheader("📋 Common Legal Topics")
        
        # Extract common words from titles
        all_titles = df['act_title'].dropna().str.lower().str.cat(sep=' ')
        
        # Create word cloud
        if all_titles:
            try:
                wordcloud = WordCloud(
                    width=800, 
                    height=400, 
                    background_color='white',
                    colormap='viridis'
                ).generate(all_titles)
                
                fig, ax = plt.subplots(figsize=(10, 5))
                ax.imshow(wordcloud, interpolation='bilinear')
                ax.axis('off')
                st.pyplot(fig)
                
            except Exception as e:
                st.error(f"Could not generate word cloud: {str(e)}")
    
    # Browse by categories
    st.subheader("🏷️ Browse by Categories")
    
    # Categorize acts based on titles
    categories = {
        "Criminal Law": ["criminal", "penal", "police", "crime"],
        "Civil Law": ["civil", "contract", "property", "family"],
        "Commercial Law": ["company", "business", "trade", "commercial"],
        "Constitutional Law": ["constitution", "fundamental", "rights"],
        "Administrative Law": ["government", "administrative", "public"],
        "Tax Law": ["tax", "income", "customs", "vat"],
        "Labor Law": ["labor", "employment", "worker", "industrial"]
    }
    
    category_counts = {}
    for category, keywords in categories.items():
        if 'act_title' in df.columns:
            count = df[df['act_title'].str.lower().str.contains('|'.join(keywords), na=False)].shape[0]
            category_counts[category] = count
    
    # Display category buttons
    cols = st.columns(3)
    for i, (category, count) in enumerate(category_counts.items()):
        with cols[i % 3]:
            if st.button(f"{category}\n({count} acts)", key=f"cat_{category}"):
                st.session_state['selected_category'] = category
    
    # Show acts for selected category
    if 'selected_category' in st.session_state:
        selected_cat = st.session_state['selected_category']
        keywords = categories.get(selected_cat, [])
        
        if keywords and 'act_title' in df.columns:
            filtered_df = df[df['act_title'].str.lower().str.contains('|'.join(keywords), na=False)]
            
            st.subheader(f"📚 {selected_cat} Acts ({len(filtered_df)} found)")
            
            for _, row in filtered_df.head(10).iterrows():
                with st.expander(f"{row.get('act_title', 'Unknown')} ({row.get('act_year', 'N/A')})"):
                    col1, col2 = st.columns(2)
                    with col1:
                        st.write(f"**Act Number:** {row.get('act_number', 'N/A')}")
                        st.write(f"**Year:** {row.get('act_year', 'N/A')}")
                    with col2:
                        st.write(f"**Status:** {'Repealed' if row.get('is_repealed') else 'Active'}")
                        st.write(f"**Sections:** {row.get('total_sections', 'N/A')}")

def render_quick_help():
    """Render quick help and examples"""
    
    st.header("💡 Quick Help & Examples")
    
    # Sample questions by mode
    examples = {
        "🤖 General Questions": [
            "What is the punishment for theft in Bangladesh?",
            "How do I register a company in Bangladesh?",
            "What are the fundamental rights in the constitution?"
        ],
        "⚖️ Legal Professional": [
            "Analyze the legal implications of breach of contract under Bangladesh law",
            "What are the procedural requirements for filing a civil suit?",
            "Compare the penalties for different types of fraud"
        ],
        "🎯 Argument Building": [
            "Build arguments for and against digital privacy rights",
            "What are the defenses available in a defamation case?",
            "Arguments for contract rescission due to misrepresentation"
        ],
        "📚 Research Queries": [
            "Historical development of labor laws in Bangladesh",
            "All amendments to the Evidence Act since independence",
            "Cross-references between family law and inheritance law"
        ],
        "👤 Simple Explanations": [
            "Explain what a contract means in simple terms",
            "What rights do tenants have?",
            "How does the court system work in Bangladesh?"
        ]
    }
    
    for category, questions in examples.items():
        with st.expander(category):
            for i, question in enumerate(questions, 1):
                col1, col2 = st.columns([4, 1])
                with col1:
                    st.write(f"{i}. {question}")
                with col2:
                    if st.button("Try", key=f"example_{category}_{i}"):
                        st.session_state['example_query'] = question
    
    # Tips and tricks
    st.subheader("💡 Tips for Better Results")
    
    tips = [
        "**Be specific**: Instead of 'property law', try 'property inheritance rights' or 'land registration process'",
        "**Use legal terms**: Terms like 'breach', 'liability', 'jurisdiction' help find more relevant results",
        "**Specify time period**: Add year ranges to find laws from specific periods",
        "**Ask follow-up questions**: Build on previous answers for deeper understanding",
        "**Use different modes**: Switch modes for different perspectives on the same topic"
    ]
    
    for tip in tips:
        st.write(f"• {tip}")

def render_footer():
    """Render application footer"""
    
    st.markdown("---")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("**Bangladesh Legal Assistant**")
        st.markdown("AI-powered legal research tool")
    
    with col2:
        st.markdown("**Disclaimer**")
        st.markdown("This tool provides general legal information only. Consult a qualified lawyer for legal advice.")
    
    with col3:
        st.markdown("**Last Updated**")
        st.markdown(f"{datetime.now().strftime('%B %Y')}")
    
    st.markdown(
        "<div style='text-align: center; color: #666; margin-top: 20px;'>"
        "⚖️ Built for educational and research purposes • "
        "🇧🇩 Bangladesh Legal Database"
        "</div>",
        unsafe_allow_html=True
    )