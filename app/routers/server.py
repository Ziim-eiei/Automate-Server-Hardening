from fastapi import APIRouter, status, Path, HTTPException
from dotenv import dotenv_values
from pymongo import MongoClient
from jinja2 import Environment, FileSystemLoader
from fastapi.encoders import jsonable_encoder
from models import *
from typing import List
from bson.objectid import ObjectId
import os, shutil

router = APIRouter(prefix="/api")
config = dotenv_values(".env")


@router.get("/servers", response_model=List[Server])
async def list_all_server():
    monogo_client = MongoClient(config["MONGODB_URI"])[config["DB_NAME"]]["server"]
    servers = list(monogo_client.find())
    return servers


@router.get("/servers/{server_id}", response_model=Server)
async def list_server(server_id: Annotated[str, Path(...)]):
    monogo_client = MongoClient(config["MONGODB_URI"])[config["DB_NAME"]]["server"]
    result = monogo_client.find_one(ObjectId(server_id))
    return result


@router.post("/servers", status_code=status.HTTP_201_CREATED, response_model=Server)
async def create_server(body: Server):
    env = Environment(loader=FileSystemLoader("./templates/cis"))
    template = env.get_template("hosts.j2")
    body_json = jsonable_encoder(body)
    render_file = template.render(body_json)
    monogo_client = MongoClient(config["MONGODB_URI"])[config["DB_NAME"]]["server"]
    result = monogo_client.insert_one(jsonable_encoder(body, exclude_none=True))
    body = body.model_dump()
    body["_id"] = result.inserted_id
    monogo_client = MongoClient(config["MONGODB_URI"])[config["DB_NAME"]]["project"]
    result = monogo_client.find_one(ObjectId(body["project_id"]))
    path = f"./job/{str(body['_id'])}"
    os.makedirs(path)
    os.mkdir(path + "/hardening")
    os.mkdir(path + "/audit")
    os.mkdir(path + "/hardening/vars")
    with open(f"{path}/hosts", "w") as file:
        file.write(render_file)
    shutil.copytree("./templates/cis/audit/tasks", path + "/audit/tasks")
    shutil.copytree("./templates/cis/hardening/tasks", path + "/hardening/tasks")
    monogo_client = MongoClient(config["MONGODB_URI"])[config["DB_NAME"]]["server"]
    myquery = {"_id": ObjectId(body["_id"])}
    newvalues = {
        "$set": {
            "path": path,
        }
    }
    monogo_client.update_one(myquery, newvalues)
    return body


@router.patch("/servers/{server_id}", response_model=ServerUpdate)
async def update_server(server_id: Annotated[str, Path(...)], body: ServerUpdate):
    monogo_client = MongoClient(config["MONGODB_URI"])[config["DB_NAME"]]["server"]
    result = monogo_client.find_one(ObjectId(server_id))
    if result == None:
        raise HTTPException(status_code=404, detail="not found")
    body = body.model_dump()
    if body["server_ip"] == "":
        body["server_ip"] = result["server_ip"]
    if body["server_username"] == "":
        body["server_username"] = result["server_username"]
    if body["server_password"] == "":
        body["server_password"] = result["server_password"]
    myquery = {"_id": ObjectId(server_id)}
    newvalues = {
        "$set": {
            "server_ip": body["server_ip"],
            "server_username": body["server_username"],
            "server_password": body["server_password"],
        }
    }
    monogo_client.update_one(myquery, newvalues)
    return body


@router.delete("/servers/{server_id}")
async def delete_server(server_id: Annotated[str, Path(...)]):
    monogo_client = MongoClient(config["MONGODB_URI"])[config["DB_NAME"]]["server"]
    result = monogo_client.find_one(ObjectId(server_id))
    shutil.rmtree(result["path"])
    result = monogo_client.delete_one({"_id": ObjectId(server_id)})
    return {"msg": f"{server_id} deleted"}
