from fastapi import APIRouter, status, WebSocket
from starlette.websockets import WebSocketState
from dotenv import dotenv_values
from pymongo import MongoClient
from jinja2 import Environment, FileSystemLoader
from fastapi.encoders import jsonable_encoder
from models import *
from typing import List
from bson.objectid import ObjectId
import subprocess, asyncio, logging, time

router = APIRouter(prefix="/api")
config = dotenv_values(".env")
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


def save_history(output, id):
    monogo_client = MongoClient(config["MONGODB_URI"])[config["DB_NAME"]][
        "hardening_job"
    ]
    # server = monogo_client.find_one({"server_id": ObjectId(id)})
    # history = server["history"]
    # print(output)
    # history.append(output)
    # print(history)
    myquery = {"server_id": id}
    newvalues = {"$set": {"history": output, "status": "success"}}
    monogo_client.update_one(myquery, newvalues)


async def run_proc(cmd, id):
    result_output = b""
    try:
        process = subprocess.Popen(
            cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True
        )
        while True:
            out = process.stdout.readline()
            if out == b"" and process.poll() != None:
                break
            if out != b"":
                result_output += out
                logging.debug(f"Sending data to {len(connected_clients)} clients.")
                for client in connected_clients:
                    print(client.client_state)
                    if client.client_state == WebSocketState.CONNECTED:
                        logging.debug(f"Sending to client {client}")
                        # time.sleep(0.1)
                        await client.send_text(out.decode())
                    else:
                        connected_clients.remove(client)
    except Exception as e:
        print(e)
    # save_history(result_output, id)


@router.post("/run")
async def run_command(cmd: Command):
    cmd_received = jsonable_encoder(cmd)
    asyncio.create_task(run_proc(cmd_received["cmd"], cmd_received["id"]))


@router.post("/hardening")
async def run_job(job: Job):
    env = Environment(loader=FileSystemLoader("./templates/cis/hardening/vars"))
    template = env.get_template("main.yml.j2")
    body_json = jsonable_encoder(job)
    # print(body_json)
    render_file = template.render(body_json)
    # print(render_file)
    job = job.model_dump()
    monogo_client = MongoClient(config["MONGODB_URI"])[config["DB_NAME"]]["server"]
    server = monogo_client.find_one({"_id": ObjectId(job["server_id"])})
    # print(server)
    with open(f"{server['path'] + '/hardening/vars'}/main.yml", "w") as file:
        file.write(render_file)
    monogo_client = MongoClient(config["MONGODB_URI"])[config["DB_NAME"]][
        "hardening_job"
    ]
    myquery = {"server_id": job["server_id"]}
    newvalues = {
        "$set": {
            "status": "running",
            "run_at": datetime.datetime.now(tz=datetime.timezone.utc),
            "topic_select": job["topic_select"],
        }
    }
    monogo_client.update_one(myquery, newvalues)
    # run command
    cmd = f"ansible-playbook -i {server['path']+'/hosts'} {server['path']+'/hardening/tasks/main.yml'}"
    # print(cmd)
    asyncio.create_task(run_proc("ls -la && cat main.py", job["server_id"]))
    return {"msg": "running"}


@router.get("/hardening", response_model=List[Hardening_Job])
async def list_job():
    monogo_client = MongoClient(config["MONGODB_URI"])[config["DB_NAME"]][
        "hardening_job"
    ]
    servers = list(monogo_client.find().limit(10))
    return servers


@router.delete("/hardening")
async def delete_job():
    monogo_client = MongoClient(config["MONGODB_URI"])[config["DB_NAME"]][
        "hardening_job"
    ]
    result = monogo_client.drop()
    return {"msg": "delete all hardening-jobs"}
