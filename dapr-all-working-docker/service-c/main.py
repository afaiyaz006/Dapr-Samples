from fastapi import FastAPI
from typing import Any, Dict, Optional
from dapr.ext.workflow import DaprWorkflowClient
from pydantic import BaseModel
from workflow import distributed_workflow,wfr
from time import sleep
from dapr.clients import DaprClient
app = FastAPI(title="Service C - Workflow Controller", version="2.0.0")
# Models
class ProcessRequest(BaseModel):
    value: str
    metadata: Dict[str, Any] = {}

class ProcessResponse(BaseModel):
    processed_by: str
    input_data: Dict[str, Any]
    result: str
    status: str

class WorkflowRequest(BaseModel):
    value: str
    metadata: Dict[str, Any] = {}

class WorkflowResponse(BaseModel):
    workflow_id: str
    status: str
    message: str

class WorkflowStatus(BaseModel):
    workflow_id: str
    status: str
    result: Optional[Dict[str, Any]] = None
    error: Optional[str] = None

@app.post("/start-workflow", response_model=WorkflowResponse)
def start_workflow(request: WorkflowRequest):
    print("Starting workflow...")
    wfClient = DaprWorkflowClient()
    print(wfClient)
    instance_id=wfClient.schedule_new_workflow(
        workflow=distributed_workflow,
        input="A"
    )
    wfClient.wait_for_workflow_completion(instance_id=instance_id)
    wfClient.terminate_workflow(instance_id=instance_id)
    return WorkflowResponse(
        workflow_id=instance_id,
        status="started",
        message=f"Workflow {instance_id} started successfully"
    )

@app.get("/call-service-b")
def call_service_b():
    with DaprClient() as client:
        response = client.invoke_method(
            app_id="service-b",
            method_name="process2",
            data="DATA",
            http_verb="POST"
        )
        client
        return response.json()
