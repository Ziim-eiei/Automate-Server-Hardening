from fastapi import APIRouter, status, Path, HTTPException
from dotenv import dotenv_values
from pymongo import MongoClient
from fastapi.encoders import jsonable_encoder
from models import *
from typing import List
from bson.objectid import ObjectId
from routers.server import delete_server

router = APIRouter(prefix="/api")
config = dotenv_values(".env")


@router.get("/projects", status_code=status.HTTP_200_OK, response_model=List[Project])
async def list_all_project():
    monogo_client = MongoClient(config["MONGODB_URI"])[config["DB_NAME"]]["project"]
    projects = list(monogo_client.find().limit(10))
    for p in projects:
        monogo_client = MongoClient(config["MONGODB_URI"])[config["DB_NAME"]]["server"]
        servers = list(monogo_client.find({"project_id": f"{p['_id']}"}))
        p["server"] = servers
    return projects


@router.get(
    "/projects/{project_id}", status_code=status.HTTP_200_OK, response_model=Project
)
async def list_project(project_id: Annotated[str, Path(...)]):
    monogo_client = MongoClient(config["MONGODB_URI"])[config["DB_NAME"]]["project"]
    project = monogo_client.find_one({"_id": ObjectId(project_id)})
    monogo_client = MongoClient(config["MONGODB_URI"])[config["DB_NAME"]]["server"]
    servers = list(monogo_client.find({"project_id": f"{project['_id']}"}))
    if servers == None:
        raise HTTPException(status_code=404, detail="not found")
    project["server"] = servers
    return project


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
    monogo_client = MongoClient(config["MONGODB_URI"])[config["DB_NAME"]]["server"]
    servers = list(monogo_client.find({"project_id": project_id}))
    for s in servers:
        await delete_server(s["_id"])
    return {"msg": f"{project_id} deleted"}
