from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List
from dapr.clients import DaprClient
import json
from dapr.ext.fastapi import DaprApp
app = FastAPI(title="Service-2 API")
dapr_app = DaprApp(app)
# models
class Item(BaseModel):
    item_name: str
    item_price: str

class ShopListResponse(BaseModel):
    shop_list: List[Item]

# in-memory list
dummy_database = ShopListResponse(shop_list=[Item(item_name="Mango", item_price="2$")])
# for pubsub    

class News(BaseModel):
    new_title: str
    news_details: str

class NewsListResponse(BaseModel):
    news_list: List[News]

dummy_news_database = NewsListResponse(
    news_list=[
        News(new_title="Dummy News title",news_details="Dummy News Description")
    ]
)
class CloudEventModel(BaseModel):
    data: News
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
# routes
@app.get("/")
def read_root():
    return {"message": "Hello from Service-2!"}

@app.get("/get-list", response_model=ShopListResponse)
def get_data():
    return dummy_database

@app.post("/add-item")
async def add_item(request: Item):
    dummy_database.shop_list.append(request)
    print(request.model_dump_json())
    with DaprClient() as d:
        response =await d.invoke_method_async(
            app_id="service-a",
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

@dapr_app.subscribe(pubsub='pubsub-rabbitmq',topic='news')
def event_handler(news_publish_event: CloudEventModel):
    dummy_news_database.news_list.append(news_publish_event.data)
    print("News Recieved: ")
    print(news_publish_event)
    with DaprClient() as d:
        d.publish_event(
            pubsub_name="pubsub-rabbitmq",
            topic_name="news_published",
            data = json.dumps(dummy_news_database.model_dump()['news_list']),
            data_content_type='application/json'
        )

