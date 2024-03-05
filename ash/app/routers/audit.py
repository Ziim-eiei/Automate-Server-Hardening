from fastapi import APIRouter, Path
from starlette.websockets import WebSocketState
from dotenv import dotenv_values
from pymongo import MongoClient
from jinja2 import Environment, FileSystemLoader
from fastapi.encoders import jsonable_encoder
from models import *
from typing import List
from bson.objectid import ObjectId
import subprocess, asyncio, logging
import configparser

router = APIRouter(prefix="/api")
config = dotenv_values(".env")


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
                print(out.decode())
    except Exception as e:
        print(e)


@router.post("/audit")
async def run_job(job: Job):
    job = job.model_dump()
    monogo_client = MongoClient(config["MONGODB_URI"])[config["DB_NAME"]]["server"]
    server = monogo_client.find_one({"_id": ObjectId(job["server_id"])})
    cmd = f"ansible-playbook -i {server['path']+'/hosts'} {server['path']+'/audit/tasks/main.yml'}"
    print(cmd)
    asyncio.create_task(run_proc(cmd, job["server_id"]))
    return {"msg": "running"}


def audit_cis(path):
    # variables
    everyone_sid = "*S-1-1-0"
    auth_users_sid = "*S-1-5-11"
    local_svc_sid = "*S-1-5-19"
    local_net_sid = "*S-1-5-20"
    admin_sid = "*S-1-5-32-544"
    user_sid = "*S-1-5-32-545"
    guest_sid = "*S-1-5-32-546"
    backup_sid = "*S-1-5-32-551"
    remote_desktop_sid = "*S-1-5-32-555"
    nt_svc_sid = "*S-1-5-80-"

    audit_result = {}
    try:
        audit_file = configparser.ConfigParser()
        audit_file.read(f"{path}/audit/security.cfg", encoding="utf-16")
        # 1.1.1
        audit_result["1.1.1"] = {}
        audit_result["1.1.1"]["value"] = audit_file["System Access"][
            "PasswordHistorySize"
        ]
        audit_result["1.1.1"]["status"] = (
            int(audit_file["System Access"]["PasswordHistorySize"]) == 24
        )
        # 1.1.2
        audit_result["1.1.2"] = {}
        audit_result["1.1.2"]["value"] = audit_file["System Access"][
            "MaximumPasswordAge"
        ]
        audit_result["1.1.2"]["status"] = (
            int(audit_file["System Access"]["MaximumPasswordAge"]) >= 60
        )
        # 1.1.3
        audit_result["1.1.3"] = {}
        audit_result["1.1.3"]["value"] = audit_file["System Access"][
            "MinimumPasswordAge"
        ]
        audit_result["1.1.3"]["status"] = (
            int(audit_file["System Access"]["MinimumPasswordAge"]) >= 1
        )
        # 1.1.4
        audit_result["1.1.4"] = {}
        audit_result["1.1.4"]["value"] = audit_file["System Access"][
            "MinimumPasswordLength"
        ]
        audit_result["1.1.4"]["status"] = (
            int(audit_file["System Access"]["MinimumPasswordLength"]) >= 14
        )
        # 1.1.5
        audit_result["1.1.5"] = {}
        audit_result["1.1.5"]["value"] = audit_file["System Access"][
            "PasswordComplexity"
        ]
        audit_result["1.1.5"]["status"] = (
            int(audit_file["System Access"]["PasswordComplexity"]) == 1
        )
        # 1.1.6
        audit_result["1.1.6"] = {}
        audit_result["1.1.6"]["value"] = audit_file["System Access"][
            "ClearTextPassword"
        ]
        audit_result["1.1.6"]["status"] = (
            int(audit_file["System Access"]["ClearTextPassword"]) == 0
        )
        # 1.2.1
        audit_result["1.2.1"] = {}
        audit_result["1.2.1"]["value"] = audit_file["System Access"]["LockoutDuration"]
        audit_result["1.2.1"]["status"] = (
            int(audit_file["System Access"]["LockoutDuration"]) >= 15
        )
        # 1.2.2
        audit_result["1.2.2"] = {}
        audit_result["1.2.2"]["value"] = audit_file["System Access"]["LockoutBadCount"]
        audit_result["1.2.2"]["status"] = (
            int(audit_file["System Access"]["LockoutBadCount"]) >= 10
        )
        # 1.2.3
        audit_result["1.2.3"] = {}
        audit_result["1.2.3"]["value"] = audit_file["System Access"][
            "ResetLockoutCount"
        ]
        audit_result["1.2.3"]["status"] = (
            int(audit_file["System Access"]["ResetLockoutCount"]) >= 15
        )
        # 2.2.1
        try:
            audit_result["2.2.1"] = {}
            audit_result["2.2.1"]["value"] = audit_file["Privilege Rights"][
                "SeTrustedCredManAccessPrivilege"
            ]
            audit_result["2.2.1"]["status"] = False
        except:
            audit_result["2.2.1"] = {}
            audit_result["2.2.1"]["value"] = "N/A"
            audit_result["2.2.1"]["status"] = True
        # 2.2.2
        audit_result["2.2.2"] = {}
        audit_result["2.2.2"]["value"] = audit_file["Privilege Rights"][
            "SeNetworkLogonRight"
        ]
        audit_result["2.2.2"]["status"] = (
            audit_file["Privilege Rights"]["SeNetworkLogonRight"]
            == f"{auth_users_sid },{ admin_sid }"
        )
    except Exception as e:
        return {"error": str(e)}
    return audit_result


@router.get("/audit/{server_id}")
async def get_audit_jobs(server_id: Annotated[str, Path(...)]):
    monogo_client = MongoClient(config["MONGODB_URI"])[config["DB_NAME"]]["server"]
    server = monogo_client.find_one({"_id": ObjectId(server_id)})
    result = audit_cis(server["path"])
    return result
