import pandas as pd
import numpy as np
import json
import re
from typing import List, Dict, Any, Optional
from datetime import datetime
import logging
from pathlib import Path

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class LegalDataProcessor:
    def __init__(self, csv_path: str):
        """Initialize with CSV file path"""
        self.csv_path = csv_path
        self.df = None
        self.processed_documents = []
        
    def load_data(self) -> pd.DataFrame:
        """Load and validate CSV data"""
        try:
            logger.info(f"Loading data from {self.csv_path}")
            self.df = pd.read_csv(self.csv_path, encoding='utf-8-sig')
            
            # Validate required columns
            required_cols = ['act_id', 'act_title', 'act_year']
            missing_cols = [col for col in required_cols if col not in self.df.columns]
            
            if missing_cols:
                raise ValueError(f"Missing required columns: {missing_cols}")
            
            logger.info(f"Loaded {len(self.df)} acts successfully")
            return self.df
            
        except Exception as e:
            logger.error(f"Error loading data: {str(e)}")
            raise
    
    def clean_text(self, text: str) -> str:
        """Clean and normalize text content"""
        if pd.isna(text) or text == '':
            return ""
        
        text = str(text)
        
        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text)
        
        # Remove special characters but keep Bengali
        text = re.sub(r'[^\w\s\u0980-\u09FF.,;:!?()-]', ' ', text)
        
        return text.strip()
    
    def extract_sections_from_json(self, sections_json: str) -> List[Dict]:
        """Extract sections from JSON string"""
        if pd.isna(sections_json) or sections_json == '':
            return []
        
        try:
            sections = json.loads(sections_json)
            if isinstance(sections, list):
                return sections
            return []
        except (json.JSONDecodeError, TypeError):
            return []
    
    def create_document_chunks(self, row: pd.Series) -> List[Dict[str, Any]]:
        """Create searchable document chunks from a single act"""
        chunks = []
        
        # Basic act information
        act_info = {
            'act_id': row.get('act_id', ''),
            'act_title': self.clean_text(row.get('act_title', '')),
            'act_title_bengali': self.clean_text(row.get('act_title_bengali', '')),
            'act_number': self.clean_text(row.get('act_number', '')),
            'act_year': str(row.get('act_year', '')),
            'publication_date': self.clean_text(row.get('publication_date', '')),
            'is_repealed': bool(row.get('is_repealed', False)),
            'repealed_by': self.clean_text(row.get('repealed_by', '')),
            'url': row.get('url', ''),
            'total_sections': row.get('total_sections', 0),
            'language_detected': row.get('language_detected', 'unknown')
        }
        
        # Main document chunk (act overview)
        main_title = act_info['act_title'] or act_info['act_title_bengali']
        if main_title:
            overview_content = f"""
            Act Title: {main_title}
            Act Number: {act_info['act_number']}
            Year: {act_info['act_year']}
            Publication Date: {act_info['publication_date']}
            Status: {'Repealed' if act_info['is_repealed'] else 'Active'}
            Total Sections: {act_info['total_sections']}
            """
            
            if act_info['is_repealed'] and act_info['repealed_by']:
                overview_content += f"\nRepealed by: {act_info['repealed_by']}"
            
            # Add preamble if available
            preamble = self.clean_text(row.get('preamble', ''))
            if preamble:
                overview_content += f"\nPreamble: {preamble}"
            
            chunks.append({
                'content': self.clean_text(overview_content),
                'chunk_type': 'overview',
                'chunk_id': f"{act_info['act_id']}_overview",
                'metadata': act_info
            })
        
        # Section chunks
        sections_json = row.get('sections_json', '')
        sections = self.extract_sections_from_json(sections_json)
        
        for i, section in enumerate(sections):
            if isinstance(section, dict):
                section_title = self.clean_text(section.get('title', ''))
                section_content = self.clean_text(section.get('content', ''))
                chapter = self.clean_text(section.get('chapter', ''))
                
                if section_title or section_content:
                    section_text = f"""
                    Act: {main_title}
                    Section: {section_title}
                    Chapter: {chapter}
                    Content: {section_content}
                    """
                    
                    section_metadata = act_info.copy()
                    section_metadata.update({
                        'section_number': i + 1,
                        'section_title': section_title,
                        'chapter': chapter
                    })
                    
                    chunks.append({
                        'content': self.clean_text(section_text),
                        'chunk_type': 'section',
                        'chunk_id': f"{act_info['act_id']}_section_{i+1}",
                        'metadata': section_metadata
                    })
        
        return chunks
    
    def process_all_acts(self) -> List[Dict[str, Any]]:
        """Process all acts and create document chunks"""
        if self.df is None:
            self.load_data()
        
        logger.info("Processing all acts into document chunks...")
        all_chunks = []
        
        for idx, row in self.df.iterrows():
            try:
                chunks = self.create_document_chunks(row)
                all_chunks.extend(chunks)
                
                if (idx + 1) % 100 == 0:
                    logger.info(f"Processed {idx + 1}/{len(self.df)} acts")
                    
            except Exception as e:
                logger.error(f"Error processing act {row.get('act_id', 'unknown')}: {str(e)}")
                continue
        
        logger.info(f"Created {len(all_chunks)} document chunks from {len(self.df)} acts")
        self.processed_documents = all_chunks
        return all_chunks
    
    def filter_by_year_range(self, start_year: int, end_year: int) -> List[Dict[str, Any]]:
        """Filter documents by year range"""
        filtered = []
        for doc in self.processed_documents:
            year_str = doc['metadata'].get('act_year', '')
            if year_str and year_str.isdigit():
                year = int(year_str)
                if start_year <= year <= end_year:
                    filtered.append(doc)
        return filtered
    
    def filter_by_keywords(self, keywords: List[str]) -> List[Dict[str, Any]]:
        """Filter documents by keywords"""
        filtered = []
        keywords_lower = [kw.lower() for kw in keywords]
        
        for doc in self.processed_documents:
            content_lower = doc['content'].lower()
            title_lower = doc['metadata'].get('act_title', '').lower()
            
            if any(kw in content_lower or kw in title_lower for kw in keywords_lower):
                filtered.append(doc)
        
        return filtered
    
    def get_act_statistics(self) -> Dict[str, Any]:
        """Get statistics about the legal database"""
        if self.df is None:
            return {}
        
        stats = {
            'total_acts': len(self.df),
            'total_chunks': len(self.processed_documents),
            'active_acts': len(self.df[~self.df.get('is_repealed', False)]),
            'repealed_acts': len(self.df[self.df.get('is_repealed', False)]),
            'years_coverage': {
                'earliest': None,
                'latest': None
            },
            'language_distribution': {},
            'acts_by_decade': {}
        }
        
        # Year statistics
        years = self.df[self.df['act_year'].notna() & (self.df['act_year'] != '')]['act_year']
        if len(years) > 0:
            year_ints = [int(y) for y in years if str(y).isdigit()]
            if year_ints:
                stats['years_coverage']['earliest'] = min(year_ints)
                stats['years_coverage']['latest'] = max(year_ints)
                
                # Acts by decade
                for year in year_ints:
                    decade = (year // 10) * 10
                    decade_key = f"{decade}s"
                    stats['acts_by_decade'][decade_key] = stats['acts_by_decade'].get(decade_key, 0) + 1
        
        # Language distribution
        if 'language_detected' in self.df.columns:
            lang_counts = self.df['language_detected'].value_counts().to_dict()
            stats['language_distribution'] = lang_counts
        
        return stats
    
    def save_processed_data(self, output_path: str):
        """Save processed document chunks"""
        if not self.processed_documents:
            self.process_all_acts()
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(self.processed_documents, f, ensure_ascii=False, indent=2)
        
        logger.info(f"Saved {len(self.processed_documents)} processed documents to {output_path}")

# Usage example
if __name__ == "__main__":
    processor = LegalDataProcessor("data/bangladesh_laws.csv")
    processor.load_data()
    chunks = processor.process_all_acts()
    stats = processor.get_act_statistics()
    
    print("Database Statistics:")
    for key, value in stats.items():
        print(f"  {key}: {value}")
    
    processor.save_processed_data("data/processed_documents.json")