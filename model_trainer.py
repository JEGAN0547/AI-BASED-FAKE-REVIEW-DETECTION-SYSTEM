"""
AI-Based Fake Review Detection System
Python Machine Learning Model Trainer (Scikit-Learn TF-IDF + Logistic Regression)
"""

import json
import re
import os
from typing import List, Dict, Tuple

try:
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.linear_model import LogisticRegression
    from sklearn.model_selection import train_test_split
    from sklearn.metrics import classification_report, confusion_matrix
    SKLEARN_AVAILABLE = True
except ImportError:
    SKLEARN_AVAILABLE = False


class FakeReviewModelTrainer:
    def __init__(self):
        self.vectorizer = None
        self.model = None
        
    def load_dataset(self, filepath: str) -> Tuple[List[str], List[int]]:
        """Load and extract text and labels from sample_reviews.json"""
        if not os.path.exists(filepath):
            raise FileNotFoundError(f"Dataset file not found at {filepath}")
            
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
            
        texts = []
        labels = []
        for item in data:
            texts.append(item.get("text", ""))
            # label "fake" -> 1, "authentic" -> 0
            labels.append(1 if item.get("label") == "fake" else 0)
            
        return texts, labels

    def train_and_evaluate(self, texts: List[str], labels: List[int]) -> Dict:
        """Train TF-IDF + Logistic Regression Model"""
        if not SKLEARN_AVAILABLE:
            print("scikit-learn is not installed. Install via pip install scikit-learn pandas")
            return {"error": "scikit-learn not installed"}

        if len(texts) < 4:
            print("Dataset too small for train/test split. Using full dataset for demo fit.")
            X_train, X_test, y_train, y_test = texts, texts, labels, labels
        else:
            X_train, X_test, y_train, y_test = train_test_split(
                texts, labels, test_size=0.25, random_state=42, stratify=labels if len(set(labels)) > 1 else None
            )

        # Build TF-IDF Pipeline
        self.vectorizer = TfidfVectorizer(
            ngram_range=(1, 2),
            max_features=1000,
            stop_words='english'
        )
        
        X_train_vec = self.vectorizer.fit_transform(X_train)
        X_test_vec = self.vectorizer.transform(X_test)

        self.model = LogisticRegression(C=1.0, random_state=42)
        self.model.fit(X_train_vec, y_train)

        predictions = self.model.predict(X_test_vec)
        report = classification_report(y_test, predictions, output_dict=True, zero_division=0)
        
        print("\n=== Model Training Performance Report ===")
        print(classification_report(y_test, predictions, zero_division=0))
        
        return {
            "status": "success",
            "train_samples": len(X_train),
            "test_samples": len(X_test),
            "vocabulary_size": len(self.vectorizer.vocabulary_),
            "metrics": report
        }


if __name__ == "__main__":
    dataset_path = os.path.join(os.path.dirname(__file__), "data", "sample_reviews.json")
    trainer = FakeReviewModelTrainer()
    if os.path.exists(dataset_path):
        texts, labels = trainer.load_dataset(dataset_path)
        trainer.train_and_evaluate(texts, labels)
    else:
        print(f"Dataset path {dataset_path} does not exist yet.")
