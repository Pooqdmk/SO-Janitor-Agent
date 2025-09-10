# src/main.py

from fastapi import FastAPI
from pydantic import BaseModel
from typing import List
from pathlib import Path
import faiss
import pickle
from sentence_transformers import SentenceTransformer
import numpy as np
from contextlib import asynccontextmanager

# --- CONFIGURATION & Pydantic Models ---

# These constants define our "Confidence Zones" for scoring.
# You can tune these values to make the scores more or less strict.
HIGH_CONFIDENCE_DISTANCE = 0.3   # Anything below this distance is a very strong match.
MEDIUM_CONFIDENCE_DISTANCE = 1.0 # Distances between HIGH and MEDIUM are moderate matches.

class QuestionRequest(BaseModel):
    text: str
    top_k: int = 5

class SimilarQuestion(BaseModel):
    so_id: str
    distance: float
    similarity_percent: float
    link: str

class APIResponse(BaseModel):
    results: List[SimilarQuestion]


# --- Global State & Lifespan Manager for Model Loading ---
# We use a dictionary to hold our models. It will be populated on startup.
ml_models = {}

@asynccontextmanager
async def lifespan(app: FastAPI):
    # --- Code to run on startup ---
    print("🚀 Starting API server... Loading models into memory.")
    
    # --- Robust Pathing ---
    # Get the absolute path to the directory where this script is located
    SCRIPT_DIR = Path(__file__).parent.resolve()
    # Define model paths relative to the script's location
    models_dir = SCRIPT_DIR.parent / "models"
    
    faiss_index_path = models_dir / "faiss_index.bin"
    id_map_path = models_dir / "id_map.pkl"
    model_name = 'all-MiniLM-L6-v2'
    
    # Load all models and store them in the ml_models dictionary
    print("Step 1/3: Loading sentence-transformer model...")
    ml_models["sentence_transformer"] = SentenceTransformer(model_name)
    
    print(f"Step 2/3: Loading FAISS index from {faiss_index_path}...")
    ml_models["faiss_index"] = faiss.read_index(str(faiss_index_path))
    
    print(f"Step 3/3: Loading ID map from {id_map_path}...")
    with open(id_map_path, 'rb') as f:
        ml_models["id_map"] = pickle.load(f)

    print("✅ Models loaded successfully. API is ready!")
    
    yield
    
    # --- Code to run on shutdown (optional) ---
    print("Shutting down API server...")
    ml_models.clear()


# --- App Initialization with Lifespan ---
app = FastAPI(
    title="StackGuardian AI Search API",
    description="An API to find semantically similar questions from Stack Overflow.",
    version="1.0.0",
    lifespan=lifespan
)


# --- API Endpoint Definition ---
@app.post("/find_similar_questions", response_model=APIResponse)
def find_similar_questions(request: QuestionRequest):
    """
    Accepts a question text in a JSON body and returns the top_k most similar questions.
    """
    # Retrieve models from our global state
    model = ml_models["sentence_transformer"]
    index = ml_models["faiss_index"]
    id_map = ml_models["id_map"]

    query_embedding = model.encode([request.text])
    query_embedding = np.float32(query_embedding)

    distances, indices = index.search(query_embedding, request.top_k)

    results = []
    for i, idx in enumerate(indices[0]):
        so_id = str(id_map[idx])
        distance_score = float(distances[0][i])
        link = f"https://stackoverflow.com/q/{so_id}"

        # --- NEW: Advanced Multi-Stage Scoring Logic ---
        similarity_percent = 0.0
        if distance_score <= HIGH_CONFIDENCE_DISTANCE:
            # Scale from 90% to 100% for the best matches
            normalized_dist = distance_score / HIGH_CONFIDENCE_DISTANCE
            similarity_percent = 90 + (10 * (1 - normalized_dist))
        elif distance_score < MEDIUM_CONFIDENCE_DISTANCE:
            # Scale from 60% to 90% for moderate matches
            normalized_dist = (distance_score - HIGH_CONFIDENCE_DISTANCE) / (MEDIUM_CONFIDENCE_DISTANCE - HIGH_CONFIDENCE_DISTANCE)
            similarity_percent = 60 + (30 * (1 - normalized_dist))
        else:
            # Lower scores for less related items
            # This part can be adjusted for a steeper drop-off if needed
            normalized_dist = (distance_score - MEDIUM_CONFIDENCE_DISTANCE) / (1.5 - MEDIUM_CONFIDENCE_DISTANCE)
            similarity_percent = 30 + (30 * (1 - min(1, normalized_dist)))
        
        similarity_percent = round(max(0, similarity_percent), 2)
        # ----------------------------------------------------

        results.append(
            SimilarQuestion(
                so_id=so_id,
                distance=distance_score,
                similarity_percent=similarity_percent,
                link=link
            )
        )

    return APIResponse(results=results)

@app.get("/")
def read_root():
    return {"message": "Welcome to the StackGuardian AI API. Go to /docs to see the interactive API documentation."}

