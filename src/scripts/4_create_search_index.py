# src/scripts/4_create_search_index.py
import pandas as pd
from sentence_transformers import SentenceTransformer
import faiss
import numpy as np
import pickle
from pathlib import Path
import os
import torch  # <-- Added torch for GPU check

def create_search_index():
    """
    Loads the golden dataset, generates vector embeddings for each question,
    and builds a searchable FAISS index.
    """
    print("🚀 Starting the search index creation process...")

    # --- Configuration ---
    script_location = Path(__file__).resolve().parent
    root_directory = script_location.parent.parent
    
    input_parquet_file = root_directory / "data" / "processed" / "top_50_tags_golden_questions.parquet"
    models_dir = root_directory / "models"
    faiss_index_file = models_dir / "faiss_index.bin"
    id_map_file = models_dir / "id_map.pkl"
    
    # --- Pre-flight checks ---
    if not input_parquet_file.exists():
        print(f"❌ ERROR: Input Parquet file not found at {input_parquet_file}")
        return
    models_dir.mkdir(parents=True, exist_ok=True)

    # --- 1. Load the pre-trained model ---
    print("Step 1/5: Loading sentence-transformer model ('all-MiniLM-L6-v2')...")
    
    # --- CORRECTED GPU CHECK ---
    device = 'cuda' if torch.cuda.is_available() else 'cpu'
    print(f"  Using device: {device}")
    
    model = SentenceTransformer('all-MiniLM-L6-v2', device=device)

    # --- 2. Load the processed data ---
    print(f"Step 2/5: Loading data from {input_parquet_file}...")
    df = pd.read_parquet(input_parquet_file)
    df.dropna(subset=['Title', 'Body'], inplace=True)
    df['text_to_embed'] = df['Title'] + ". " + df['Body']
    print(f"  Data loaded. Found {len(df):,} questions to process.")

    # --- 3. Generate Embeddings ---
    print("Step 3/5: Generating embeddings for all questions... This is the longest step and will take a while.")
    question_embeddings = model.encode(df['text_to_embed'].tolist(), show_progress_bar=True, device=device)
    question_embeddings = np.float32(question_embeddings)

    # --- 4. Build the FAISS Index ---
    print("Step 4/5: Building the FAISS index...")
    embedding_dim = question_embeddings.shape[1]
    index = faiss.IndexFlatL2(embedding_dim)
    index.add(question_embeddings)
    print(f"  FAISS index built successfully. It contains {index.ntotal:,} vectors.")

    # --- 5. Save Everything ---
    print(f"Step 5/5: Saving the index and ID map to the '{models_dir}' directory...")
    faiss.write_index(index, str(faiss_index_file))
    
    id_map = df['Id'].tolist()
    with open(id_map_file, 'wb') as f:
        pickle.dump(id_map, f)

    print("\n" + "="*50)
    print("✅ All files saved successfully! Your search engine is ready to be used.")
    print("="*50)

if __name__ == "__main__":
    create_search_index()
