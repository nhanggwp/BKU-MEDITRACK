"""
DDI API Service using FastAPI
"""
import os
from typing import List, Dict, Optional
from fastapi import FastAPI, HTTPException, BackgroundTasks
from pydantic import BaseModel
import logging
import asyncio

from src.inference import DDIPredictor
from src.drug_lookup import drug_name_to_smiles, drug_names_to_smiles_batch

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="Drug-Drug Interaction Prediction API",
    description="API for predicting drug-drug interactions using deep learning",
    version="1.0.0"
)

# Global predictor instance
predictor: Optional[DDIPredictor] = None

# Pydantic models for request/response
class DrugPair(BaseModel):
    drug1_smiles: str
    drug2_smiles: str

class BatchPredictionRequest(BaseModel):
    drug_pairs: List[DrugPair]
    top_k: int = 5

class SinglePredictionRequest(BaseModel):
    drug1_smiles: str
    drug2_smiles: str
    top_k: int = 5

class SideEffectPrediction(BaseModel):
    side_effect: str
    probability: float
    index: int

class PredictionResponse(BaseModel):
    predictions: List[SideEffectPrediction]
    drug1_smiles: str
    drug2_smiles: str

class BatchPredictionResponse(BaseModel):
    results: List[PredictionResponse]

class HealthResponse(BaseModel):
    status: str
    message: str
    model_loaded: bool

# New models for drug name-based requests
class DrugPairByName(BaseModel):
    drug1_name: str
    drug2_name: str

class SinglePredictionByNameRequest(BaseModel):
    drug1_name: str
    drug2_name: str
    top_k: int = 5

class BatchPredictionByNameRequest(BaseModel):
    drug_pairs: List[DrugPairByName]
    top_k: int = 5

class PredictionByNameResponse(BaseModel):
    predictions: List[SideEffectPrediction]
    drug1_name: str
    drug2_name: str
    drug1_smiles: Optional[str]
    drug2_smiles: Optional[str]
    conversion_errors: List[str] = []

class BatchPredictionByNameResponse(BaseModel):
    results: List[PredictionByNameResponse]


@app.on_event("startup")
async def startup_event():
    """Initialize the DDI predictor on startup"""
    global predictor
    
    try:
        model_path = os.getenv("DDI_MODEL_PATH", "/app/models/best_ddi_model.pt")
        num_labels = int(os.getenv("NUM_LABELS", "1317"))  # TWOSIDES default
        
        logger.info(f"Loading DDI model from {model_path}")
        predictor = DDIPredictor(model_path)
        predictor.load_model(num_labels)
        logger.info("DDI model loaded successfully")
        
    except Exception as e:
        logger.error(f"Failed to load DDI model: {e}")
        # Don't fail startup, but model won't be available
        predictor = None


@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint"""
    model_loaded = predictor is not None and predictor.model is not None
    
    return HealthResponse(
        status="healthy" if model_loaded else "degraded",
        message="DDI service is running" if model_loaded else "DDI model not loaded",
        model_loaded=model_loaded
    )


@app.post("/predict", response_model=PredictionResponse)
async def predict_ddi(request: SinglePredictionRequest):
    """Predict drug-drug interactions for a single drug pair"""
    if predictor is None or predictor.model is None:
        raise HTTPException(
            status_code=503, 
            detail="DDI model not loaded. Please check service health."
        )
    
    try:
        predictions = predictor.predict(
            request.drug1_smiles, 
            request.drug2_smiles, 
            request.top_k
        )
        
        return PredictionResponse(
            predictions=[SideEffectPrediction(**pred) for pred in predictions],
            drug1_smiles=request.drug1_smiles,
            drug2_smiles=request.drug2_smiles
        )
        
    except Exception as e:
        logger.error(f"Prediction error: {e}")
        raise HTTPException(
            status_code=500, 
            detail=f"Prediction failed: {str(e)}"
        )


@app.post("/predict/by-name", response_model=PredictionByNameResponse)
async def predict_ddi_by_name(request: SinglePredictionByNameRequest):
    """Predict drug-drug interactions for a single drug pair using drug names"""
    if predictor is None or predictor.model is None:
        raise HTTPException(
            status_code=503, 
            detail="DDI model not loaded. Please check service health."
        )
    
    try:
        # Convert drug names to SMILES
        drug1_smiles = drug_name_to_smiles(request.drug1_name)
        drug2_smiles = drug_name_to_smiles(request.drug2_name)
        
        errors = []
        if drug1_smiles is None:
            errors.append(f"Could not find SMILES for drug: {request.drug1_name}")
        if drug2_smiles is None:
            errors.append(f"Could not find SMILES for drug: {request.drug2_name}")
        
        if drug1_smiles is None or drug2_smiles is None:
            return PredictionByNameResponse(
                predictions=[],
                drug1_name=request.drug1_name,
                drug2_name=request.drug2_name,
                drug1_smiles=drug1_smiles,
                drug2_smiles=drug2_smiles,
                conversion_errors=errors
            )
        
        # Make prediction using SMILES
        predictions = predictor.predict(drug1_smiles, drug2_smiles, request.top_k)
        
        return PredictionByNameResponse(
            predictions=[SideEffectPrediction(**pred) for pred in predictions],
            drug1_name=request.drug1_name,
            drug2_name=request.drug2_name,
            drug1_smiles=drug1_smiles,
            drug2_smiles=drug2_smiles,
            conversion_errors=errors
        )
        
    except Exception as e:
        logger.error(f"Prediction by name error: {e}")
        raise HTTPException(
            status_code=500, 
            detail=f"Prediction failed: {str(e)}"
        )


@app.post("/predict/batch", response_model=BatchPredictionResponse)
async def predict_ddi_batch(request: BatchPredictionRequest):
    """Predict drug-drug interactions for multiple drug pairs"""
    if predictor is None or predictor.model is None:
        raise HTTPException(
            status_code=503, 
            detail="DDI model not loaded. Please check service health."
        )
    
    try:
        # Convert to tuples for the predictor
        drug_pairs = [(pair.drug1_smiles, pair.drug2_smiles) for pair in request.drug_pairs]
        
        batch_predictions = predictor.predict_batch(drug_pairs, request.top_k)
        
        results = []
        for i, predictions in enumerate(batch_predictions):
            results.append(PredictionResponse(
                predictions=[SideEffectPrediction(**pred) for pred in predictions],
                drug1_smiles=request.drug_pairs[i].drug1_smiles,
                drug2_smiles=request.drug_pairs[i].drug2_smiles
            ))
        
        return BatchPredictionResponse(results=results)
        
    except Exception as e:
        logger.error(f"Batch prediction error: {e}")
        raise HTTPException(
            status_code=500, 
            detail=f"Batch prediction failed: {str(e)}"
        )


@app.post("/predict/batch/by-name", response_model=BatchPredictionByNameResponse)
async def predict_ddi_batch_by_name(request: BatchPredictionByNameRequest):
    """Predict drug-drug interactions for multiple drug pairs using drug names"""
    if predictor is None or predictor.model is None:
        raise HTTPException(
            status_code=503, 
            detail="DDI model not loaded. Please check service health."
        )
    
    try:
        # Extract drug names for batch conversion
        drug_names = []
        for pair in request.drug_pairs:
            drug_names.extend([pair.drug1_name, pair.drug2_name])
        
        # Remove duplicates while preserving order
        unique_drug_names = list(dict.fromkeys(drug_names))
        
        # Convert all drug names to SMILES asynchronously
        conversion_results = await drug_names_to_smiles_batch(unique_drug_names)
        name_to_smiles = dict(conversion_results)
        
        # Process each drug pair
        results = []
        for pair in request.drug_pairs:
            drug1_smiles = name_to_smiles.get(pair.drug1_name)
            drug2_smiles = name_to_smiles.get(pair.drug2_name)
            
            errors = []
            predictions = []
            
            if drug1_smiles is None:
                errors.append(f"Could not find SMILES for drug: {pair.drug1_name}")
            if drug2_smiles is None:
                errors.append(f"Could not find SMILES for drug: {pair.drug2_name}")
            
            # Only predict if both SMILES are available
            if drug1_smiles and drug2_smiles:
                try:
                    pred_results = predictor.predict(drug1_smiles, drug2_smiles, request.top_k)
                    predictions = [SideEffectPrediction(**pred) for pred in pred_results]
                except Exception as e:
                    errors.append(f"Prediction failed: {str(e)}")
            
            results.append(PredictionByNameResponse(
                predictions=predictions,
                drug1_name=pair.drug1_name,
                drug2_name=pair.drug2_name,
                drug1_smiles=drug1_smiles,
                drug2_smiles=drug2_smiles,
                conversion_errors=errors
            ))
        
        return BatchPredictionByNameResponse(results=results)
        
    except Exception as e:
        logger.error(f"Batch prediction by name error: {e}")
        raise HTTPException(
            status_code=500, 
            detail=f"Batch prediction failed: {str(e)}"
        )


@app.get("/")
async def root():
    """Root endpoint with basic info"""
    return {
        "message": "Drug-Drug Interaction Prediction API",
        "version": "1.0.0",
        "endpoints": {
            "health": "/health",
            "predict": "/predict",
            "predict_by_name": "/predict/by-name",
            "batch_predict": "/predict/batch",
            "batch_predict_by_name": "/predict/batch/by-name",
            "docs": "/docs"
        },
        "description": {
            "/predict": "Predict DDI using SMILES format",
            "/predict/by-name": "Predict DDI using drug names (converted to SMILES)",
            "/predict/batch": "Batch predict DDI using SMILES format",
            "/predict/batch/by-name": "Batch predict DDI using drug names (converted to SMILES)"
        }
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)