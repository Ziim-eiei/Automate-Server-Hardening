from fastapi import APIRouter, status, Path, HTTPException
from dotenv import dotenv_values
from pymongo import MongoClient
from pymongo.collation import Collation
from models import *
from typing import List

router = APIRouter(prefix="/api")
config = dotenv_values(".env")


@router.get("/documents", response_model=List[CIS_Benchmark])
async def list_documents():
    monogo_client = MongoClient(config["MONGODB_URI"])[config["DB_NAME"]][
        "cis_benchmark"
    ]
    docs = list(
        monogo_client.find()
        .sort("benchmark_no")
        .collation(Collation(locale="en_US", numericOrdering=True))
    )
    docs = [d for d in docs if len(d["benchmark_no"]) == 1]
    return docs


@router.get("/documents/{benchmark_no}", response_model=List[CIS_Benchmark])
async def get_document(benchmark_no: Annotated[str, Path(...)]):
    monogo_client = MongoClient(config["MONGODB_URI"])[config["DB_NAME"]][
        "cis_benchmark"
    ]
    docs = []
    doc = monogo_client.find_one({"benchmark_no": (benchmark_no)})
    try:
        for t in doc["benchmark_child"]:
            find_sub = doc = monogo_client.find_one({"benchmark_no": t})
            if find_sub != None:
                docs.append(find_sub)
    except Exception as e:
        raise HTTPException(status_code=404, detail="not found")
    return docs
