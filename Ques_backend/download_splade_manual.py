"""
Manual SPLADE Model Download and Setup
Alternative methods to access SPLADE model without HuggingFace login
"""
import os
import requests
from pathlib import Path

def method_1_git_clone():
    """
    Method 1: Git Clone (if you have access)
    Clone the repository directly using git
    """
    print("Method 1: Git Clone")
    print("=" * 50)
    
    model_dir = Path("./models/splade-v3")
    
    print("1. First, request access to the model at:")
    print("   https://huggingface.co/naver/splade-v3")
    print()
    print("2. Then clone using git:")
    print(f"   git clone https://huggingface.co/naver/splade-v3 {model_dir}")
    print()
    print("3. Use local path in code:")
    print(f"   model = AutoModelForMaskedLM.from_pretrained('{model_dir}')")
    print()

def method_2_manual_download():
    """
    Method 2: Manual file download
    Download required files individually
    """
    print("Method 2: Manual Download")
    print("=" * 50)
    
    base_url = "https://huggingface.co/naver/splade-v3/resolve/main"
    files_needed = [
        "config.json",
        "pytorch_model.bin",
        "tokenizer.json", 
        "tokenizer_config.json",
        "vocab.txt"
    ]
    
    model_dir = Path("./models/splade-v3")
    model_dir.mkdir(parents=True, exist_ok=True)
    
    print("Required files to download manually:")
    for file in files_needed:
        url = f"{base_url}/{file}"
        print(f"   {url}")
        print(f"   -> save to: {model_dir}/{file}")
    print()
    print("After downloading all files, use:")
    print(f"   model = AutoModelForMaskedLM.from_pretrained('{model_dir}')")
    print()

def method_3_alternative_models():
    """
    Method 3: Use alternative SPLADE models
    Some SPLADE models might not be gated
    """
    print("Method 3: Alternative SPLADE Models")
    print("=" * 50)
    
    alternatives = [
        "naver/splade-cocondenser-ensembledistil",
        "naver/splade-cocondenser-selfdistil", 
        "naver/splade_v2_max",
        "naver/splade_v2_distil",
        "sentence-transformers/msmarco-distilbert-base-tas-b"  # Similar sparse approach
    ]
    
    print("Try these alternative models (might not be gated):")
    for model in alternatives:
        print(f"   {model}")
    print()
    print("Test with:")
    print("   from transformers import AutoModelForMaskedLM, AutoTokenizer")
    print("   model = AutoModelForMaskedLM.from_pretrained('naver/splade_v2_max')")
    print()

def method_4_local_implementation():
    """
    Method 4: Implement your own sparse vector generator
    Create a custom SPLADE-like implementation
    """
    print("Method 4: Custom Sparse Vector Implementation")
    print("=" * 50)
    
    implementation = '''
import torch
import torch.nn.functional as F
from transformers import AutoTokenizer, AutoModel
from sklearn.feature_extraction.text import TfidfVectorizer
import numpy as np

class CustomSparseEncoder:
    def __init__(self):
        # Use a non-gated BERT model
        self.tokenizer = AutoTokenizer.from_pretrained('bert-base-uncased')
        self.model = AutoModel.from_pretrained('bert-base-uncased')
        
    def encode_sparse(self, text):
        """Generate sparse representation similar to SPLADE"""
        inputs = self.tokenizer(text, return_tensors='pt', padding=True, truncation=True)
        
        with torch.no_grad():
            outputs = self.model(**inputs)
            # Use attention weights to create sparse representation
            attention = outputs.attentions[-1].mean(dim=1).mean(dim=1)  # Average attention
            
            # Convert to sparse dict
            tokens = self.tokenizer.convert_ids_to_tokens(inputs['input_ids'][0])
            sparse_dict = {}
            
            for i, (token, weight) in enumerate(zip(tokens, attention[0])):
                if token not in ['[CLS]', '[SEP]', '[PAD]'] and weight > 0.1:
                    sparse_dict[token] = float(weight)
            
            return sparse_dict

# Usage:
encoder = CustomSparseEncoder()
sparse_vector = encoder.encode_sparse("machine learning student")
print(sparse_vector)
'''
    
    print("Custom implementation code:")
    print(implementation)

def method_5_test_alternatives():
    """
    Method 5: Test which models are accessible
    """
    print("Method 5: Test Model Accessibility")
    print("=" * 50)
    
    models_to_test = [
        "naver/splade_v2_max",
        "naver/splade_v2_distil", 
        "naver/splade-cocondenser-ensembledistil",
        "distilbert-base-uncased",  # Fallback for custom implementation
    ]
    
    print("Testing model accessibility...")
    
    try:
        from transformers import AutoTokenizer, AutoModelForMaskedLM
        
        for model_name in models_to_test:
            try:
                print(f"\n  Testing: {model_name}")
                tokenizer = AutoTokenizer.from_pretrained(model_name)
                model = AutoModelForMaskedLM.from_pretrained(model_name)
                print(f"  ✅ {model_name} - ACCESSIBLE")
                
                # Test encoding
                inputs = tokenizer("test query", return_tensors="pt")
                outputs = model(**inputs)
                print(f"     Model loaded successfully, output shape: {outputs.logits.shape}")
                
            except Exception as e:
                if "gated" in str(e).lower() or "restricted" in str(e).lower():
                    print(f"  🔒 {model_name} - GATED/RESTRICTED")
                else:
                    print(f"  ❌ {model_name} - ERROR: {str(e)[:50]}...")
                    
    except ImportError:
        print("  ⚠️  transformers library not installed")
        print("  Install with: pip install transformers")

if __name__ == "__main__":
    print("SPLADE Model Access Alternatives")
    print("=" * 80)
    print()
    
    method_1_git_clone()
    print()
    method_2_manual_download()
    print()
    method_3_alternative_models()
    print()
    method_4_local_implementation()
    print()
    method_5_test_alternatives()