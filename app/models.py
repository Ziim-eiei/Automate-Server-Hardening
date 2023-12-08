from typing_extensions import Annotated
from pydantic.functional_validators import BeforeValidator
from pydantic import BaseModel, Field
from typing import List, Optional
import datetime

PyObjectId = Annotated[str, BeforeValidator(str)]


class Employee(BaseModel):
    id: Optional[PyObjectId] = Field(alias="_id", default=None)
    firstname: str
    lastname: str
    position: str


class Command(BaseModel):
    cmd: str
    id: str


class Job(BaseModel):
    server_id: str
    topic_select: dict = Field(default={})
    type: Optional[str] = Field(default="")


class Server(BaseModel):
    id: Optional[PyObjectId] = Field(alias="_id", default=None)
    server_ip: str
    server_username: str
    server_password: str
    project_id: str
    path: str = Field(default="")


class Project(BaseModel):
    id: Optional[PyObjectId] = Field(alias="_id", default=None)
    project_name: str
    project_description: str
    created_at: Optional[datetime.datetime] = Field(default=None)
    server: List[Server] = Field(default=[])


class CIS_Benchmark(BaseModel):
    id: Optional[PyObjectId] = Field(alias="_id", default=None)
    benchmark_no: str
    benchmark_name: str
    benchmark_child: Optional[List] = Field(default=[])
    benchmark_detail: Optional[str] = Field(default="")


class Hardening_Job(BaseModel):
    id: Optional[PyObjectId] = Field(alias="_id", default="")
    server_id: Optional[PyObjectId] = Field(default="")
    topic_select: dict = Field(default={})
    status: str = Field(default="")
    run_at: Optional[datetime.datetime] = Field(default=None)
    created_at: datetime.datetime
    history: str = Field(default="")
    # path: str = Field(default="")


class Audit_Result(BaseModel):
    id: Optional[PyObjectId] = Field(alias="_id", default=None)
    server_id: str
    topic_select: List = Field(default=[])
    status: str
    run_at: Optional[datetime.datetime] = Field(default=None)
    history: str
