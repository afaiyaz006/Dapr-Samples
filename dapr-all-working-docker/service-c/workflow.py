
from dapr.ext.workflow import (
    WorkflowRuntime,
    DaprWorkflowContext,
    WorkflowActivityContext,
    RetryPolicy,
    DaprWorkflowClient,
    when_any,
)
from dapr.clients import DaprClient
from pydantic import BaseModel
import json

# Workflow app
wfr = WorkflowRuntime()
wfr.start()
class WorkflowInput(BaseModel):
    value: str
    metadata: dict = {}

@wfr.workflow(name="distributed_workflow")
def distributed_workflow(ctx: DaprWorkflowContext, input_data):
    """Main distributed workflow that calls Service A and Service B"""
    
    # Call Service A and B in parallel
    yield ctx.call_activity(activity=call_service_a,input= "A")
    yield ctx.call_activity(activity=call_service_b, input="B")

    

@wfr.activity(name="Task1")
async def call_service_a(ctx:WorkflowActivityContext,wf_input):
    """Activity to call Service A"""
    print(f"Context {ctx.task_id} --> Input: {wf_input}")
    with DaprClient() as client:
        response =await client.invoke_method_async(
            app_id="service-a",
            method_name="process",
            data="DATA",
            http_verb="POST"
        )
        return response.json()

@wfr.activity(name="Task2")
async def  call_service_b(ctx:WorkflowActivityContext,wf_input):
    
    """Activity to call Service B"""
    print(f"Context {ctx.task_id} --> Input: {wf_input}")
    with DaprClient() as client:
        response =await client.invoke_method(
            app_id="service-b", 
            method_name="process2",
            data="DATA",
            http_verb="POST"
        )
        


@wfr.activity
def call_service_c(input_data):
    """Activity to call Service C (itself) for final processing"""
    with DaprClient() as client:
        response = client.invoke_method(
            app_id="service-c",
            method_name="process",
            data=json.dumps({
                "value": f"Combined results: A={input_data['service_a_result']['result']}, B={input_data['service_b_result']['result']}",
                "metadata": input_data
            }),
            http_verb="POST"
        )
        client.publish_event()
        
        return response.json()


