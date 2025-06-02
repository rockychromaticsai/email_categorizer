# app/main.py
from fastapi import FastAPI, Request
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
import pandas as pd
from io import StringIO
import logging
from typing import Dict, List, Optional

from .models import EmailInput, EmailBatchInput, ClassificationResult, BatchClassificationResult
from .services.classifier import EmailClassifier

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Email Categorizer")
templates = Jinja2Templates(directory="app/templates")
classifier = EmailClassifier()

# Temporary storage for batch results
last_batch_results: Optional[BatchClassificationResult] = None

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/classify", response_model=ClassificationResult)
async def classify_email(email: EmailInput):
    result = await classifier.classify_email(email.content)
    return ClassificationResult(email=email.content, tags=result["tags"])

@app.post("/classify-batch", response_model=BatchClassificationResult)
async def classify_emails(batch: EmailBatchInput):
    global last_batch_results
    results = await classifier.classify_emails(batch.emails)
    last_batch_results = BatchClassificationResult(
        results=[
            ClassificationResult(email=email, tags=result["tags"])
            for email, result in zip(batch.emails, results)
        ]
    )
    return last_batch_results

@app.post("/export-csv")
async def export_csv(batch: EmailBatchInput):
    global last_batch_results
    
    # If we have stored results and the emails match, use them
    if last_batch_results and len(last_batch_results.results) == len(batch.emails):
        # Verify the emails match
        stored_emails = [r.email for r in last_batch_results.results]
        if stored_emails == batch.emails:
            logger.info("Using stored batch results for CSV export")
            results_to_use = last_batch_results
        else:
            # If emails don't match, get new classification
            results_to_use = await classify_emails(batch)
    else:
        # If no stored results, get new classification
        results_to_use = await classify_emails(batch)
    
    # Create DataFrame from the results
    df = pd.DataFrame([
        {
            "Email": result.email,
            "Tags": ", ".join(result.tags)
        }
        for result in results_to_use.results
    ])
    
    # Convert to CSV
    csv = StringIO()
    df.to_csv(csv, index=False)
    
    return {"csv": csv.getvalue()}
