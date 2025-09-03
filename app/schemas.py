from pydantic import BaseModel
from typing import Optional, List

class ClassificationResult(BaseModel):
    category: str
    confidence: float
    keywords: List[str]
    used_ai: bool
    model: str
    reply: str
