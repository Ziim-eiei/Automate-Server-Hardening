from fastapi import APIRouter, status, Path
from dotenv import dotenv_values
from pymongo import MongoClient
from fastapi.encoders import jsonable_encoder
from models import *
from typing import List
from bson.objectid import ObjectId

router = APIRouter(prefix="/api")
config = dotenv_values(".env")


@router.get("/projects", status_code=status.HTTP_200_OK, response_model=List[Project])
async def list_project():
    monogo_client = MongoClient(config["MONGODB_URI"])[config["DB_NAME"]]["project"]
    projects = list(monogo_client.find().limit(10))
    for p in projects:
        monogo_client = MongoClient(config["MONGODB_URI"])[config["DB_NAME"]]["server"]
        servers = list(monogo_client.find({"project_id": f"{p['_id']}"}))
        p["server"] = servers
    return projects


@router.post("/projects", status_code=status.HTTP_201_CREATED, response_model=Project)
async def create_project(body: Project):
    body = body.model_dump()
    body["created_at"] = datetime.datetime.now(tz=datetime.timezone.utc)
    monogo_client = MongoClient(config["MONGODB_URI"])[config["DB_NAME"]]["project"]
    result = monogo_client.insert_one(jsonable_encoder(body, exclude_none=True))
    body["_id"] = result.inserted_id
    return body


# @router.delete("/projects")
# async def delete_project():
#     monogo_client = MongoClient(config["MONGODB_URI"])[config["DB_NAME"]]["project"]
#     result = monogo_client.drop()
#     return {"msg": "delete all project"}


@router.delete("/projects/{project_id}")
async def delete_project(project_id: Annotated[str, Path(...)]):
    monogo_client = MongoClient(config["MONGODB_URI"])[config["DB_NAME"]]["project"]
    result = monogo_client.delete_one({"_id": ObjectId(project_id)})
    return {"msg": f"{project_id} deleted"}
