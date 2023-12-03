from fastapi import APIRouter
from dotenv import dotenv_values
from pymongo import MongoClient
from pymongo.collation import Collation
from models import *
from typing import List

router = APIRouter(prefix="/api")
config = dotenv_values(".env")


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
