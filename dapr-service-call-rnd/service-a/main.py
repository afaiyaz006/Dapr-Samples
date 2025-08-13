from fastapi import FastAPI
from pydantic import BaseModel
from typing import List
from dapr.clients import DaprClient
import json
from dapr.ext.fastapi import DaprApp
app = FastAPI(title="Service-1 API")
dapr_app = DaprApp(app)
# --- Pydantic models ---
class Item(BaseModel):
    item_name: str
    item_price: str

class ShopListResponse(BaseModel):
    shop_list: List[Item]

dummy_database = ShopListResponse(
    shop_list=[
        Item(item_name="Mango", item_price="2$")
    ]
)
class News(BaseModel):
    new_title: str
    news_details: str
class CloudEventModel(BaseModel):
    data: List[News]
    datacontenttype: str
    id: str
    pubsubname: str
    source: str
    specversion: str
    topic: str
    traceid: str
    traceparent: str
    tracestate: str
    type: str

# --- routes ---
@app.get("/")
def read_root():
    return {"message": "Hello from Service-1!"}

@app.get("/get-list", response_model=ShopListResponse)
def get_data():
    return dummy_database

@app.post("/add-item")
async def add_item(request: Item):
    dummy_database.shop_list.append(request)
    print(request.model_dump_json())
    with DaprClient() as d:
        response =await d.invoke_method_async(
            app_id="service-b",
            method_name="update-list",
            data = request.model_dump_json(),
            http_verb="POST"
        )
    return {
        "added": request, 
        "current_list": dummy_database,
        "remote":str(response.json())
    }
@app.post("/update-list")
async def add_item(request: Item):
    dummy_database.shop_list.append(request)
    
    return {
        "added": request, 
        "current_list": dummy_database,
    }


@app.post("/publish-news")
def add_news(request:News):
    with DaprClient() as d:
        d.publish_event(
            pubsub_name='pubsub-rabbitmq',
            topic_name="news",
            data = request.model_dump_json(),
            data_content_type='application/json'
        )
    return {
        "published":True
    }


@dapr_app.subscribe(pubsub="pubsub-rabbitmq",topic="news_published")
def news_published_confirmation(request:CloudEventModel):
    print("News published confirmed....")
    print(request)