from fastapi import APIRouter, status, Path, Query
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
async def list_server():
    monogo_client = MongoClient(config["MONGODB_URI"])[config["DB_NAME"]]["server"]
    servers = list(monogo_client.find().limit(10))
    return servers


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
    path = f"./job/{result['project_name'] +'_'+ str(body['_id'])}"
    os.makedirs(path)
    os.mkdir(path + "/hardening")
    os.mkdir(path + "/audit")
    os.mkdir(path + "/hardening/vars")
    with open(f"{path}/hosts", "w") as file:
        file.write(render_file)
    monogo_client = MongoClient(config["MONGODB_URI"])[config["DB_NAME"]][
        "hardening_job"
    ]
    shutil.copytree("./templates/cis/audit/tasks", path + "/audit/tasks")
    shutil.copytree("./templates/cis/hardening/tasks", path + "/hardening/tasks")
    result = monogo_client.insert_one(
        {"server_id": body["_id"], "path": path, "status": "not running"}
    )
    return body


@router.post("/jobs")
async def create_job(job: Job):
    job = jsonable_encoder(job)
    # print(job)
    return {"msg": f"{job}"}


@router.delete("/servers")
async def delete_all_server():
    monogo_client = MongoClient(config["MONGODB_URI"])[config["DB_NAME"]]["server"]
    result = monogo_client.drop()
    shutil.rmtree("./job")
    return {"msg": "delete all server"}


@router.delete("/servers/{server_id}")
async def delete_server(server_id: Annotated[str, Path(...)]):
    # monogo_client = MongoClient(config["MONGODB_URI"])[config["DB_NAME"]]["server"]
    # result = monogo_client.delete_one({"_id": ObjectId(server_id)})
    monogo_client = MongoClient(config["MONGODB_URI"])[config["DB_NAME"]]["project"]
    result = monogo_client.find_one(ObjectId(server_id))
    print(result)
    # path = f"./job/{result['project_name'] +'_'+ str(server_id)}"
    # print(result["path"])
    # shutil.rmtree(path)
    return {"msg": f"{server_id} deleted"}
