import os
import json
import pickle
from typing import List, Dict, Any, Optional, Tuple
import numpy as np
from sentence_transformers import SentenceTransformer
import faiss
import google.generativeai as genai
from datetime import datetime
import logging
from dataclasses import dataclass

logger = logging.getLogger(__name__)

@dataclass
class SearchResult:
    content: str
    metadata: Dict[str, Any]
    score: float
    chunk_id: str
    chunk_type: str

class LegalRAGSystem:
    def __init__(self, 
                 google_api_key: str,
                 model_name: str = "gemini-1.5-flash",
                 embedding_model: str = "all-mpnet-base-v2",
                 vector_store_path: str = "./vectorstore"):
        
        self.google_api_key = google_api_key
        self.model_name = model_name
        self.vector_store_path = vector_store_path
        
        # Initialize Gemini
        genai.configure(api_key=google_api_key)
        self.model = genai.GenerativeModel(model_name)
        
        # Initialize embedding model
        logger.info(f"Loading embedding model: {embedding_model}")
        self.embedding_model = SentenceTransformer(embedding_model)
        
        # Vector store components
        self.index = None
        self.documents = []
        self.document_metadata = []
        
        # Create vector store directory
        os.makedirs(vector_store_path, exist_ok=True)
        
    def create_embeddings(self, texts: List[str]) -> np.ndarray:
        """Create embeddings for a list of texts"""
        logger.info(f"Creating embeddings for {len(texts)} texts")
        embeddings = self.embedding_model.encode(texts, show_progress_bar=True)
        return embeddings
    
    def build_vector_store(self, documents: List[Dict[str, Any]]):
        """Build FAISS vector store from processed documents"""
        logger.info(f"Building vector store from {len(documents)} documents")
        
        # Extract texts and metadata
        texts = [doc['content'] for doc in documents]
        self.documents = texts
        self.document_metadata = [doc['metadata'] for doc in documents]
        
        # Create embeddings
        embeddings = self.create_embeddings(texts)
        
        # Build FAISS index
        dimension = embeddings.shape[1]
        self.index = faiss.IndexFlatIP(dimension)  # Inner product for similarity
        
        # Normalize embeddings for cosine similarity
        faiss.normalize_L2(embeddings)
        self.index.add(embeddings.astype('float32'))
        
        logger.info(f"Vector store built with {self.index.ntotal} documents")
        
        # Save vector store
        self.save_vector_store()
    
    def save_vector_store(self):
        """Save vector store to disk"""
        # Save FAISS index
        faiss.write_index(self.index, os.path.join(self.vector_store_path, "index.faiss"))
        
        # Save documents and metadata
        with open(os.path.join(self.vector_store_path, "documents.pkl"), 'wb') as f:
            pickle.dump(self.documents, f)
        
        with open(os.path.join(self.vector_store_path, "metadata.pkl"), 'wb') as f:
            pickle.dump(self.document_metadata, f)
        
        logger.info("Vector store saved successfully")
    
    def load_vector_store(self) -> bool:
        """Load vector store from disk"""
        try:
            # Load FAISS index
            index_path = os.path.join(self.vector_store_path, "index.faiss")
            if os.path.exists(index_path):
                self.index = faiss.read_index(index_path)
            else:
                return False
            
            # Load documents and metadata
            with open(os.path.join(self.vector_store_path, "documents.pkl"), 'rb') as f:
                self.documents = pickle.load(f)
            
            with open(os.path.join(self.vector_store_path, "metadata.pkl"), 'rb') as f:
                self.document_metadata = pickle.load(f)
            
            logger.info(f"Vector store loaded with {len(self.documents)} documents")
            return True
            
        except Exception as e:
            logger.error(f"Error loading vector store: {str(e)}")
            return False
    
    def search(self, query: str, top_k: int = 5, filters: Dict[str, Any] = None) -> List[SearchResult]:
        """Search for relevant documents"""
        if self.index is None:
            raise ValueError("Vector store not built or loaded")
        
        # Create query embedding
        query_embedding = self.embedding_model.encode([query])
        faiss.normalize_L2(query_embedding)
        
        # Search in FAISS
        scores, indices = self.index.search(query_embedding.astype('float32'), top_k * 2)  # Get more for filtering
        
        results = []
        for score, idx in zip(scores[0], indices[0]):
            if idx == -1:  # FAISS returns -1 for invalid indices
                continue
                
            metadata = self.document_metadata[idx]
            
            # Apply filters
            if filters:
                if not self._apply_filters(metadata, filters):
                    continue
            
            result = SearchResult(
                content=self.documents[idx],
                metadata=metadata,
                score=float(score),
                chunk_id=metadata.get('chunk_id', f'chunk_{idx}'),
                chunk_type=metadata.get('chunk_type', 'unknown')
            )
            results.append(result)
            
            if len(results) >= top_k:
                break
        
        return results
    
    def _apply_filters(self, metadata: Dict[str, Any], filters: Dict[str, Any]) -> bool:
        """Apply filters to metadata"""
        for key, value in filters.items():
            if key == 'year_range' and isinstance(value, tuple):
                year_str = metadata.get('act_year', '')
                if year_str and year_str.isdigit():
                    year = int(year_str)
                    if not (value[0] <= year <= value[1]):
                        return False
            
            elif key == 'is_repealed' and isinstance(value, bool):
                if metadata.get('is_repealed', False) != value:
                    return False
            
            elif key == 'language' and isinstance(value, str):
                if metadata.get('language_detected', '') != value:
                    return False
            
            elif key == 'keywords' and isinstance(value, list):
                content_lower = metadata.get('act_title', '').lower()
                if not any(kw.lower() in content_lower for kw in value):
                    return False
        
        return True
    
    def generate_response(self, 
                         query: str, 
                         context_documents: List[SearchResult],
                         mode: str = "general",
                         conversation_history: List[Dict] = None) -> str:
        """Generate response using Gemini with RAG context"""
        
        # Build context from retrieved documents
        context = self._build_context(context_documents)
        
        # Select prompt template based on mode
        prompt = self._get_prompt_template(mode, query, context, conversation_history)
        
        try:
            # Generate response using Gemini
            response = self.model.generate_content(prompt)
            
            if response.text:
                return response.text
            else:
                return "I apologize, but I couldn't generate a response. Please try rephrasing your question."
                
        except Exception as e:
            logger.error(f"Error generating response: {str(e)}")
            return f"I encountered an error while processing your request: {str(e)}"
    
    def _build_context(self, documents: List[SearchResult]) -> str:
        """Build context string from retrieved documents"""
        if not documents:
            return "No relevant legal documents found."
        
        context_parts = []
        for i, doc in enumerate(documents, 1):
            metadata = doc.metadata
            
            context_part = f"""
Document {i}:
Title: {metadata.get('act_title', 'N/A')}
Year: {metadata.get('act_year', 'N/A')}
Section: {metadata.get('section_title', 'Overview')}
Status: {'Repealed' if metadata.get('is_repealed', False) else 'Active'}
Content: {doc.content[:500]}...
            """
            context_parts.append(context_part.strip())
        
        return "\n\n".join(context_parts)
    
    def _get_prompt_template(self, mode: str, query: str, context: str, history: List[Dict] = None) -> str:
        """Get appropriate prompt template based on mode"""
        
        # Common context setup
        base_context = f"""
You are a Bangladesh Legal Assistant AI, specialized in helping with legal questions based on the Bangladesh legal database.

Available Legal Context:
{context}

Current Query: {query}
        """
        
        if mode == "lawyer":
            return f"""{base_context}

LAWYER MODE: You are acting as a legal professional providing expert legal advice.

Instructions:
1. Provide comprehensive legal analysis
2. Cite specific acts, sections, and years
3. Explain legal implications and consequences
4. Suggest legal strategies or approaches
5. Mention relevant precedents if applicable
6. Use formal legal language
7. Always caveat that this is general guidance and recommend consulting a practicing lawyer for specific cases

Response format: Provide detailed legal analysis with citations.
"""
        
        elif mode == "argument":
            return f"""{base_context}

ARGUMENT MODE: Help build legal arguments and counterarguments.

Instructions:
1. Identify the main legal issues
2. Present arguments for different sides
3. Cite supporting legal provisions
4. Identify potential weaknesses in arguments
5. Suggest evidence or precedents that might be relevant
6. Present both plaintiff and defendant perspectives where applicable

Response format: Structure as "Arguments For:" and "Arguments Against:" with legal citations.
"""
        
        elif mode == "research":
            return f"""{base_context}

RESEARCH MODE: Provide comprehensive legal research assistance.

Instructions:
1. Identify all relevant laws and regulations
2. Provide historical context and amendments
3. Compare with similar provisions in other acts
4. Explain the legislative intent and purpose
5. List related acts and cross-references
6. Provide implementation guidelines if available

Response format: Comprehensive research summary with extensive citations.
"""
        
        elif mode == "simple":
            return f"""{base_context}

SIMPLE MODE: Explain legal concepts in easy-to-understand language.

Instructions:
1. Use simple, non-technical language
2. Explain legal jargon and concepts
3. Provide practical examples
4. Focus on what it means for ordinary citizens
5. Break down complex procedures into steps
6. Avoid excessive legal citations

Response format: Clear, simple explanation that a non-lawyer can understand.
"""
        
        else:  # general mode
            return f"""{base_context}

GENERAL MODE: Provide balanced legal information and guidance.

Instructions:
1. Answer the question directly and clearly
2. Provide relevant legal context
3. Cite applicable laws with act names and years
4. Explain practical implications
5. Maintain professional but accessible tone
6. Suggest next steps if appropriate

Response format: Clear, informative response with appropriate legal citations.
"""
    
    def get_chat_response(self, 
                         query: str,
                         mode: str = "general",
                         filters: Dict[str, Any] = None,
                         conversation_history: List[Dict] = None,
                         top_k: int = 5) -> Tuple[str, List[SearchResult]]:
        """Get complete chat response with RAG"""
        
        # Search for relevant documents
        search_results = self.search(query, top_k=top_k, filters=filters)
        
        # Generate response
        response = self.generate_response(query, search_results, mode, conversation_history)
        
        return response, search_results

# Usage example
if __name__ == "__main__":
    # Initialize RAG system
    rag = LegalRAGSystem(
        google_api_key="your_api_key_here",
        vector_store_path="./vectorstore"
    )
    
    # Load or build vector store
    if not rag.load_vector_store():
        print("Building new vector store...")
        # Load processed documents
        with open("data/processed_documents.json", 'r', encoding='utf-8') as f:
            documents = json.load(f)
        rag.build_vector_store(documents)
    
    # Test query
    query = "What are the penalties for digital crimes?"
    response, results = rag.get_chat_response(query, mode="lawyer")
    
    print(f"Query: {query}")
    print(f"Response: {response}")
    print(f"Sources: {len(results)} documents used")