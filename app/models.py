from pydantic import BaseModel
from typing import List

class EmailInput(BaseModel):
    content: str

class EmailBatchInput(BaseModel):
    emails: List[str]

class ClassificationResult(BaseModel):
    email: str
    tags: List[str]

class BatchClassificationResult(BaseModel):
    results: List[ClassificationResult]
