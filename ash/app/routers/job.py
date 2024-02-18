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


def create_hardening_job(job: Job):
    monogo_client = MongoClient(config["MONGODB_URI"])[config["DB_NAME"]]["server"]
    server = monogo_client.find_one(ObjectId(job["server_id"]))
    monogo_client = MongoClient(config["MONGODB_URI"])[config["DB_NAME"]]["project"]
    project = monogo_client.find_one(ObjectId(server["project_id"]))
    # print(job)
    monogo_client = MongoClient(config["MONGODB_URI"])[config["DB_NAME"]][
        "hardening_job"
    ]
    hardening_job = {
        "server_id": job["server_id"],
        "status": "not running",
        "created_at": datetime.datetime.now(tz=datetime.timezone.utc),
        "name": f"{project['project_name']}-{server['server_ip']}",
    }
    result = monogo_client.insert_one(
        jsonable_encoder(hardening_job, exclude_none=True)
    )
    return result.inserted_id


# def create_audit_job():
#     monogo_client = MongoClient(config["MONGODB_URI"])[config["DB_NAME"]]["audit_job"]


@router.post("/jobs")
async def create_job(job: Job):
    job = jsonable_encoder(job)
    if job["type"] == "hardening":
        job_id = create_hardening_job(job)
    # print(job)
    return {"msg": f"create {job['type']} of {job['server_id']}", "job_id": f"{job_id}"}
