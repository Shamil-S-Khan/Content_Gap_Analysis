"""
Content Gap Analysis - Topic Modeling and Semantic Clustering Engine
Implements LDA, semantic similarity, and topic clustering for content comparison
"""

import json
import numpy as np
from typing import Dict, List, Any, Tuple
from collections import defaultdict
from datetime import datetime

try:
    from sklearn.feature_extraction.text import TfidfVectorizer, CountVectorizer
    from sklearn.decomposition import LatentDirichletAllocation, NMF
    from sklearn.metrics.pairwise import cosine_similarity
    from sklearn.cluster import KMeans
    import nltk
    from nltk.tokenize import word_tokenize
    from nltk.corpus import stopwords
except ImportError:
    print("Installing required libraries...")
    import subprocess
    subprocess.run(["pip", "install", "scikit-learn", "nltk", "numpy"])


class TopicModelingEngine:
    """Performs topic modeling and semantic clustering"""
    
    def __init__(self, n_topics: int = 10, n_clusters: int = 5):
        """Initialize topic modeling parameters"""
        self.n_topics = n_topics
        self.n_clusters = n_clusters
        self.stop_words = set(stopwords.words('english'))
        
        # Initialize vectorizers
        self.tfidf_vectorizer = TfidfVectorizer(
            max_features=1000,
            min_df=2,
            max_df=0.8,
            stop_words='english',
            ngram_range=(1, 2)
        )
        
        self.count_vectorizer = CountVectorizer(
            max_features=1000,
            min_df=2,
            max_df=0.8,
            stop_words='english',
            ngram_range=(1, 2)
        )
        
        # Initialize models
        self.lda_model = LatentDirichletAllocation(
            n_components=n_topics,
            random_state=42,
            max_iter=20,
            learning_method='batch'
        )
        
        self.nmf_model = NMF(
            n_components=n_topics,
            random_state=42,
            max_iter=200
        )
        
        self.kmeans_model = KMeans(
            n_clusters=n_clusters,
            random_state=42,
            n_init=10
        )
    
    def extract_topics_lda(self, documents: List[str], n_top_words: int = 10) -> List[Dict[str, Any]]:
        """Extract topics using Latent Dirichlet Allocation"""
        
        # Create document-term matrix
        doc_term_matrix = self.count_vectorizer.fit_transform(documents)
        
        # Fit LDA model
        self.lda_model.fit(doc_term_matrix)
        
        # Extract topics
        feature_names = self.count_vectorizer.get_feature_names_out()
        topics = []
        
        for topic_idx, topic in enumerate(self.lda_model.components_):
            top_indices = topic.argsort()[-n_top_words:][::-1]
            top_words = [feature_names[i] for i in top_indices]
            top_weights = [float(topic[i]) for i in top_indices]
            
            topics.append({
                'topic_id': topic_idx,
                'words': top_words,
                'weights': top_weights,
                'label': f"Topic {topic_idx}: {', '.join(top_words[:3])}"
            })
        
        return topics
    
    def extract_topics_nmf(self, documents: List[str], n_top_words: int = 10) -> List[Dict[str, Any]]:
        """Extract topics using Non-negative Matrix Factorization"""
        
        # Create TF-IDF matrix
        tfidf_matrix = self.tfidf_vectorizer.fit_transform(documents)
        
        # Fit NMF model
        self.nmf_model.fit(tfidf_matrix)
        
        # Extract topics
        feature_names = self.tfidf_vectorizer.get_feature_names_out()
        topics = []
        
        for topic_idx, topic in enumerate(self.nmf_model.components_):
            top_indices = topic.argsort()[-n_top_words:][::-1]
            top_words = [feature_names[i] for i in top_indices]
            top_weights = [float(topic[i]) for i in top_indices]
            
            topics.append({
                'topic_id': topic_idx,
                'words': top_words,
                'weights': top_weights,
                'label': f"Topic {topic_idx}: {', '.join(top_words[:3])}"
            })
        
        return topics
    
    def cluster_documents(self, documents: List[str]) -> Dict[str, Any]:
        """Cluster documents using K-Means"""
        
        # Create TF-IDF matrix
        tfidf_matrix = self.tfidf_vectorizer.fit_transform(documents)
        
        # Perform clustering
        clusters = self.kmeans_model.fit_predict(tfidf_matrix)
        
        # Get cluster centers and top terms
        feature_names = self.tfidf_vectorizer.get_feature_names_out()
        cluster_info = []
        
        for cluster_id in range(self.n_clusters):
            center = self.kmeans_model.cluster_centers_[cluster_id]
            top_indices = center.argsort()[-10:][::-1]
            top_terms = [feature_names[i] for i in top_indices]
            
            # Get documents in this cluster
            doc_indices = np.where(clusters == cluster_id)[0]
            
            cluster_info.append({
                'cluster_id': cluster_id,
                'size': len(doc_indices),
                'top_terms': top_terms,
                'document_indices': doc_indices.tolist(),
                'label': f"Cluster {cluster_id}: {', '.join(top_terms[:3])}"
            })
        
        return {
            'clusters': cluster_info,
            'assignments': clusters.tolist(),
            'inertia': float(self.kmeans_model.inertia_)
        }
    
    def calculate_semantic_similarity(self, docs1: List[str], docs2: List[str]) -> np.ndarray:
        """Calculate semantic similarity between two document sets"""
        
        # Combine documents for consistent vectorization
        all_docs = docs1 + docs2
        
        # Create TF-IDF matrix
        tfidf_matrix = self.tfidf_vectorizer.fit_transform(all_docs)
        
        # Split back into two sets
        matrix1 = tfidf_matrix[:len(docs1)]
        matrix2 = tfidf_matrix[len(docs1):]
        
        # Calculate cosine similarity
        similarity_matrix = cosine_similarity(matrix1, matrix2)
        
        return similarity_matrix
    
    def compare_corpora(self, your_docs: List[str], competitor_docs: List[str]) -> Dict[str, Any]:
        """Comprehensive comparison between your content and competitor content"""
        
        # Extract topics from both corpora
        your_topics = self.extract_topics_lda(your_docs, n_top_words=15)
        competitor_topics = self.extract_topics_lda(competitor_docs, n_top_words=15)
        
        # Cluster both corpora
        your_clusters = self.cluster_documents(your_docs)
        competitor_clusters = self.cluster_documents(competitor_docs)
        
        # Calculate semantic similarity
        similarity_matrix = self.calculate_semantic_similarity(your_docs, competitor_docs)
        
        # Identify topic gaps (topics in competitor content but not in yours)
        your_topic_words = set()
        for topic in your_topics:
            your_topic_words.update(topic['words'][:5])
        
        competitor_topic_words = set()
        for topic in competitor_topics:
            competitor_topic_words.update(topic['words'][:5])
        
        missing_topics = competitor_topic_words - your_topic_words
        shared_topics = your_topic_words & competitor_topic_words
        
        # Calculate coverage metrics
        avg_similarity = float(np.mean(similarity_matrix))
        max_similarity = float(np.max(similarity_matrix))
        
        # Identify competitor documents with low similarity to your content
        avg_doc_similarity = np.mean(similarity_matrix, axis=0)
        low_coverage_indices = np.where(avg_doc_similarity < 0.3)[0]
        
        return {
            'your_topics': your_topics,
            'competitor_topics': competitor_topics,
            'your_clusters': your_clusters,
            'competitor_clusters': competitor_clusters,
            'missing_topics': list(missing_topics),
            'shared_topics': list(shared_topics),
            'coverage_metrics': {
                'avg_similarity': avg_similarity,
                'max_similarity': max_similarity,
                'topic_overlap_ratio': len(shared_topics) / len(competitor_topic_words) if competitor_topic_words else 0,
                'low_coverage_doc_count': len(low_coverage_indices)
            },
            'low_coverage_documents': low_coverage_indices.tolist()
        }
    
    def identify_content_themes(self, documents: List[str], metadata: List[Dict]) -> List[Dict[str, Any]]:
        """Identify major content themes with metadata"""
        
        # Extract topics
        topics = self.extract_topics_nmf(documents, n_top_words=15)
        
        # Get document-topic distribution
        tfidf_matrix = self.tfidf_vectorizer.transform(documents)
        doc_topic_dist = self.nmf_model.transform(tfidf_matrix)
        
        # Assign primary topic to each document
        primary_topics = np.argmax(doc_topic_dist, axis=1)
        
        # Aggregate metadata by topic
        theme_analysis = []
        for topic_idx, topic in enumerate(topics):
            doc_indices = np.where(primary_topics == topic_idx)[0]
            
            # Aggregate keywords from documents in this theme
            theme_keywords = []
            for idx in doc_indices:
                if idx < len(metadata):
                    theme_keywords.extend(metadata[idx].get('keywords', []))
            
            # Get top keywords
            from collections import Counter
            keyword_freq = Counter(theme_keywords)
            top_keywords = [k for k, v in keyword_freq.most_common(20)]
            
            theme_analysis.append({
                'theme_id': topic_idx,
                'theme_label': topic['label'],
                'topic_words': topic['words'],
                'document_count': len(doc_indices),
                'top_keywords': top_keywords,
                'document_indices': doc_indices.tolist()
            })
        
        return theme_analysis


def main():
    """Example usage"""
    print("Topic Modeling Engine initialized")
    
    # Load corpus data
    try:
        with open('data/your_content_corpus.json', 'r') as f:
            your_corpus = json.load(f)
        
        with open('data/competitor_corpus.json', 'r') as f:
            competitor_corpus = json.load(f)
        
        # Extract document texts (this would come from actual processing)
        # For now, using placeholder
        print("Topic modeling requires processed document corpus")
        print("Run data_ingestion.py first to generate corpus data")
        
    except FileNotFoundError:
        print("Corpus data not found. Run data_ingestion.py first.")


if __name__ == "__main__":
    main()
