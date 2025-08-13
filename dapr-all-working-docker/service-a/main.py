from fastapi import FastAPI
from pydantic import BaseModel
from typing import Any, Dict

app = FastAPI()
class ProcessRequest(BaseModel):
    value: str
    metadata: Dict[str, Any] = {}

class ProcessResponse(BaseModel):
    processed_by: str
    input_data: Dict[str, Any]
    result: str
    status: str

@app.post("/process", response_model=ProcessResponse)
async def process(request):
    # Your business logic here
    processed_result = f"Service A processed: {request.value}"
    
    return ProcessResponse(
        processed_by="service-a",
        input_data=request.model_dump(),
        result=processed_result,
        status="success"
    )

@app.get("/health")
async def health():
    return {"status": "healthy", "service": "service-a"}
