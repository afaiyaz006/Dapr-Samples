from fastapi import FastAPI, Request
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
    computation: float

@app.post("/process")
async def process(request: ProcessRequest):
    # Your business logic here
    computation = len(request.value) * 2.5  # Example calculation
    
    return ProcessResponse(
        processed_by="service-b",
        input_data=request.model_dump(),
        result=f"Service B computed result for: {request.value}",
        computation=computation
    )

@app.post("/process2")
async def dummy_post(request: Request):
    data= await request.body()
    print(data) 
    return {"received_data": data}
@app.get("/health")
async def health():
    return {"status": "healthy", "service": "service-b"}