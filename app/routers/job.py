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
    monogo_client = MongoClient(config["MONGODB_URI"])[config["DB_NAME"]][
        "hardening_job"
    ]
    # print(job)
    hardening_job = {
        "server_id": job["server_id"],
        "status": "not running",
        "created_at": datetime.datetime.now(tz=datetime.timezone.utc),
    }
    result = monogo_client.insert_one(
        jsonable_encoder(hardening_job, exclude_none=True)
    )


# def create_audit_job():
#     monogo_client = MongoClient(config["MONGODB_URI"])[config["DB_NAME"]]["audit_job"]


@router.post("/jobs")
async def create_job(job: Job):
    job = jsonable_encoder(job)
    if job["type"] == "hardening":
        create_hardening_job(job)
    # print(job)
    return {"msg": f"create {job['type']} of {job['server_id']} "}
