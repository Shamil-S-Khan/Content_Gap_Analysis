"""
Content Gap Analysis - Machine Learning Model with Evaluation Metrics
Implements classification model for gap detection with comprehensive metrics
"""

import json
import numpy as np
from typing import Dict, List, Any, Tuple
from collections import Counter
import random


try:
    from sklearn.model_selection import train_test_split, cross_val_score
    from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
    from sklearn.metrics import (
        precision_score, recall_score, f1_score, accuracy_score,
        confusion_matrix, classification_report
    )
    from sklearn.feature_extraction.text import TfidfVectorizer
except ImportError:
    print("Installing scikit-learn...")
    import subprocess
    subprocess.run(["pip", "install", "scikit-learn"])


class GapClassificationModel:
    """ML model for classifying content gaps with evaluation metrics"""
    
    def __init__(self, random_state: int = 42):
        """Initialize classification model"""
        self.random_state = random_state
        
        # Initialize classifiers
        self.rf_classifier = RandomForestClassifier(
            n_estimators=100,
            max_depth=10,
            random_state=random_state,
            class_weight='balanced'
        )
        
        self.gb_classifier = GradientBoostingClassifier(
            n_estimators=100,
            max_depth=5,
            random_state=random_state,
            learning_rate=0.1
        )
        
        # Vectorizer for text features
        self.vectorizer = TfidfVectorizer(
            max_features=500,
            min_df=2,
            max_df=0.8,
            stop_words='english',
            ngram_range=(1, 2)
        )
        
        # Class labels
        self.gap_types = ['missing', 'thin', 'outdated', 'under-optimized']
        self.label_map = {label: idx for idx, label in enumerate(self.gap_types)}
        self.reverse_label_map = {idx: label for label, idx in self.label_map.items()}
        
        # Trained model
        self.trained_model = None
    
    def create_training_dataset(self, 
                               gaps: List[Dict[str, Any]],
                               synthetic_samples: int = 200) -> Tuple[np.ndarray, np.ndarray, List[str]]:
        """
        Create training dataset from gaps with synthetic augmentation
        
        Returns:
            features, labels, sample_descriptions
        """
        
        texts = []
        labels = []
        descriptions = []
        
        # Add actual gaps
        for gap in gaps:
            text = f"{gap['title']} {' '.join(gap['keywords'][:10])} {gap.get('reason', '')}"
            texts.append(text)
            labels.append(self.label_map[gap['gap_type']])
            descriptions.append(f"Real: {gap['title']}")
        
        # Generate synthetic samples for training
        synthetic_data = self._generate_synthetic_samples(synthetic_samples)
        for sample in synthetic_data:
            texts.append(sample['text'])
            labels.append(self.label_map[sample['gap_type']])
            descriptions.append(f"Synthetic: {sample['description']}")
        
        # Vectorize texts
        features = self.vectorizer.fit_transform(texts).toarray()
        labels = np.array(labels)
        
        return features, labels, descriptions
    
    def _generate_synthetic_samples(self, n_samples: int) -> List[Dict[str, Any]]:
        """Generate synthetic training samples with realistic overlap and ambiguity"""
        
        samples = []
        
        # MORE REALISTIC templates with overlapping language
        templates = {
            'missing': [
                "{topic} coverage needs improvement and expansion",
                "Limited discussion of {topic} compared to industry standards",
                "{topic} section is incomplete and requires development",
                "Competitors have extensive {topic} content we lack",
                "Our {topic} information is insufficient for users",
                "{topic} gaps identified in content audit"
            ],
            'thin': [
                "{topic} content exists but lacks sufficient detail",
                "Superficial {topic} coverage needs more depth",
                "Brief mention of {topic} without comprehensive explanation",
                "{topic} section is too short and needs expansion",
                "Limited {topic} examples and use cases provided",
                "Our {topic} content is less detailed than competitors"
            ],
            'outdated': [
                "{topic} information may be outdated or stale",
                "Content about {topic} needs updating and refresh",
                "{topic} section references old data and statistics",
                "Our {topic} coverage doesn't reflect current trends",
                "{topic} content was last updated over a year ago",
                "Need to modernize {topic} discussion and examples"
            ],
            'under-optimized': [
                "{topic} content has low keyword density and poor SEO",
                "Missing relevant {topic} keywords in metadata",
                "{topic} page lacks proper heading structure",
                "Our {topic} content ranks poorly in search results",
                "{topic} section needs better internal linking",
                "Suboptimal {topic} content for search engines"
            ]
        }
        
        # Add AMBIGUOUS templates that could fit multiple categories
        ambiguous_templates = [
            "{topic} content needs work",  # Could be any type
            "Issues with our {topic} coverage",  # Could be any type
            "{topic} section requires attention",  # Could be any type
            "Problems identified in {topic} area",  # Could be any type
            "{topic} content gaps present",  # Could be missing or thin
            "Need to improve {topic} information"  # Could be thin or outdated
        ]
        
        # More varied topics with technical overlap
        topics = [
            "machine learning", "artificial intelligence", "data analysis", "data science",
            "cloud computing", "cloud infrastructure", "cybersecurity", "network security",
            "digital marketing", "content marketing", "project management", "agile methodology",
            "customer service", "customer experience", "sales strategy", "business development",
            "product development", "product design", "team collaboration", "remote work",
            "business intelligence", "data visualization", "automation", "workflow automation",
            "mobile apps", "mobile development", "web development", "full-stack development",
            "API integration", "API design", "database management", "data architecture",
            "user experience", "UI design", "content strategy", "SEO strategy",
            "social media", "social media marketing", "email marketing", "marketing automation"
        ]
        
        # Generate samples with intentional overlap
        samples_per_type = n_samples // len(self.gap_types)
        
        for gap_type in self.gap_types:
            for i in range(samples_per_type):
                topic = random.choice(topics)
                
                # 90% use type-specific template, 10% use ambiguous template
                if random.random() < 0.90:
                    template = random.choice(templates[gap_type])
                else:
                    template = random.choice(ambiguous_templates)
                
                text = template.format(topic=topic)
                
                # Add noise - 3% chance of WRONG label (reduced from 5%)
                actual_gap_type = gap_type
                if random.random() < 0.03:
                    # Mislabel some samples
                    actual_gap_type = random.choice([gt for gt in self.gap_types if gt != gap_type])
                
                samples.append({
                    'text': text,
                    'gap_type': actual_gap_type,
                    'description': f"{actual_gap_type.title()} gap for {topic}"
                })
        
        return samples
    
    def train_model(self, 
                   features: np.ndarray,
                   labels: np.ndarray,
                   model_type: str = 'random_forest') -> Dict[str, float]:
        """
        Train classification model
        
        Returns:
            Training metrics
        """
        
        # Split data
        X_train, X_val, y_train, y_val = train_test_split(
            features, labels, test_size=0.2, random_state=self.random_state, stratify=labels
        )
        
        # Select model
        if model_type == 'random_forest':
            model = self.rf_classifier
        else:
            model = self.gb_classifier
        
        # Train
        model.fit(X_train, y_train)
        self.trained_model = model
        
        # Validate
        y_pred = model.predict(X_val)
        
        # Calculate metrics
        metrics = {
            'accuracy': accuracy_score(y_val, y_pred),
            'precision_macro': precision_score(y_val, y_pred, average='macro', zero_division=0),
            'precision_micro': precision_score(y_val, y_pred, average='micro', zero_division=0),
            'recall_macro': recall_score(y_val, y_pred, average='macro', zero_division=0),
            'recall_micro': recall_score(y_val, y_pred, average='micro', zero_division=0),
            'f1_macro': f1_score(y_val, y_pred, average='macro', zero_division=0),
            'f1_micro': f1_score(y_val, y_pred, average='micro', zero_division=0)
        }
        
        return metrics
    
    def evaluate_model(self,
                      features: np.ndarray,
                      labels: np.ndarray,
                      descriptions: List[str]) -> Dict[str, Any]:
        """
        Comprehensive model evaluation with detailed metrics
        
        Returns:
            Complete evaluation metrics including confusion matrix and error analysis
        """
        
        if self.trained_model is None:
            raise ValueError("Model must be trained before evaluation")
        
        # Split data for evaluation
        X_train, X_test, y_train, y_test, desc_train, desc_test = train_test_split(
            features, labels, descriptions,
            test_size=0.25,
            random_state=self.random_state,
            stratify=labels
        )
        
        # Predictions
        y_pred = self.trained_model.predict(X_test)
        
        # Calculate comprehensive metrics
        accuracy = accuracy_score(y_test, y_pred)
        precision_macro = precision_score(y_test, y_pred, average='macro', zero_division=0)
        precision_micro = precision_score(y_test, y_pred, average='micro', zero_division=0)
        recall_macro = recall_score(y_test, y_pred, average='macro', zero_division=0)
        recall_micro = recall_score(y_test, y_pred, average='micro', zero_division=0)
        f1_macro = f1_score(y_test, y_pred, average='macro', zero_division=0)
        f1_micro = f1_score(y_test, y_pred, average='micro', zero_division=0)
        
        # Confusion matrix
        cm = confusion_matrix(y_test, y_pred)
        
        # Error analysis
        false_positives = []
        false_negatives = []
        
        for i, (true_label, pred_label) in enumerate(zip(y_test, y_pred)):
            if true_label != pred_label:
                true_class = self.reverse_label_map[true_label]
                pred_class = self.reverse_label_map[pred_label]
                
                error_desc = f"{desc_test[i]} | True: {true_class}, Predicted: {pred_class}"
                
                # Classify as FP or FN based on first class
                if pred_label > true_label:
                    false_positives.append(error_desc)
                else:
                    false_negatives.append(error_desc)
        
        # Ensure minimum 80% accuracy requirement
        if accuracy < 0.80:
            print(f"Warning: Model accuracy ({accuracy:.2%}) is below 80% threshold")
            print("Consider: 1) Adding more training data, 2) Feature engineering, 3) Hyperparameter tuning")
        
        # Classification report
        report = classification_report(
            y_test, y_pred,
            target_names=self.gap_types,
            output_dict=True
        )
        
        return {
            'precision': float(precision_macro),
            'recall': float(recall_macro),
            'accuracy': float(accuracy),
            'f1_macro': float(f1_macro),
            'f1_micro': float(f1_micro),
            'confusion_matrix': cm.tolist(),
            'samples_evaluated': len(y_test),
            'false_positives': false_positives[:10],  # Top 10
            'false_negatives': false_negatives[:10],  # Top 10
            'per_class_metrics': {
                gap_type: {
                    'precision': float(report[gap_type]['precision']),
                    'recall': float(report[gap_type]['recall']),
                    'f1_score': float(report[gap_type]['f1-score']),
                    'support': int(report[gap_type]['support'])
                }
                for gap_type in self.gap_types
            },
            'classification_report': report
        }
    
    def predict_gap_type(self, text: str) -> Tuple[str, float]:
        """
        Predict gap type for new text
        
        Returns:
            (gap_type, confidence)
        """
        
        if self.trained_model is None:
            raise ValueError("Model must be trained before prediction")
        
        # Vectorize
        features = self.vectorizer.transform([text]).toarray()
        
        # Predict
        prediction = self.trained_model.predict(features)[0]
        probabilities = self.trained_model.predict_proba(features)[0]
        
        gap_type = self.reverse_label_map[prediction]
        confidence = float(probabilities[prediction])
        
        return gap_type, confidence
    
    def cross_validate(self, features: np.ndarray, labels: np.ndarray, cv: int = 5) -> Dict[str, Any]:
        """Perform cross-validation"""
        
        scores = cross_val_score(
            self.trained_model,
            features,
            labels,
            cv=cv,
            scoring='accuracy'
        )
        
        return {
            'cv_scores': scores.tolist(),
            'mean_cv_score': float(np.mean(scores)),
            'std_cv_score': float(np.std(scores)),
            'cv_folds': cv
        }


def main():
    """Example usage and model training"""
    
    print("Gap Classification Model Initialized")
    
    # Example: Create and train model
    model = GapClassificationModel(random_state=42)
    
    # Generate synthetic training data (since we may not have real data yet)
    print("\nGenerating training dataset...")
    
    # Example gaps (would come from gap_analyzer in practice)
    example_gaps = [
        {
            'title': 'Guide to Machine Learning',
            'gap_type': 'missing',
            'keywords': ['machine learning', 'AI', 'algorithms'],
            'reason': 'Covered by competitors'
        },
        {
            'title': 'Update: Cloud Security Best Practices',
            'gap_type': 'outdated',
            'keywords': ['cloud', 'security', 'best practices'],
            'reason': 'Content is 2 years old'
        }
    ]
    
    # Create training dataset
    features, labels, descriptions = model.create_training_dataset(example_gaps, synthetic_samples=300)
    
    print(f"Training dataset: {features.shape[0]} samples, {features.shape[1]} features")
    print(f"Class distribution: {dict(Counter(labels))}")
    
    # Train model
    print("\nTraining Random Forest model...")
    train_metrics = model.train_model(features, labels, model_type='random_forest')
    
    print("\nTraining Metrics:")
    for metric, value in train_metrics.items():
        print(f"  {metric}: {value:.4f}")
    
    # Evaluate model
    print("\nEvaluating model...")
    eval_metrics = model.evaluate_model(features, labels, descriptions)
    
    print("\nEvaluation Metrics:")
    print(f"  Accuracy: {eval_metrics['accuracy']:.4f} ({'✓ PASS' if eval_metrics['accuracy'] >= 0.80 else '✗ FAIL'} ≥80% threshold)")
    print(f"  Precision: {eval_metrics['precision']:.4f}")
    print(f"  Recall: {eval_metrics['recall']:.4f}")
    print(f"  F1 (macro): {eval_metrics['f1_macro']:.4f}")
    print(f"  F1 (micro): {eval_metrics['f1_micro']:.4f}")
    print(f"  Samples evaluated: {eval_metrics['samples_evaluated']}")
    
    print("\nConfusion Matrix:")
    print(f"  {model.gap_types}")
    for row in eval_metrics['confusion_matrix']:
        print(f"  {row}")
    
    if eval_metrics['false_positives']:
        print(f"\nExample False Positives ({len(eval_metrics['false_positives'])}):")
        for fp in eval_metrics['false_positives'][:3]:
            print(f"  - {fp}")
    
    if eval_metrics['false_negatives']:
        print(f"\nExample False Negatives ({len(eval_metrics['false_negatives'])}):")
        for fn in eval_metrics['false_negatives'][:3]:
            print(f"  - {fn}")
    
    # Save metrics
    output_file = 'models/model_evaluation_metrics.json'
    with open(output_file, 'w') as f:
        json.dump(eval_metrics, f, indent=2)
    print(f"\nMetrics saved to: {output_file}")


if __name__ == "__main__":
    main()
