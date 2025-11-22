"""
Content Gap Analysis - Data Ingestion and Preprocessing Module
Extracts text, metadata, keywords, entities from multiple document formats
"""

import json
import re
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional
from collections import Counter
import hashlib

# Document processing libraries
try:
    from bs4 import BeautifulSoup
    import nltk
    from nltk.tokenize import word_tokenize, sent_tokenize
    from nltk.corpus import stopwords
    from nltk.stem import WordNetLemmatizer
    import spacy
except ImportError:
    print("Installing required libraries...")
    import subprocess
    subprocess.run(["pip", "install", "beautifulsoup4", "nltk", "spacy"])
    

class DocumentProcessor:
    """Processes documents and extracts comprehensive metadata"""
    
    def __init__(self):
        """Initialize NLP components"""
        # Download NLTK data
        try:
            nltk.data.find('tokenizers/punkt')
        except LookupError:
            nltk.download('punkt')
            nltk.download('stopwords')
            nltk.download('wordnet')
            nltk.download('averaged_perceptron_tagger')
        
        self.lemmatizer = WordNetLemmatizer()
        self.stop_words = set(stopwords.words('english'))
        
        # Try to load spaCy model
        try:
            self.nlp = spacy.load('en_core_web_sm')
        except OSError:
            print("Downloading spaCy model...")
            import subprocess
            subprocess.run(["python", "-m", "spacy", "download", "en_core_web_sm"])
            self.nlp = spacy.load('en_core_web_sm')
    
    def extract_text_from_file(self, file_path: str) -> str:
        """Extract text from various file formats"""
        path = Path(file_path)
        
        if not path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")
        
        if path.suffix.lower() == '.txt':
            with open(file_path, 'r', encoding='utf-8') as f:
                return f.read()
        
        elif path.suffix.lower() == '.json':
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                # Extract text from common JSON structures
                if isinstance(data, dict):
                    text_parts = []
                    for key, value in data.items():
                        if isinstance(value, str):
                            text_parts.append(value)
                        elif isinstance(value, list):
                            text_parts.extend([str(v) for v in value])
                    # Store the JSON data for later metadata extraction
                    self._current_json_data = data
                    return ' '.join(text_parts)
                elif isinstance(data, list):
                    self._current_json_data = None
                    return ' '.join([str(item) for item in data])
                else:
                    self._current_json_data = None
                    return str(data)
        
        elif path.suffix.lower() in ['.html', '.htm']:
            with open(file_path, 'r', encoding='utf-8') as f:
                soup = BeautifulSoup(f.read(), 'html.parser')
                return soup.get_text()
        
        elif path.suffix.lower() == '.md':
            with open(file_path, 'r', encoding='utf-8') as f:
                return f.read()
        
        else:
            # Default: try to read as text
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                return f.read()
    
    def extract_metadata(self, text: str, source: str = "unknown") -> Dict[str, Any]:
        """Extract comprehensive metadata from text"""
        
        # Try to get title from JSON data if available
        title = None
        if hasattr(self, '_current_json_data') and self._current_json_data:
            title = self._current_json_data.get('title')
            self._current_json_data = None  # Clear after use
        
        # Basic statistics
        sentences = sent_tokenize(text)
        words = word_tokenize(text.lower())
        
        # Filter stopwords and get clean tokens
        clean_tokens = [
            self.lemmatizer.lemmatize(word) 
            for word in words 
            if word.isalnum() and word not in self.stop_words
        ]
        
        # Extract keywords (top 20 most common)
        word_freq = Counter(clean_tokens)
        keywords = [word for word, count in word_freq.most_common(20)]
        
        # Extract entities using spaCy
        doc = self.nlp(text[:100000])  # Limit for performance
        entities = {
            'PERSON': [],
            'ORG': [],
            'GPE': [],
            'PRODUCT': [],
            'EVENT': [],
            'DATE': []
        }
        
        for ent in doc.ents:
            if ent.label_ in entities:
                entities[ent.label_].append(ent.text)
        
        # Clean up entities (unique values only)
        entities = {k: list(set(v)) for k, v in entities.items()}
        
        # Extract headings (if markdown or HTML-like)
        headings = re.findall(r'^#+\s+(.+)$', text, re.MULTILINE)
        headings.extend(re.findall(r'<h[1-6]>(.+?)</h[1-6]>', text, re.IGNORECASE))
        
        # Extract URLs
        urls = re.findall(r'https?://[^\s<>"]+|www\.[^\s<>"]+', text)
        
        # Calculate text hash for deduplication
        text_hash = hashlib.md5(text.encode()).hexdigest()
        
        metadata = {
            'source': source,
            'char_count': len(text),
            'word_count': len(words),
            'sentence_count': len(sentences),
            'token_count': len(clean_tokens),
            'unique_tokens': len(set(clean_tokens)),
            'keywords': keywords,
            'entities': entities,
            'headings': headings[:10],  # Top 10 headings
            'urls': urls[:20],  # Top 20 URLs
            'timestamp': datetime.now().isoformat(),
            'text_hash': text_hash,
            'avg_sentence_length': len(words) / len(sentences) if sentences else 0,
            'lexical_diversity': len(set(clean_tokens)) / len(clean_tokens) if clean_tokens else 0
        }
        
        # Add title if available
        if title:
            metadata['title'] = title
        
        return metadata
    
    def process_corpus(self, file_paths: List[str], corpus_name: str = "corpus") -> Dict[str, Any]:
        """Process multiple documents and aggregate statistics"""
        
        all_texts = []
        all_metadata = []
        total_tokens = 0
        total_chars = 0
        all_keywords = []
        all_entities = {'PERSON': [], 'ORG': [], 'GPE': [], 'PRODUCT': [], 'EVENT': [], 'DATE': []}
        
        for file_path in file_paths:
            try:
                text = self.extract_text_from_file(file_path)
                metadata = self.extract_metadata(text, source=file_path)
                
                all_texts.append(text)
                all_metadata.append(metadata)
                total_tokens += metadata['token_count']
                total_chars += metadata['char_count']
                all_keywords.extend(metadata['keywords'])
                
                # Aggregate entities
                for entity_type in all_entities:
                    all_entities[entity_type].extend(metadata['entities'].get(entity_type, []))
                
            except Exception as e:
                print(f"Error processing {file_path}: {str(e)}")
                continue
        
        # Get top keywords across corpus
        keyword_freq = Counter(all_keywords)
        top_keywords = [word for word, count in keyword_freq.most_common(50)]
        
        # Get unique entities
        unique_entities = {k: list(set(v)) for k, v in all_entities.items()}
        
        return {
            'corpus_name': corpus_name,
            'document_count': len(all_metadata),
            'total_token_count': total_tokens,
            'total_char_count': total_chars,
            'page_count': total_chars // 2000,  # Estimate: ~2000 chars per page
            'top_keywords': top_keywords,
            'entities': unique_entities,
            'documents': all_metadata,
            'processed_at': datetime.now().isoformat()
        }
    
    def save_corpus_data(self, corpus_data: Dict[str, Any], output_path: str):
        """Save processed corpus data to JSON"""
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(corpus_data, f, indent=2, ensure_ascii=False)
        print(f"Corpus data saved to: {output_path}")


def main():
    """Example usage"""
    processor = DocumentProcessor()
    
    # Example: Process your organization's content
    your_files = [
        # Add your content file paths here
        # "path/to/your/content1.txt",
        # "path/to/your/content2.md",
    ]
    
    # Example: Process competitor content
    competitor_files = [
        # Add competitor content file paths here
        # "path/to/competitor/content1.txt",
        # "path/to/competitor/content2.html",
    ]
    
    if your_files:
        your_corpus = processor.process_corpus(your_files, "your_organization")
        processor.save_corpus_data(your_corpus, "data/your_content_corpus.json")
    
    if competitor_files:
        competitor_corpus = processor.process_corpus(competitor_files, "competitors")
        processor.save_corpus_data(competitor_corpus, "data/competitor_corpus.json")
    
    print("Data ingestion complete!")


if __name__ == "__main__":
    main()
