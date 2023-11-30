from fastapi import APIRouter, status, WebSocket
from starlette.websockets import WebSocketState
from dotenv import dotenv_values
from pymongo import MongoClient
from pymongo.collation import Collation
from jinja2 import Environment, FileSystemLoader
from fastapi.encoders import jsonable_encoder
from models import *
from typing import List
from bson.objectid import ObjectId
import subprocess, asyncio, os, logging, shutil

router = APIRouter(prefix="/api")
config = dotenv_values(".env")
monogo_client = MongoClient(config["MONGODB_URI"])[config["DB_NAME"]]["users"]
connected_clients = []


@router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    connected_clients.clear()
    await websocket.accept()
    connected_clients.append(websocket)
    try:
        while True:
            await asyncio.sleep(1)
            # data = await websocket.receive_text()
            # await websocket.send_text(f"You said: {data}")
    except Exception as e:
        print(e)
    finally:
        connected_clients.clear()


async def run_proc(cmd):
    try:
        process = subprocess.Popen(
            cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True
        )
        while True:
            out = process.stdout.readline()
            if out == b"" and process.poll() != None:
                break
            if out != b"":
                logging.debug(f"Sending data to {len(connected_clients)} clients.")
                for client in connected_clients:
                    print(client.client_state)
                    if client.client_state == WebSocketState.CONNECTED:
                        logging.debug(f"Sending to client {client}")
                        await client.send_text(out.decode())
                    else:
                        connected_clients.remove(client)
    except Exception as e:
        print(e)


@router.post("/run")
async def run_command(cmd: Command):
    cmd_received = jsonable_encoder(cmd)
    asyncio.create_task(run_proc(cmd_received["cmd"]))


@router.post("/hardeing")
async def run_command(job: Job):
    job = job.model_dump()
    monogo_client = MongoClient(config["MONGODB_URI"])[config["DB_NAME"]][
        "hardening_job"
    ]
    myquery = {"server_id": ObjectId(job["server_id"])}
    newvalues = {
        "$set": {
            "status": "success",
            "run_at": datetime.datetime.now(tz=datetime.timezone.utc)
            # Add more fields and values as needed
        }
    }
    monogo_client.update_one(myquery, newvalues)
    # server = monogo_client.find_one({"server_id": ObjectId(job["server_id"])})
    # print(server)
    return {"msg": "running"}


@router.get("/hardening", response_model=List[Hardening_Job])
async def list_server():
    monogo_client = MongoClient(config["MONGODB_URI"])[config["DB_NAME"]][
        "hardening_job"
    ]
    servers = list(monogo_client.find().limit(10))
    return servers


@router.get("/servers", response_model=List[Server])
async def list_server():
    monogo_client = MongoClient(config["MONGODB_URI"])[config["DB_NAME"]]["server"]
    servers = list(monogo_client.find().limit(10))
    return servers


@router.post("/servers", status_code=status.HTTP_201_CREATED, response_model=Server)
async def run_command(body: Server):
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
    path = f"./cis/{result['project_name'] +'_'+ str(body['_id'])}"
    os.makedirs(path)
    with open(f"{path}/hosts", "w") as file:
        file.write(render_file)
    monogo_client = MongoClient(config["MONGODB_URI"])[config["DB_NAME"]][
        "hardening_job"
    ]
    result = monogo_client.insert_one({"server_id": body["_id"], "path": path})
    return body


@router.delete("/servers")
async def list_server():
    monogo_client = MongoClient(config["MONGODB_URI"])[config["DB_NAME"]]["server"]
    result = monogo_client.drop()
    shutil.rmtree("./cis")
    return {"msg": "delete all server"}


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


@router.delete("/projects")
async def delete_project():
    monogo_client = MongoClient(config["MONGODB_URI"])[config["DB_NAME"]]["project"]
    result = monogo_client.drop()
    return {"msg": "delete all project"}


@router.get("/documents", response_model=List[CIS_Benchmark])
async def list_server():
    monogo_client = MongoClient(config["MONGODB_URI"])[config["DB_NAME"]][
        "cis_benchmark"
    ]
    servers = list(
        monogo_client.find()
        .sort("benchmark_no")
        .collation(Collation(locale="en_US", numericOrdering=True))
    )
    return servers
