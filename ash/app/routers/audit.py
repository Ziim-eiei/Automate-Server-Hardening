from fastapi import APIRouter, Path, HTTPException
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
        audit_result["rule_1_1_1"] = {}
        audit_result["rule_1_1_1"]["value"] = audit_file["System Access"][
            "PasswordHistorySize"
        ]
        audit_result["rule_1_1_1"]["status"] = (
            int(audit_file["System Access"]["PasswordHistorySize"]) == 24
        )
        # 1.1.2
        audit_result["rule_1_1_2"] = {}
        audit_result["rule_1_1_2"]["value"] = audit_file["System Access"][
            "MaximumPasswordAge"
        ]
        audit_result["rule_1_1_2"]["status"] = (
            int(audit_file["System Access"]["MaximumPasswordAge"]) >= 60
        )
        # 1.1.3
        audit_result["rule_1_1_3"] = {}
        audit_result["rule_1_1_3"]["value"] = audit_file["System Access"][
            "MinimumPasswordAge"
        ]
        audit_result["rule_1_1_3"]["status"] = (
            int(audit_file["System Access"]["MinimumPasswordAge"]) >= 1
        )
        # 1.1.4
        audit_result["rule_1_1_4"] = {}
        audit_result["rule_1_1_4"]["value"] = audit_file["System Access"][
            "MinimumPasswordLength"
        ]
        audit_result["rule_1_1_4"]["status"] = (
            int(audit_file["System Access"]["MinimumPasswordLength"]) >= 14
        )
        # 1.1.5
        audit_result["rule_1_1_5"] = {}
        audit_result["rule_1_1_5"]["value"] = audit_file["System Access"][
            "PasswordComplexity"
        ]
        audit_result["rule_1_1_5"]["status"] = (
            int(audit_file["System Access"]["PasswordComplexity"]) == 1
        )
        # 1.1.6
        audit_result["rule_1_1_6"] = {}
        audit_result["rule_1_1_6"]["value"] = audit_file["System Access"][
            "ClearTextPassword"
        ]
        audit_result["rule_1_1_6"]["status"] = (
            int(audit_file["System Access"]["ClearTextPassword"]) == 0
        )
        # 1.2.1
        audit_result["rule_1_2_1"] = {}
        audit_result["rule_1_2_1"]["value"] = audit_file["System Access"][
            "LockoutDuration"
        ]
        audit_result["rule_1_2_1"]["status"] = (
            int(audit_file["System Access"]["LockoutDuration"]) >= 15
        )
        # 1.2.2
        audit_result["rule_1_2_2"] = {}
        audit_result["rule_1_2_2"]["value"] = audit_file["System Access"][
            "LockoutBadCount"
        ]
        audit_result["rule_1_2_2"]["status"] = (
            int(audit_file["System Access"]["LockoutBadCount"]) >= 5
        )
        # 1.2.3
        audit_result["rule_1_2_3"] = {}
        audit_result["rule_1_2_3"]["value"] = audit_file["System Access"][
            "ResetLockoutCount"
        ]
        audit_result["rule_1_2_3"]["status"] = (
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
        # 2.2.3
        try:
            audit_result["2.2.3"] = {}
            audit_result["2.2.3"]["value"] = audit_file["Privilege Rights"][
                "SeNetworkLogonRight"
            ]
            audit_result["2.2.3"]["status"] = (
                audit_file["Privilege Rights"]["SeNetworkLogonRight"]
                == f"{auth_users_sid},{admin_sid}"
            )
        except:
            audit_result["2.2.3"] = {}
            audit_result["2.2.3"]["value"] = "N/A"
            audit_result["2.2.3"]["status"] = False
        # 2.2.4
        try:
            audit_result["2.2.4"] = {}
            audit_result["2.2.4"]["value"] = audit_file["Privilege Rights"][
                "SeTcbPrivilege"
            ]
            audit_result["2.2.4"]["status"] = (
                audit_file["Privilege Rights"]["SeTcbPrivilege"] == ""
            )
        except:
            audit_result["2.2.4"] = {}
            audit_result["2.2.4"]["value"] = "N/A"
            audit_result["2.2.4"]["status"] = True
        # 2.2.6
        try:
            audit_result["2.2.6"] = {}
            audit_result["2.2.6"]["value"] = audit_file["Privilege Rights"][
                "SeIncreaseQuotaPrivilege"
            ]
            audit_result["2.2.6"]["status"] = (
                audit_file["Privilege Rights"]["SeIncreaseQuotaPrivilege"]
                == f"{local_svc_sid},{local_net_sid},{admin_sid}"
            )
        except:
            audit_result["2.2.6"] = {}
            audit_result["2.2.6"]["value"] = "N/A"
            audit_result["2.2.6"]["status"] = False
        # 2.2.7
        try:
            audit_result["2.2.7"] = {}
            audit_result["2.2.7"]["value"] = audit_file["Privilege Rights"][
                "SeInteractiveLogonRight"
            ]
            audit_result["2.2.7"]["status"] = (
                audit_file["Privilege Rights"]["SeInteractiveLogonRight"]
                == f"{admin_sid}"
            )
        except:
            audit_result["2.2.7"] = {}
            audit_result["2.2.7"]["value"] = "N/A"
            audit_result["2.2.7"]["status"] = False
        # 2.2.9
        try:
            audit_result["2.2.9"] = {}
            audit_result["2.2.9"]["value"] = audit_file["Privilege Rights"][
                "SeRemoteInteractiveLogonRight"
            ]
            audit_result["2.2.9"]["status"] = (
                audit_file["Privilege Rights"]["SeRemoteInteractiveLogonRight"]
                == f"{admin_sid},{remote_desktop_sid}"
            )
        except:
            audit_result["2.2.9"] = {}
            audit_result["2.2.9"]["value"] = "N/A"
            audit_result["2.2.9"]["status"] = False
        # 2.2.10
        try:
            audit_result["2.2.10"] = {}
            audit_result["2.2.10"]["value"] = audit_file["Privilege Rights"][
                "SeBackupPrivilege"
            ]
            audit_result["2.2.10"]["status"] = (
                audit_file["Privilege Rights"]["SeBackupPrivilege"] == f"{admin_sid}"
            )
        except:
            audit_result["2.2.10"] = {}
            audit_result["2.2.10"]["value"] = "N/A"
            audit_result["2.2.10"]["status"] = False
        # 2.2.11
        try:
            audit_result["2.2.11"] = {}
            audit_result["2.2.11"]["value"] = audit_file["Privilege Rights"][
                "SeSystemTimePrivilege"
            ]
            audit_result["2.2.11"]["status"] = (
                audit_file["Privilege Rights"]["SeSystemTimePrivilege"]
                == f"{local_svc_sid},{admin_sid}"
            )
        except:
            audit_result["2.2.11"] = {}
            audit_result["2.2.11"]["value"] = "N/A"
            audit_result["2.2.11"]["status"] = False
        # 2.2.12
        try:
            audit_result["2.2.12"] = {}
            audit_result["2.2.12"]["value"] = audit_file["Privilege Rights"][
                "SeTimeZonePrivilege"
            ]
            audit_result["2.2.12"]["status"] = (
                audit_file["Privilege Rights"]["SeTimeZonePrivilege"]
                == f"{local_svc_sid},{admin_sid}"
            )
        except:
            audit_result["2.2.12"] = {}
            audit_result["2.2.12"]["value"] = "N/A"
            audit_result["2.2.12"]["status"] = False
        # 2.2.13
        try:
            audit_result["2.2.13"] = {}
            audit_result["2.2.13"]["value"] = audit_file["Privilege Rights"][
                "SeCreatePagefilePrivilge"
            ]
            audit_result["2.2.13"]["status"] = (
                audit_file["Privilege Rights"]["SeCreatePagefilePrivilge"]
                == f"{admin_sid}"
            )
        except:
            audit_result["2.2.13"] = {}
            audit_result["2.2.13"]["value"] = "N/A"
            audit_result["2.2.13"]["status"] = False
        # 2.2.14
        try:
            audit_result["2.2.14"] = {}
            audit_result["2.2.14"]["value"] = audit_file["Privilege Rights"][
                "SeCreateTokenPrivilege"
            ]
            audit_result["2.2.14"]["status"] = (
                audit_file["Privilege Rights"]["SeCreateTokenPrivilege"] == ""
            )
        except:
            audit_result["2.2.14"] = {}
            audit_result["2.2.14"]["value"] = "N/A"
            audit_result["2.2.14"]["status"] = True
        # 2.2.15
        try:
            audit_result["2.2.15"] = {}
            audit_result["2.2.15"]["value"] = audit_file["Privilege Rights"][
                "SeCreateGlobalPrivilege"
            ]
            audit_result["2.2.15"]["status"] = (
                audit_file["Privilege Rights"]["SeCreateGlobalPrivilege"]
                == f"{local_svc_sid},{local_net_sid},{admin_sid}"
            )
        except:
            audit_result["2.2.15"] = {}
            audit_result["2.2.15"]["value"] = "N/A"
            audit_result["2.2.15"]["status"] = False
        # 2.2.16
        try:
            audit_result["2.2.16"] = {}
            audit_result["2.2.16"]["value"] = audit_file["Privilege Rights"][
                "SeCreatePermanentPrivilege"
            ]
            audit_result["2.2.16"]["status"] = (
                audit_file["Privilege Rights"]["SeCreatePermanentPrivilege"] == ""
            )
        except:
            audit_result["2.2.16"] = {}
            audit_result["2.2.16"]["value"] = "N/A"
            audit_result["2.2.16"]["status"] = True
        # 2.2.18
        try:
            audit_result["2.2.18"] = {}
            audit_result["2.2.18"]["value"] = audit_file["Privilege Rights"][
                "SeCreateSymbolicLinkPrivilege"
            ]
            audit_result["2.2.18"]["status"] = (
                audit_file["Privilege Rights"]["SeCreateSymbolicLinkPrivilege"]
                == f"{admin_sid}"
            )
        except:
            audit_result["2.2.18"] = {}
            audit_result["2.2.18"]["value"] = "N/A"
            audit_result["2.2.18"]["status"] = False
        # 2.2.19
        try:
            audit_result["2.2.19"] = {}
            audit_result["2.2.19"]["value"] = audit_file["Privilege Rights"][
                "SeDebugPrivilege"
            ]
            audit_result["2.2.19"]["status"] = (
                audit_file["Privilege Rights"]["SeDebugPrivilege"] == f"{admin_sid}"
            )
        except:
            audit_result["2.2.19"] = {}
            audit_result["2.2.19"]["value"] = "N/A"
            audit_result["2.2.19"]["status"] = False
        # 2.2.21
        try:
            audit_result["2.2.21"] = {}
            audit_result["2.2.21"]["value"] = audit_file["Privilege Rights"][
                "DenyNetworkLogonRight"
            ]
            audit_result["2.2.21"]["status"] = (
                audit_file["Privilege Rights"]["DenyNetworkLogonRight"] == ""
            )
        except:
            audit_result["2.2.21"] = {}
            audit_result["2.2.21"]["value"] = "N/A"
            audit_result["2.2.21"]["status"] = True
        # 2.2.22
        try:
            audit_result["2.2.22"] = {}
            audit_result["2.2.22"]["value"] = audit_file["Privilege Rights"][
                "SeDenyBatchLogonRight"
            ]
            audit_result["2.2.22"]["status"] = (
                audit_file["Privilege Rights"]["SeDenyBatchLogonRight"]
                == f"{guest_sid}"
            )
        except:
            audit_result["2.2.22"] = {}
            audit_result["2.2.22"]["value"] = "N/A"
            audit_result["2.2.22"]["status"] = False
        # 2.2.23
        try:
            audit_result["2.2.23"] = {}
            audit_result["2.2.23"]["value"] = audit_file["Privilege Rights"][
                "SeDenyServiceLogonRight"
            ]
            audit_result["2.2.23"]["status"] = (
                audit_file["Privilege Rights"]["SeDenyServiceLogonRight"]
                == f"{guest_sid}"
            )
        except:
            audit_result["2.2.23"] = {}
            audit_result["2.2.23"]["value"] = "N/A"
            audit_result["2.2.23"]["status"] = False
        # 2.2.24
        try:
            audit_result["2.2.24"] = {}
            audit_result["2.2.24"]["value"] = audit_file["Privilege Rights"][
                "SeDenyInteractiveLogonRight"
            ]
            audit_result["2.2.24"]["status"] = (
                audit_file["Privilege Rights"]["SeDenyInteractiveLogonRight"]
                == f"{guest_sid}"
            )
        except:
            audit_result["2.2.24"] = {}
            audit_result["2.2.24"]["value"] = "N/A"
            audit_result["2.2.24"]["status"] = False
        # 2.2.26
        try:
            audit_result["2.2.26"] = {}
            audit_result["2.2.26"]["value"] = audit_file["Privilege Rights"][
                "RemoteInteractiveLogonRight"
            ]
            audit_result["2.2.26"]["status"] = (
                audit_file["Privilege Rights"]["RemoteInteractiveLogonRight"]
                == f"{guest_sid}"
            )
        except:
            audit_result["2.2.26"] = {}
            audit_result["2.2.26"]["value"] = "N/A"
            audit_result["2.2.26"]["status"] = False
        # 2.2.28
        try:
            audit_result["2.2.28"] = {}
            audit_result["2.2.28"]["value"] = audit_file["Privilege Rights"][
                "EnableDelegationPrivilege"
            ]
            audit_result["2.2.28"]["status"] = (
                audit_file["Privilege Rights"]["EnableDelegationPrivilege"] == ""
            )
        except:
            audit_result["2.2.28"] = {}
            audit_result["2.2.28"]["value"] = "N/A"
            audit_result["2.2.28"]["status"] = True
        # 2.2.29
        try:
            audit_result["2.2.29"] = {}
            audit_result["2.2.29"]["value"] = audit_file["Privilege Rights"][
                "SeRemoteShutdownPrivilege"
            ]
            audit_result["2.2.29"]["status"] = (
                audit_file["Privilege Rights"]["SeRemoteShutdownPrivilege"]
                == f"{admin_sid}"
            )
        except:
            audit_result["2.2.29"] = {}
            audit_result["2.2.29"]["value"] = "N/A"
            audit_result["2.2.29"]["status"] = False
        # 2.2.30
        try:
            audit_result["2.2.30"] = {}
            audit_result["2.2.30"]["value"] = audit_file["Privilege Rights"][
                "SeAuditPrivilege"
            ]
            audit_result["2.2.30"]["status"] = (
                audit_file["Privilege Rights"]["SeAuditPrivilege"]
                == f"{local_svc_sid},{local_net_sid}"
            )
        except:
            audit_result["2.2.30"] = {}
            audit_result["2.2.30"]["value"] = "N/A"
            audit_result["2.2.30"]["status"] = False
        # 2.2.32
        try:
            audit_result["2.2.32"] = {}
            audit_result["2.2.32"]["value"] = audit_file["Privilege Rights"][
                "SeDelegateSessionUserImpersonatePrivilege"
            ]
            audit_result["2.2.32"]["status"] = (
                audit_file["Privilege Rights"][
                    "SeDelegateSessionUserImpersonatePrivilege"
                ]
                == f"{admin_sid}"
            )
        except:
            audit_result["2.2.32"] = {}
            audit_result["2.2.32"]["value"] = "N/A"
            audit_result["2.2.32"]["status"] = False
        # 2.2.33
        try:
            audit_result["2.2.33"] = {}
            audit_result["2.2.33"]["value"] = audit_file["Privilege Rights"][
                "SeIncreaseBasePriorityPrivilege"
            ]
            audit_result["2.2.33"]["status"] = (
                audit_file["Privilege Rights"]["SeIncreaseBasePriorityPrivilege"]
                == f"{admin_sid}"
            )
        except:
            audit_result["2.2.33"] = {}
            audit_result["2.2.33"]["value"] = "N/A"
            audit_result["2.2.33"]["status"] = False
        # 2.2.34
        try:
            audit_result["2.2.34"] = {}
            audit_result["2.2.34"]["value"] = audit_file["Privilege Rights"][
                "SeLoadDriverPrivilege"
            ]
            audit_result["2.2.34"]["status"] = (
                audit_file["Privilege Rights"]["SeLoadDriverPrivilege"]
                == f"{admin_sid}"
            )
        except:
            audit_result["2.2.34"] = {}
            audit_result["2.2.34"]["value"] = "N/A"
            audit_result["2.2.34"]["status"] = False
        # 2.2.35
        try:
            audit_result["2.2.35"] = {}
            audit_result["2.2.35"]["value"] = audit_file["Privilege Rights"][
                "SeLockMemoryPrivilege"
            ]
            audit_result["2.2.35"]["status"] = (
                audit_file["Privilege Rights"]["SeLockMemoryPrivilege"] == ""
            )
        except:
            audit_result["2.2.35"] = {}
            audit_result["2.2.35"]["value"] = "N/A"
            audit_result["2.2.35"]["status"] = True
        # 2.2.38
        try:
            audit_result["2.2.38"] = {}
            audit_result["2.2.38"]["value"] = audit_file["Privilege Rights"][
                "SeSecurityPrivilege"
            ]
            audit_result["2.2.38"]["status"] = (
                audit_file["Privilege Rights"]["SeSecurityPrivilege"] == f"{admin_sid}"
            )
        except:
            audit_result["2.2.38"] = {}
            audit_result["2.2.38"]["value"] = "N/A"
            audit_result["2.2.38"]["status"] = False
        # 2.2.39
        try:
            audit_result["2.2.39"] = {}
            audit_result["2.2.39"]["value"] = audit_file["Privilege Rights"][
                "SeReLabelPrivilege"
            ]
            audit_result["2.2.39"]["status"] = (
                audit_file["Privilege Rights"]["SeReLabelPrivilege"] == ""
            )
        except:
            audit_result["2.2.39"] = {}
            audit_result["2.2.39"]["value"] = "N/A"
            audit_result["2.2.39"]["status"] = True
        # 2.2.40
        try:
            audit_result["2.2.40"] = {}
            audit_result["2.2.40"]["value"] = audit_file["Privilege Rights"][
                "SeSystemEnvironmentPrivilege"
            ]
            audit_result["2.2.40"]["status"] = (
                audit_file["Privilege Rights"]["SeSystemEnvironmentPrivilege"]
                == f"{admin_sid}"
            )
        except:
            audit_result["2.2.40"] = {}
            audit_result["2.2.40"]["value"] = "N/A"
            audit_result["2.2.40"]["status"] = False
        # 2.2.41
        try:
            audit_result["2.2.41"] = {}
            audit_result["2.2.41"]["value"] = audit_file["Privilege Rights"][
                "SeManageVolumePrivilege"
            ]
            audit_result["2.2.41"]["status"] = (
                audit_file["Privilege Rights"]["SeManageVolumePrivilege"]
                == f"{admin_sid}"
            )
        except:
            audit_result["2.2.41"] = {}
            audit_result["2.2.41"]["value"] = "N/A"
            audit_result["2.2.41"]["status"] = False
        # 2.2.42
        try:
            audit_result["2.2.42"] = {}
            audit_result["2.2.42"]["value"] = audit_file["Privilege Rights"][
                "SeProfileSingleProcessPrivilege"
            ]
            audit_result["2.2.42"]["status"] = (
                audit_file["Privilege Rights"]["SeProfileSingleProcessPrivilege"]
                == f"{admin_sid}"
            )
        except:
            audit_result["2.2.42"] = {}
            audit_result["2.2.42"]["value"] = "N/A"
            audit_result["2.2.42"]["status"] = False
        # 2.2.43
        try:
            audit_result["2.2.43"] = {}
            audit_result["2.2.43"]["value"] = audit_file["Privilege Rights"][
                "SeSystemProfilePrivilege"
            ]
            audit_result["2.2.43"]["status"] = (
                audit_file["Privilege Rights"]["SeSystemProfilePrivilege"]
                == f"{admin_sid},{nt_svc_sid}"
            )
        except:
            audit_result["2.2.43"] = {}
            audit_result["2.2.43"]["value"] = "N/A"
            audit_result["2.2.43"]["status"] = False
        # 2.2.44
        try:
            audit_result["2.2.44"] = {}
            audit_result["2.2.44"]["value"] = audit_file["Privilege Rights"][
                "SeAssignPrimaryTokenPrivilege"
            ]
            audit_result["2.2.44"]["status"] = (
                audit_file["Privilege Rights"]["SeAssignPrimaryTokenPrivilege"]
                == f"{local_svc_sid},{local_net_sid}"
            )
        except:
            audit_result["2.2.44"] = {}
            audit_result["2.2.44"]["value"] = "N/A"
            audit_result["2.2.44"]["status"] = False
        # 2.2.45
        try:
            audit_result["2.2.45"] = {}
            audit_result["2.2.45"]["value"] = audit_file["Privilege Rights"][
                "SeRestorePrivilege"
            ]
            audit_result["2.2.45"]["status"] = (
                audit_file["Privilege Rights"]["SeRestorePrivilege"] == f"{admin_sid}"
            )
        except:
            audit_result["2.2.45"] = {}
            audit_result["2.2.45"]["value"] = "N/A"
            audit_result["2.2.45"]["status"] = False
        # 2.2.46
        try:
            audit_result["2.2.46"] = {}
            audit_result["2.2.46"]["value"] = audit_file["Privilege Rights"][
                "SeShutdownPrivilege"
            ]
            audit_result["2.2.46"]["status"] = (
                audit_file["Privilege Rights"]["SeShutdownPrivilege"] == f"{admin_sid}"
            )
        except:
            audit_result["2.2.46"] = {}
            audit_result["2.2.46"]["value"] = "N/A"
            audit_result["2.2.46"]["status"] = False
        # 2.2.48
        try:
            audit_result["2.2.48"] = {}
            audit_result["2.2.48"]["value"] = audit_file["Privilege Rights"][
                "SeTakeOwnershipPrivilege"
            ]
            audit_result["2.2.48"]["status"] = (
                audit_file["Privilege Rights"]["SeTakeOwnershipPrivilege"]
                == f"{admin_sid}"
            )
        except:
            audit_result["2.2.48"] = {}
            audit_result["2.2.48"]["value"] = "N/A"
            audit_result["2.2.48"]["status"] = False
        # 2.3.1.1
        try:
            audit_result["2.3.1.1"] = {}
            audit_result["2.3.1.1"]["value"] = audit_file["System Access"][
                "EnableAdminAccount"
            ]
            audit_result["2.3.1.1"]["status"] = (
                audit_file["System Access"]["EnableAdminAccount"] == "1"
            )
        except:
            audit_result["2.3.1.1"] = {}
            audit_result["2.3.1.1"]["value"] = "N/A"
            audit_result["2.3.1.1"]["status"] = False
        # 2.3.1.2
        try:
            audit_result["2.3.1.2"] = {}
            audit_result["2.3.1.2"]["value"] = audit_file["Registry Values"][
                "MACHINE\\SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\Policies\\System\\NoConnectedUser"
            ]
            audit_result["2.3.1.2"]["status"] = (
                audit_file["Registry Values"][
                    "MACHINE\\SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\Policies\\System\\NoConnectedUser"
                ]
                == "3"
            )
        except:
            audit_result["2.3.1.2"] = {}
            audit_result["2.3.1.2"]["value"] = "N/A"
            audit_result["2.3.1.2"]["status"] = False
        # 2.3.1.3
        try:
            audit_result["2.3.1.3"] = {}
            audit_result["2.3.1.3"]["value"] = audit_file["System Access"][
                "EnableGuestAccount"
            ]
            audit_result["2.3.1.3"]["status"] = (
                audit_file["System Access"]["EnableGuestAccount"] == "0"
            )
        except:
            audit_result["2.3.1.1"] = {}
            audit_result["2.3.1.1"]["value"] = "N/A"
            audit_result["2.3.1.1"]["status"] = False
        # 2.3.1.4
        try:
            audit_result["2.3.1.4"] = {}
            audit_result["2.3.1.4"]["value"] = audit_file["Registry Values"][
                "MACHINE\\SYSTEM\\CurrentControlSet\\Control\\Lsa\\LimitBlankPasswordUse"
            ]
            audit_result["2.3.1.4"]["status"] = (
                audit_file["Registry Values"][
                    "MACHINE\\SYSTEM\\CurrentControlSet\\Control\\Lsa\\LimitBlankPasswordUse"
                ]
                == "1"
            )
        except:
            audit_result["2.3.1.4"] = {}
            audit_result["2.3.1.4"]["value"] = "N/A"
            audit_result["2.3.1.4"]["status"] = False
        # 2.3.1.5
        try:
            audit_result["2.3.1.5"] = {}
            audit_result["2.3.1.5"]["value"] = audit_file["System Access"][
                "NewAdministratorName"
            ].replace('"', "")
            audit_result["2.3.1.5"]["status"] = (
                audit_file["System Access"]["NewAdministratorName"].replace('"', "")
                != "Administrator"
            )
        except:
            audit_result["2.3.1.5"] = {}
            audit_result["2.3.1.5"]["value"] = "N/A"
            audit_result["2.3.1.5"]["status"] = False
        # 2.3.1.6
        try:
            audit_result["2.3.1.6"] = {}
            audit_result["2.3.1.6"]["value"] = audit_file["System Access"][
                "NewGuestName"
            ].replace('"', "")
            audit_result["2.3.1.6"]["status"] = (
                audit_file["System Access"]["NewGuestName"].replace('"', "") != "Guest"
            )
        except:
            audit_result["2.3.1.6"] = {}
            audit_result["2.3.1.6"]["value"] = "N/A"
            audit_result["2.3.1.6"]["status"] = False
        # 2.3.2.1
        try:
            audit_result["2.3.2.1"] = {}
            audit_result["2.3.2.1"]["value"] = audit_file["Registry Values"][
                "MACHINE\\SYSTEM\\CurrentControlSet\\Control\\Lsa\\SCENoApplyLegacyAuditPolicy"
            ]
            audit_result["2.3.2.1"]["status"] = (
                audit_file["Registry Values"][
                    "MACHINE\\SYSTEM\\CurrentControlSet\\Control\\Lsa\\SCENoApplyLegacyAuditPolicy"
                ]
                == "1"
            )
        except:
            audit_result["2.3.2.1"] = {}
            audit_result["2.3.2.1"]["value"] = "N/A"
            audit_result["2.3.2.1"]["status"] = False

        # 2.3.2.2
        try:
            audit_result["2.3.2.2"] = {}
            audit_result["2.3.2.2"]["value"] = audit_file["Registry Values"][
                "MACHINE\\SYSTEM\\CurrentControlSet\\Control\\Lsa\\CrashOnAuditFail"
            ]
            audit_result["2.3.2.2"]["status"] = (
                audit_file["Registry Values"][
                    "MACHINE\\SYSTEM\\CurrentControlSet\\Control\\Lsa\\CrashOnAuditFail"
                ]
                == "0"
            )
        except:
            audit_result["2.3.2.2"] = {}
            audit_result["2.3.2.2"]["value"] = "N/A"
            audit_result["2.3.2.2"]["status"] = False

        # 2.3.4.1
        try:
            audit_result["2.3.4.1"] = {}
            audit_result["2.3.4.1"]["value"] = audit_file["Registry Values"][
                "MACHINE\\Software\\Microsoft\\Windows NT\\CurrentVersion\\Winlogon\\AllocateDASD"
            ]
            audit_result["2.3.4.1"]["status"] = (
                audit_file["Registry Values"][
                    "MACHINE\\Software\\Microsoft\\Windows NT\\CurrentVersion\\Winlogon\\AllocateDASD"
                ]
                == "0"
            )
        except:
            audit_result["2.3.4.1"] = {}
            audit_result["2.3.4.1"]["value"] = "N/A"
            audit_result["2.3.4.1"]["status"] = False

        # 2.3.4.2
        try:
            audit_result["2.3.4.2"] = {}
            audit_result["2.3.4.2"]["value"] = audit_file["Registry Values"][
                "MACHINE\\System\\CurrentControlSet\\Control\\Print\\Providers\\LanMan Print Services\\Servers\\AddPrinterDrivers"
            ]
            audit_result["2.3.4.2"]["status"] = (
                audit_file["Registry Values"][
                    "MACHINE\\System\\CurrentControlSet\\Control\\Print\\Providers\\LanMan Print Services\\Servers\\AddPrinterDrivers"
                ]
                == "1"
            )
        except:
            audit_result["2.3.4.2"] = {}
            audit_result["2.3.4.2"]["value"] = "N/A"
            audit_result["2.3.4.2"]["status"] = False

        # 2.3.6.1
        try:
            audit_result["2.3.6.1"] = {}
            audit_result["2.3.6.1"]["value"] = audit_file["Registry Values"][
                "MACHINE\\System\\CurrentControlSet\\Services\\Netlogon\\Parameters\\RequireSignOrSeal"
            ]
            audit_result["2.3.6.1"]["status"] = (
                audit_file["Registry Values"][
                    "MACHINE\\System\\CurrentControlSet\\Services\\Netlogon\\Parameters\\RequireSignOrSeal"
                ]
                == "1"
            )
        except:
            audit_result["2.3.6.1"] = {}
            audit_result["2.3.6.1"]["value"] = "N/A"
            audit_result["2.3.6.1"]["status"] = False

        # 2.3.6.2
        try:
            audit_result["2.3.6.2"] = {}
            audit_result["2.3.6.2"]["value"] = audit_file["Registry Values"][
                "MACHINE\\System\\CurrentControlSet\\Services\\Netlogon\\Parameters\\SealSecureChannel"
            ]
            audit_result["2.3.6.2"]["status"] = (
                audit_file["Registry Values"][
                    "MACHINE\\System\\CurrentControlSet\\Services\\Netlogon\\Parameters\\SealSecureChannel"
                ]
                == "1"
            )
        except:
            audit_result["2.3.6.2"] = {}
            audit_result["2.3.6.2"]["value"] = "N/A"
            audit_result["2.3.6.2"]["status"] = False

        # 2.3.6.3
        try:
            audit_result["2.3.6.3"] = {}
            audit_result["2.3.6.3"]["value"] = audit_file["Registry Values"][
                "MACHINE\\System\\CurrentControlSet\\Services\\Netlogon\\Parameters\\SignSecureChannel"
            ]
            audit_result["2.3.6.3"]["status"] = (
                audit_file["Registry Values"][
                    "MACHINE\\System\\CurrentControlSet\\Services\\Netlogon\\Parameters\\SignSecureChannel"
                ]
                == "1"
            )
        except:
            audit_result["2.3.6.3"] = {}
            audit_result["2.3.6.3"]["value"] = "N/A"
            audit_result["2.3.6.3"]["status"] = False

        # 2.3.6.4
        try:
            audit_result["2.3.6.4"] = {}
            audit_result["2.3.6.4"]["value"] = audit_file["Registry Values"][
                "MACHINE\\System\\CurrentControlSet\\Services\\Netlogon\\Parameters\\DisablePasswordChange"
            ]
            audit_result["2.3.6.4"]["status"] = (
                audit_file["Registry Values"][
                    "MACHINE\\System\\CurrentControlSet\\Services\\Netlogon\\Parameters\\DisablePasswordChange"
                ]
                == "1"
            )
        except:
            audit_result["2.3.6.4"] = {}
            audit_result["2.3.6.4"]["value"] = "N/A"
            audit_result["2.3.6.4"]["status"] = False

        # 2.3.6.5
        try:
            audit_result["2.3.6.5"] = {}
            audit_result["2.3.6.5"]["value"] = audit_file["Registry Values"][
                "MACHINE\\System\\CurrentControlSet\\Services\\Netlogon\\Parameters\\MaximumPasswordAge"
            ]
            audit_result["2.3.6.5"]["status"] = (
                audit_file["Registry Values"][
                    "MACHINE\\System\\CurrentControlSet\\Services\\Netlogon\\Parameters\\MaximumPasswordAge"
                ]
                == "30"
            )
        except:
            audit_result["2.3.6.5"] = {}
            audit_result["2.3.6.5"]["value"] = "N/A"
            audit_result["2.3.6.5"]["status"] = False

        # 2.3.6.6
        try:
            audit_result["2.3.6.6"] = {}
            audit_result["2.3.6.6"]["value"] = audit_file["Registry Values"][
                "MACHINE\\System\\CurrentControlSet\\Services\\Netlogon\\Parameters\\RequireStrongKey"
            ]
            audit_result["2.3.6.6"]["status"] = (
                audit_file["Registry Values"][
                    "MACHINE\\System\\CurrentControlSet\\Services\\Netlogon\\Parameters\\RequireStrongKey"
                ]
                == "1"
            )
        except:
            audit_result["2.3.6.6"] = {}
            audit_result["2.3.6.6"]["value"] = "N/A"
            audit_result["2.3.6.6"]["status"] = False

        # 2.3.7.1
        try:
            audit_result["2.3.7.1"] = {}
            audit_result["2.3.7.1"]["value"] = audit_file["Registry Values"][
                "MACHINE\\SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\Policies\\System\\DontDisplayLastUserName"
            ]
            audit_result["2.3.7.1"]["status"] = (
                audit_file["Registry Values"][
                    "MACHINE\\SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\Policies\\System\\DontDisplayLastUserName"
                ]
                == "1"
            )
        except:
            audit_result["2.3.7.1"] = {}
            audit_result["2.3.7.1"]["value"] = "N/A"
            audit_result["2.3.7.1"]["status"] = False

        # 2.3.7.2
        try:
            audit_result["2.3.7.2"] = {}
            audit_result["2.3.7.2"]["value"] = audit_file["Registry Values"][
                "MACHINE\\SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\Policies\\System\\DisableCAD"
            ]
            audit_result["2.3.7.2"]["status"] = (
                audit_file["Registry Values"][
                    "MACHINE\\SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\Policies\\System\\DisableCAD"
                ]
                == "1"
            )
        except:
            audit_result["2.3.7.2"] = {}
            audit_result["2.3.7.2"]["value"] = "N/A"
            audit_result["2.3.7.2"]["status"] = False

        # 2.3.7.3
        try:
            audit_result["2.3.7.3"] = {}
            audit_result["2.3.7.3"]["value"] = audit_file["Registry Values"][
                "MACHINE\\SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\Policies\\System\\InactivityTimeoutSecs"
            ]
            audit_result["2.3.7.3"]["status"] = (
                audit_file["Registry Values"][
                    "MACHINE\\SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\Policies\\System\\InactivityTimeoutSecs"
                ]
                == "900"
            )
        except:
            audit_result["2.3.7.3"] = {}
            audit_result["2.3.7.3"]["value"] = "N/A"
            audit_result["2.3.7.3"]["status"] = False

        # 2.3.7.4
        try:
            audit_result["2.3.7.4"] = {}
            audit_result["2.3.7.4"]["value"] = audit_file["Registry Values"][
                "MACHINE\\SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\Policies\\System\\LegalNoticeText"
            ]
            audit_result["2.3.7.4"]["status"] = (
                audit_file["Registry Values"][
                    "MACHINE\\SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\Policies\\System\\LegalNoticeText"
                ]
                != ""
            )
        except:
            audit_result["2.3.7.4"] = {}
            audit_result["2.3.7.4"]["value"] = "N/A"
            audit_result["2.3.7.4"]["status"] = False

        # 2.3.7.5
        try:
            audit_result["2.3.7.5"] = {}
            audit_result["2.3.7.5"]["value"] = audit_file["Registry Values"][
                "MACHINE\\SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\Policies\\System\\LegalNoticeCaption"
            ].replace('"', "")
            audit_result["2.3.7.5"]["status"] = (
                audit_file["Registry Values"][
                    "MACHINE\\SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\Policies\\System\\LegalNoticeCaption"
                ].replace('"', "")
                != ""
            )
        except:
            audit_result["2.3.7.5"] = {}
            audit_result["2.3.7.5"]["value"] = "N/A"
            audit_result["2.3.7.5"]["status"] = False

        # 2.3.7.7
        try:
            audit_result["2.3.7.7"] = {}
            audit_result["2.3.7.7"]["value"] = audit_file["Registry Values"][
                "MACHINE\\SOFTWARE\\Microsoft\\Windows NT\\CurrentVersion\\Winlogon\\PasswordExpiryWarning"
            ]
            audit_result["2.3.7.7"]["status"] = (
                audit_file["Registry Values"][
                    "MACHINE\\SOFTWARE\\Microsoft\\Windows NT\\CurrentVersion\\Winlogon\\PasswordExpiryWarning"
                ]
                >= "5"
                or audit_file["Registry Values"][
                    "MACHINE\\SOFTWARE\\Microsoft\\Windows NT\\CurrentVersion\\Winlogon\\PasswordExpiryWarning"
                ]
                <= "14"
            )
        except:
            audit_result["2.3.7.7"] = {}
            audit_result["2.3.7.7"]["value"] = "N/A"
            audit_result["2.3.7.7"]["status"] = False

        # 2.3.7.9
        try:
            audit_result["2.3.7.9"] = {}
            audit_result["2.3.7.9"]["value"] = (
                audit_file["Registry Values"][
                    "MACHINE\\SOFTWARE\\Microsoft\\Windows NT\\CurrentVersion\\Winlogon\\ScRemoveOption"
                ]
                .replace('"', "")
                .split(",")[1]
            )
            audit_result["2.3.7.9"]["status"] = (
                audit_file["Registry Values"][
                    "MACHINE\\SOFTWARE\\Microsoft\\Windows NT\\CurrentVersion\\Winlogon\\ScRemoveOption"
                ].split(",")[1]
                >= "1"
                or audit_file["Registry Values"][
                    "MACHINE\\SOFTWARE\\Microsoft\\Windows NT\\CurrentVersion\\Winlogon\\ScRemoveOption"
                ].split(",")[1]
                <= "3"
            )
        except:
            audit_result["2.3.7.9"] = {}
            audit_result["2.3.7.9"]["value"] = "N/A"
            audit_result["2.3.7.9"]["status"] = False

        # 2.3.8.1
        try:
            audit_result["2.3.8.1"] = {}
            audit_result["2.3.8.1"]["value"] = audit_file["Registry Values"][
                "MACHINE\\SYSTEM\\CurrentControlSet\\Services\\LanmanWorkStation\\Parameters\\RequireSecuritySignature"
            ]
            audit_result["2.3.8.1"]["status"] = (
                audit_file["Registry Values"][
                    "MACHINE\\SYSTEM\\CurrentControlSet\\Services\\LanmanWorkStation\\Parameters\\RequireSecuritySignature"
                ]
                == "1"
            )
        except:
            audit_result["2.3.8.1"] = {}
            audit_result["2.3.8.1"]["value"] = "N/A"
            audit_result["2.3.8.1"]["status"] = False

        # 2.3.8.2
        try:
            audit_result["2.3.8.2"] = {}
            audit_result["2.3.8.2"]["value"] = audit_file["Registry Values"][
                "MACHINE\\SYSTEM\\CurrentControlSet\\Services\\LanmanWorkStation\\Parameters\\EnableSecuritySignature"
            ]
            audit_result["2.3.8.2"]["status"] = (
                audit_file["Registry Values"][
                    "MACHINE\\SYSTEM\\CurrentControlSet\\Services\\LanmanWorkStation\\Parameters\\EnableSecuritySignature"
                ]
                == "1"
            )
        except:
            audit_result["2.3.8.2"] = {}
            audit_result["2.3.8.2"]["value"] = "N/A"
            audit_result["2.3.8.2"]["status"] = False

        # 2.3.8.3
        try:
            audit_result["2.3.8.3"] = {}
            audit_result["2.3.8.3"]["value"] = audit_file["Registry Values"][
                "MACHINE\\SYSTEM\\CurrentControlSet\\Services\\LanmanWorkStation\\Parameters\\EnablePlainTextPassword"
            ]
            audit_result["2.3.8.3"]["status"] = (
                audit_file["Registry Values"][
                    "MACHINE\\SYSTEM\\CurrentControlSet\\Services\\LanmanWorkStation\\Parameters\\EnablePlainTextPassword"
                ]
                == "1"
            )
        except:
            audit_result["2.3.8.3"] = {}
            audit_result["2.3.8.3"]["value"] = "N/A"
            audit_result["2.3.8.3"]["status"] = False

        # 2.3.9.1
        try:
            audit_result["2.3.9.1"] = {}
            audit_result["2.3.9.1"]["value"] = audit_file["Registry Values"][
                "MACHINE\\SYSTEM\\CurrentControlSet\\Services\\LanmanServer\\Parameters\\AutoDisconnect"
            ].split(",")[1]
            audit_result["2.3.9.1"]["status"] = (
                audit_file["Registry Values"][
                    "MACHINE\\SYSTEM\\CurrentControlSet\\Services\\LanmanServer\\Parameters\\AutoDisconnect"
                ].split(",")[1]
                >= "1"
                or audit_file["Registry Values"][
                    "MACHINE\\SYSTEM\\CurrentControlSet\\Services\\LanmanServer\\Parameters\\AutoDisconnect"
                ].split(",")[1]
                <= "15"
            )
        except:
            audit_result["2.3.9.1"] = {}
            audit_result["2.3.9.1"]["value"] = "N/A"
            audit_result["2.3.9.1"]["status"] = False

        # 2.3.9.2
        try:
            audit_result["2.3.9.2"] = {}
            audit_result["2.3.9.2"]["value"] = audit_file["Registry Values"][
                "MACHINE\\System\\CurrentControlSet\\Services\\LanManServer\\Parameters\\RequireSecuritySignature"
            ]
            audit_result["2.3.9.2"]["status"] = (
                audit_file["Registry Values"][
                    "MACHINE\\System\\CurrentControlSet\\Services\\LanManServer\\Parameters\\RequireSecuritySignature"
                ]
                == "1"
            )
        except:
            audit_result["2.3.9.2"] = {}
            audit_result["2.3.9.2"]["value"] = "N/A"
            audit_result["2.3.9.2"]["status"] = False

        # 2.3.9.3
        try:
            audit_result["2.3.9.3"] = {}
            audit_result["2.3.9.3"]["value"] = audit_file["Registry Values"][
                "MACHINE\\System\\CurrentControlSet\\Services\\LanManServer\\Parameters\\EnableSecuritySignature"
            ]
            audit_result["2.3.9.3"]["status"] = (
                audit_file["Registry Values"][
                    "MACHINE\\System\\CurrentControlSet\\Services\\LanManServer\\Parameters\\EnableSecuritySignature"
                ]
                == "1"
            )
        except:
            audit_result["2.3.9.3"] = {}
            audit_result["2.3.9.3"]["value"] = "N/A"
            audit_result["2.3.9.3"]["status"] = False

        # 2.3.9.4
        try:
            audit_result["2.3.9.4"] = {}
            audit_result["2.3.9.4"]["value"] = audit_file["Registry Values"][
                "MACHINE\\System\\CurrentControlSet\\Services\\LanManServer\\Parameters\\EnableForcedLogOff"
            ]
            audit_result["2.3.9.4"]["status"] = (
                audit_file["Registry Values"][
                    "MACHINE\\System\\CurrentControlSet\\Services\\LanManServer\\Parameters\\EnableForcedLogOff"
                ]
                == "1"
            )
        except:
            audit_result["2.3.9.4"] = {}
            audit_result["2.3.9.4"]["value"] = "N/A"
            audit_result["2.3.9.4"]["status"] = False

        # 2.3.10.1
        try:
            audit_result["2.3.10.1"] = {}
            audit_result["2.3.10.1"]["value"] = audit_file["System Access"][
                "LSAAnonymousNameLookup"
            ]
            audit_result["2.3.10.1"]["status"] = (
                audit_file["System Access"]["LSAAnonymousNameLookup"] == "0"
            )
        except:
            audit_result["2.3.10.1"] = {}
            audit_result["2.3.10.1"]["value"] = "N/A"
            audit_result["2.3.10.1"]["status"] = False

        # 2.3.10.2
        try:
            audit_result["2.3.10.2"] = {}
            audit_result["2.3.10.2"]["value"] = audit_file["Registry Values"][
                "MACHINE\\SYSTEM\\CurrentControlSet\\Control\\Lsa\\RestrictAnonymousSAM"
            ]
            audit_result["2.3.10.2"]["status"] = (
                audit_file["Registry Values"][
                    "MACHINE\\SYSTEM\\CurrentControlSet\\Control\\Lsa\\RestrictAnonymousSAM"
                ]
                == "1"
            )
        except:
            audit_result["2.3.10.2"] = {}
            audit_result["2.3.10.2"]["value"] = "N/A"
            audit_result["2.3.10.2"]["status"] = False

        # 2.3.10.3
        try:
            audit_result["2.3.10.3"] = {}
            audit_result["2.3.10.3"]["value"] = audit_file["Registry Values"][
                "MACHINE\\SYSTEM\\CurrentControlSet\\Control\\Lsa\\RestrictAnonymous"
            ]
            audit_result["2.3.10.3"]["status"] = (
                audit_file["Registry Values"][
                    "MACHINE\\SYSTEM\\CurrentControlSet\\Control\\Lsa\\RestrictAnonymous"
                ]
                == "0"
            )
        except:
            audit_result["2.3.10.3"] = {}
            audit_result["2.3.10.3"]["value"] = "N/A"
            audit_result["2.3.10.3"]["status"] = False

        # 2.3.10.5
        try:
            audit_result["2.3.10.5"] = {}
            audit_result["2.3.10.5"]["value"] = audit_file["Registry Values"][
                "MACHINE\\SYSTEM\\CurrentControlSet\\Control\\Lsa\\EveryoneIncludesAnonymous"
            ]
            audit_result["2.3.10.5"]["status"] = (
                audit_file["Registry Values"][
                    "MACHINE\\SYSTEM\\CurrentControlSet\\Control\\Lsa\\EveryoneIncludesAnonymous"
                ]
                == "0"
            )
        except:
            audit_result["2.3.10.5"] = {}
            audit_result["2.3.10.5"]["value"] = "N/A"
            audit_result["2.3.10.5"]["status"] = False

        # 2.3.10.7
        try:
            audit_result["2.3.10.7"] = {}
            audit_result["2.3.10.7"]["value"] = audit_file["Registry Values"][
                "MACHINE\\SYSTEM\\CurrentControlSet\\Services\\LanmanServer\\Parameters\\NullSessionPipes"
            ]
            audit_result["2.3.10.7"]["status"] = (
                audit_file["Registry Values"][
                    "MACHINE\\SYSTEM\\CurrentControlSet\\Services\\LanmanServer\\Parameters\\NullSessionPipes"
                ]
                == ""
            )
        except:
            audit_result["2.3.10.7"] = {}
            audit_result["2.3.10.7"]["value"] = "N/A"
            audit_result["2.3.10.7"]["status"] = False

        # 2.3.10.8
        try:
            audit_result["2.3.10.8"] = {}
            audit_result["2.3.10.8"]["value"] = audit_file["Registry Values"][
                "MACHINE\\SYSTEM\\CurrentControlSet\\Control\\SecurePipeServers\\winreg\\AllowedExactPaths\\Machine"
            ]
            audit_result["2.3.10.8"]["status"] = (
                audit_file["Registry Values"][
                    "MACHINE\\SYSTEM\\CurrentControlSet\\Control\\SecurePipeServers\\winreg\\AllowedExactPaths\\Machine"
                ]
                == "System\\CurrentControlSet\\Control\\ProductOptions,System\\CurrentControlSet\\Control\\Server Applications,Software\\Microsoft\\Windows NT\\CurrentVersion"
            )
        except:
            audit_result["2.3.10.8"] = {}
            audit_result["2.3.10.8"]["value"] = "N/A"
            audit_result["2.3.10.8"]["status"] = False

        # 2.3.10.9
        try:
            audit_result["2.3.10.9"] = {}
            audit_result["2.3.10.9"]["value"] = audit_file["Registry Values"][
                "MACHINE\\SYSTEM\\CurrentControlSet\\Control\\SecurePipeServers\\winreg\\AllowedPaths\\Machine"
            ]
            audit_result["2.3.10.9"]["status"] = (
                audit_file["Registry Values"][
                    "MACHINE\\SYSTEM\\CurrentControlSet\\Control\\SecurePipeServers\\winreg\\AllowedPaths\\Machine"
                ]
                == """
                System\\CurrentControlSet\\Control\\Print\\Printers,System\\CurrentControlSet\\Services\\Eventlog,Software\\Microsoft\\OLAP Server,Software\\Microsoft\\Windows NT\\CurrentVersion\\Print,Software\\Microsoft\\Windows NT\\CurrentVersion\\Windows,System\\CurrentControlSet\\Control\\ContentIndex,System\\CurrentControlSet\\Control\\Terminal Server,System\\CurrentControlSet\\Control\\Terminal Server\\UserConfig,System\\CurrentControlSet\\Control\\Terminal Server\\DefaultUserConfiguration,Software\\Microsoft\\Windows NT\\CurrentVersion\\Perflib,System\\CurrentControlSet\\Services\\SysmonLog
                """
            )
        except:
            audit_result["2.3.10.9"] = {}
            audit_result["2.3.10.9"]["value"] = "N/A"
            audit_result["2.3.10.9"]["status"] = False

        # 2.3.10.10
        try:
            audit_result["2.3.10.10"] = {}
            audit_result["2.3.10.10"]["value"] = audit_file["Registry Values"][
                "MACHINE\\SYSTEM\\CurrentControlSet\\Services\\LanmanServer\\Parameters\\RestrictNullSessAccess"
            ]
            audit_result["2.3.10.10"]["status"] = (
                audit_file["Registry Values"][
                    "MACHINE\\SYSTEM\\CurrentControlSet\\Services\\LanmanServer\\Parameters\\RestrictNullSessAccess"
                ]
                == "0"
            )
        except:
            audit_result["2.3.10.10"] = {}
            audit_result["2.3.10.10"]["value"] = "N/A"
            audit_result["2.3.10.10"]["status"] = False

        # 2.3.10.11
        try:
            audit_result["2.3.10.11"] = {}
            audit_result["2.3.10.11"]["value"] = audit_file["Registry Values"][
                "MACHINE\\SYSTEM\\CurrentControlSet\\Control\\Lsa\\restrictremotesam"
            ]
            audit_result["2.3.10.11"]["status"] = (
                audit_file["Registry Values"][
                    "MACHINE\\SYSTEM\\CurrentControlSet\\Control\\Lsa\\restrictremotesam"
                ]
                == "0"
            )
        except:
            audit_result["2.3.10.11"] = {}
            audit_result["2.3.10.11"]["value"] = "N/A"
            audit_result["2.3.10.11"]["status"] = False

        # 2.3.10.12
        try:
            audit_result["2.3.10.12"] = {}
            audit_result["2.3.10.12"]["value"] = audit_file["Registry Values"][
                "MACHINE\\SYSTEM\\CurrentControlSet\\Services\\LanmanServer\\Parameters\\NullSessionShares"
            ]
            audit_result["2.3.10.12"]["status"] = (
                audit_file["Registry Values"][
                    "MACHINE\\SYSTEM\\CurrentControlSet\\Services\\LanmanServer\\Parameters\\NullSessionShares"
                ]
                == ""
            )
        except:
            audit_result["2.3.10.12"] = {}
            audit_result["2.3.10.12"]["value"] = "N/A"
            audit_result["2.3.10.12"]["status"] = False

        # 2.3.10.13
        try:
            audit_result["2.3.10.13"] = {}
            audit_result["2.3.10.13"]["value"] = audit_file["Registry Values"][
                "MACHINE\\SYSTEM\\CurrentControlSet\\Control\\Lsa\\ForceGuest"
            ]
            audit_result["2.3.10.13"]["status"] = (
                audit_file["Registry Values"][
                    "MACHINE\\SYSTEM\\CurrentControlSet\\Control\\Lsa\\ForceGuest"
                ]
                == "0"
            )
        except:
            audit_result["2.3.10.13"] = {}
            audit_result["2.3.10.13"]["value"] = "N/A"
            audit_result["2.3.10.13"]["status"] = False

        # 2.3.10.14
        try:
            audit_result["2.3.10.14"] = {}
            audit_result["2.3.10.14"]["value"] = audit_file["Registry Values"][
                "MACHINE\\SYSTEM\\CurrentControlSet\\Control\\Lsa\\DisableDomainCreds"
            ]
            audit_result["2.3.10.14"]["status"] = (
                audit_file["Registry Values"][
                    "MACHINE\\SYSTEM\\CurrentControlSet\\Control\\Lsa\\DisableDomainCreds"
                ]
                == "1"
            )
        except:
            audit_result["2.3.10.14"] = {}
            audit_result["2.3.10.14"]["value"] = "N/A"
            audit_result["2.3.10.14"]["status"] = False

        # 2.3.11.1
        try:
            audit_result["2.3.11.1"] = {}
            audit_result["2.3.11.1"]["value"] = audit_file["Registry Values"][
                "MACHINE\\SYSTEM\\CurrentControlSet\\Control\\Lsa\\UseMachineId"
            ]
            audit_result["2.3.11.1"]["status"] = (
                audit_file["Registry Values"][
                    "MACHINE\\SYSTEM\\CurrentControlSet\\Control\\Lsa\\UseMachineId"
                ]
                == "1"
            )
        except:
            audit_result["2.3.11.1"] = {}
            audit_result["2.3.11.1"]["value"] = "N/A"
            audit_result["2.3.11.1"]["status"] = False

        # 2.3.11.2
        try:
            audit_result["2.3.11.2"] = {}
            audit_result["2.3.11.2"]["value"] = audit_file["Registry Values"][
                "MACHINE\\SYSTEM\\CurrentControlSet\\Control\\Lsa\\MSV1_0\\AllowNullSessionFallback"
            ]
            audit_result["2.3.11.2"]["status"] = (
                audit_file["Registry Values"][
                    "MACHINE\\SYSTEM\\CurrentControlSet\\Control\\Lsa\\MSV1_0\\AllowNullSessionFallback"
                ]
                == "0"
            )
        except:
            audit_result["2.3.11.2"] = {}
            audit_result["2.3.11.2"]["value"] = "N/A"
            audit_result["2.3.11.2"]["status"] = False

        # 2.3.11.3
        try:
            audit_result["2.3.11.3"] = {}
            audit_result["2.3.11.3"]["value"] = audit_file["Registry Values"][
                "MACHINE\\SYSTEM\\CurrentControlSet\\Control\\Lsa\\pku2u\\AllowOnlineID"
            ]
            audit_result["2.3.11.3"]["status"] = (
                audit_file["Registry Values"][
                    "MACHINE\\SYSTEM\\CurrentControlSet\\Control\\Lsa\\pku2u\\AllowOnlineID"
                ]
                == "0"
            )
        except:
            audit_result["2.3.11.3"] = {}
            audit_result["2.3.11.3"]["value"] = "N/A"
            audit_result["2.3.11.3"]["status"] = False

        # 2.3.11.4
        try:
            audit_result["2.3.11.4"] = {}
            audit_result["2.3.11.4"]["value"] = audit_file["Registry Values"][
                "MACHINE\\SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\Policies\\System\\Kerberos\\Parameters\\SupportedEncryptionTypes"
            ]
            audit_result["2.3.11.4"]["status"] = (
                audit_file["Registry Values"][
                    "MACHINE\\SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\Policies\\System\\Kerberos\\Parameters\\SupportedEncryptionTypes"
                ]
                == "2147483640"
            )
        except:
            audit_result["2.3.11.4"] = {}
            audit_result["2.3.11.4"]["value"] = "N/A"
            audit_result["2.3.11.4"]["status"] = False

        # 2.3.11.5
        try:
            audit_result["2.3.11.5"] = {}
            audit_result["2.3.11.5"]["value"] = audit_file["Registry Values"][
                "MACHINE\\SYSTEM\\CurrentControlSet\\Control\\Lsa\\NoLMHash"
            ]
            audit_result["2.3.11.5"]["status"] = (
                audit_file["Registry Values"][
                    "MACHINE\\SYSTEM\\CurrentControlSet\\Control\\Lsa\\NoLMHash"
                ]
                == "1"
            )
        except:
            audit_result["2.3.11.5"] = {}
            audit_result["2.3.11.5"]["value"] = "N/A"
            audit_result["2.3.11.5"]["status"] = False

        # 2.3.11.6
        try:
            audit_result["2.3.11.6"] = {}
            audit_result["2.3.11.6"]["value"] = audit_file["Registry Values"][
                "MACHINE\\SYSTEM\\CurrentControlSet\\Services\\LanmanServer\\Parameter\\EnableForcedLogoff"
            ]
            audit_result["2.3.11.6"]["status"] = (
                audit_file["Registry Values"][
                    "MACHINE\\SYSTEM\\CurrentControlSet\\Services\\LanmanServer\\Parameter\\EnableForcedLogoff"
                ]
                == "1"
            )
        except:
            audit_result["2.3.11.6"] = {}
            audit_result["2.3.11.6"]["value"] = "N/A"
            audit_result["2.3.11.6"]["status"] = False

        # 2.3.11.7
        try:
            audit_result["2.3.11.7"] = {}
            audit_result["2.3.11.7"]["value"] = audit_file["Registry Values"][
                "MACHINE\\SYSTEM\\CurrentControlSet\\Control\\Lsa\\LmCompatibilityLevel"
            ]
            audit_result["2.3.11.7"]["status"] = (
                audit_file["Registry Values"][
                    "MACHINE\\SYSTEM\\CurrentControlSet\\Control\\Lsa\\LmCompatibilityLevel"
                ]
                == "1"
            )
        except:
            audit_result["2.3.11.7"] = {}
            audit_result["2.3.11.7"]["value"] = "N/A"
            audit_result["2.3.11.7"]["status"] = False

        # 2.3.11.8
        try:
            audit_result["2.3.11.8"] = {}
            audit_result["2.3.11.8"]["value"] = audit_file["Registry Values"][
                "MACHINE\\SYSTEM\\CurrentControlSet\\Services\\LDAP\\LDAPClientIntegrity"
            ]
            audit_result["2.3.11.8"]["status"] = (
                audit_file["Registry Values"][
                    "MACHINE\\SYSTEM\\CurrentControlSet\\Services\\LDAP\\LDAPClientIntegrity"
                ]
                == "1"
                or audit_file["Registry Values"][
                    "MACHINE\\SYSTEM\\CurrentControlSet\\Services\\LDAP\\LDAPClientIntegrity"
                ]
                == "2"
            )
        except:
            audit_result["2.3.11.8"] = {}
            audit_result["2.3.11.8"]["value"] = "N/A"
            audit_result["2.3.11.8"]["status"] = False

        # 2.3.11.9
        try:
            audit_result["2.3.11.9"] = {}
            audit_result["2.3.11.9"]["value"] = audit_file["Registry Values"][
                "MACHINE\\SYSTEM\\CurrentControlSet\\Control\\Lsa\\MSV1_0\\NTLMMinClientSec"
            ]
            audit_result["2.3.11.9"]["status"] = (
                audit_file["Registry Values"][
                    "MACHINE\\SYSTEM\\CurrentControlSet\\Control\\Lsa\\MSV1_0\\NTLMMinClientSec"
                ]
                == "537395200"
            )
        except:
            audit_result["2.3.11.9"] = {}
            audit_result["2.3.11.9"]["value"] = "N/A"
            audit_result["2.3.11.9"]["status"] = False

        # 2.3.11.10
        try:
            audit_result["2.3.11.10"] = {}
            audit_result["2.3.11.10"]["value"] = audit_file["Registry Values"][
                "MACHINE\\SYSTEM\\CurrentControlSet\\Control\\Lsa\\MSV1_0\\NTLMMinServerSec"
            ]
            audit_result["2.3.11.10"]["status"] = (
                audit_file["Registry Values"][
                    "MACHINE\\SYSTEM\\CurrentControlSet\\Control\\Lsa\\MSV1_0\\NTLMMinServerSec"
                ]
                == "537395200"
            )
        except:
            audit_result["2.3.11.10"] = {}
            audit_result["2.3.11.10"]["value"] = "N/A"
            audit_result["2.3.11.10"]["status"] = False

        # 2.3.13.1
        try:
            audit_result["2.3.13.1"] = {}
            audit_result["2.3.13.1"]["value"] = audit_file["Registry Values"][
                "MACHINE\\SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\Policies\\System\\ShutdownWithoutLogon"
            ]
            audit_result["2.3.13.1"]["status"] = (
                audit_file["Registry Values"][
                    "MACHINE\\SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\Policies\\System\\ShutdownWithoutLogon"
                ]
                == "0"
            )
        except:
            audit_result["2.3.13.1"] = {}
            audit_result["2.3.13.1"]["value"] = "N/A"
            audit_result["2.3.13.1"]["status"] = False

        # 2.3.15.1
        try:
            audit_result["2.3.15.1"] = {}
            audit_result["2.3.15.1"]["value"] = audit_file["Registry Values"][
                "MACHINE\\SYSTEM\\CurrentControlSet\\Control\\Session Manager\\kernel\\ObCaseInsensitive"
            ]
            audit_result["2.3.15.1"]["status"] = (
                audit_file["Registry Values"][
                    "MACHINE\\SYSTEM\\CurrentControlSet\\Control\\Session Manager\\kernel\\ObCaseInsensitive"
                ]
                == "1"
            )
        except:
            audit_result["2.3.15.1"] = {}
            audit_result["2.3.15.1"]["value"] = "N/A"
            audit_result["2.3.15.1"]["status"] = False

        # 2.3.15.2
        try:
            audit_result["2.3.15.2"] = {}
            audit_result["2.3.15.2"]["value"] = audit_file["Registry Values"][
                "MACHINE\\SYSTEM\\CurrentControlSet\\Control\\Session Manager\\ProtectionMode"
            ]
            audit_result["2.3.15.2"]["status"] = (
                audit_file["Registry Values"][
                    "MACHINE\\SYSTEM\\CurrentControlSet\\Control\\Session Manager\\ProtectionMode"
                ]
                == "1"
            )
        except:
            audit_result["2.3.15.2"] = {}
            audit_result["2.3.15.2"]["value"] = "N/A"
            audit_result["2.3.15.2"]["status"] = False

        # 2.3.17.1
        try:
            audit_result["2.3.17.1"] = {}
            audit_result["2.3.17.1"]["value"] = audit_file["Registry Values"][
                "MACHINE\\SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\Policies\\System\\FilterAdministratorToken"
            ]
            audit_result["2.3.17.1"]["status"] = (
                audit_file["Registry Values"][
                    "MACHINE\\SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\Policies\\System\\FilterAdministratorToken"
                ]
                == "1"
            )
        except:
            audit_result["2.3.17.1"] = {}
            audit_result["2.3.17.1"]["value"] = "N/A"
            audit_result["2.3.17.1"]["status"] = False

        # 2.3.17.2
        try:
            audit_result["2.3.17.2"] = {}
            audit_result["2.3.17.2"]["value"] = audit_file["Registry Values"][
                "MACHINE\\SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\Policies\\System\\ConsentPromptBehaviorAdmin"
            ]
            audit_result["2.3.17.2"]["status"] = (
                audit_file["Registry Values"][
                    "MACHINE\\SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\Policies\\System\\ConsentPromptBehaviorAdmin"
                ]
                == "2"
            )
        except:
            audit_result["2.3.17.2"] = {}
            audit_result["2.3.17.2"]["value"] = "N/A"
            audit_result["2.3.17.2"]["status"] = False

        # 2.3.17.3
        try:
            audit_result["2.3.17.3"] = {}
            audit_result["2.3.17.3"]["value"] = audit_file["Registry Values"][
                "MACHINE\\SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\Policies\\System\\ConsentPromptBehaviorUser"
            ]
            audit_result["2.3.17.3"]["status"] = (
                audit_file["Registry Values"][
                    "MACHINE\\SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\Policies\\System\\ConsentPromptBehaviorUser"
                ]
                == "0"
            )
        except:
            audit_result["2.3.17.3"] = {}
            audit_result["2.3.17.3"]["value"] = "N/A"
            audit_result["2.3.17.3"]["status"] = False

        # 2.3.17.4
        try:
            audit_result["2.3.17.4"] = {}
            audit_result["2.3.17.4"]["value"] = audit_file["Registry Values"][
                "MACHINE\\SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\Policies\\System\\EnableInstallerDetection"
            ]
            audit_result["2.3.17.4"]["status"] = (
                audit_file["Registry Values"][
                    "MACHINE\\SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\Policies\\System\\EnableInstallerDetection"
                ]
                == "1"
            )
        except:
            audit_result["2.3.17.4"] = {}
            audit_result["2.3.17.4"]["value"] = "N/A"
            audit_result["2.3.17.4"]["status"] = False

        # 2.3.17.5
        try:
            audit_result["2.3.17.5"] = {}
            audit_result["2.3.17.5"]["value"] = audit_file["Registry Values"][
                "MACHINE\\SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\Policies\\System\\EnableSecureUIAPaths"
            ]
            audit_result["2.3.17.5"]["status"] = (
                audit_file["Registry Values"][
                    "MACHINE\\SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\Policies\\System\\EnableSecureUIAPaths"
                ]
                == "1"
            )
        except:
            audit_result["2.3.17.5"] = {}
            audit_result["2.3.17.5"]["value"] = "N/A"
            audit_result["2.3.17.5"]["status"] = False

        # 2.3.17.6
        try:
            audit_result["2.3.17.6"] = {}
            audit_result["2.3.17.6"]["value"] = audit_file["Registry Values"][
                "MACHINE\\SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\Policies\\System\\EnableLUA"
            ]
            audit_result["2.3.17.6"]["status"] = (
                audit_file["Registry Values"][
                    "MACHINE\\SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\Policies\\System\\EnableLUA"
                ]
                == "1"
            )
        except:
            audit_result["2.3.17.6"] = {}
            audit_result["2.3.17.6"]["value"] = "N/A"
            audit_result["2.3.17.6"]["status"] = False

        # 2.3.17.7
        try:
            audit_result["2.3.17.7"] = {}
            audit_result["2.3.17.7"]["value"] = audit_file["Registry Values"][
                "MACHINE\\SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\Policies\\System\\PromptOnSecureDesktop"
            ]
            audit_result["2.3.17.7"]["status"] = (
                audit_file["Registry Values"][
                    "MACHINE\\SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\Policies\\System\\PromptOnSecureDesktop"
                ]
                == "1"
            )
        except:
            audit_result["2.3.17.7"] = {}
            audit_result["2.3.17.7"]["value"] = "N/A"
            audit_result["2.3.17.7"]["status"] = False

        # 2.3.17.8
        try:
            audit_result["2.3.17.8"] = {}
            audit_result["2.3.17.8"]["value"] = audit_file["Registry Values"][
                "MACHINE\\SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\Policies\\System\\EnableVirtualization"
            ]
            audit_result["2.3.17.8"]["status"] = (
                audit_file["Registry Values"][
                    "MACHINE\\SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\Policies\\System\\EnableVirtualization"
                ]
                == "1"
            )
        except:
            audit_result["2.3.17.8"] = {}
            audit_result["2.3.17.8"]["value"] = "N/A"
            audit_result["2.3.17.8"]["status"] = False

    except Exception as e:
        return {"error": str(e)}
    return audit_result


@router.get("/audit/{server_id}")
async def get_audit_jobs(server_id: Annotated[str, Path(...)]):
    monogo_client = MongoClient(config["MONGODB_URI"])[config["DB_NAME"]]["server"]
    server = monogo_client.find_one({"_id": ObjectId(server_id)})
    result = audit_cis(server["path"])
    return result


@router.post("/auto-hardening")
async def auto_hardening(job: Job):
    # if not ObjectId.is_valid(job.job_id):
    #     raise HTTPException(status_code=400, detail="invalid object id")
    job = job.model_dump()
    # print(job)
    monogo_client = MongoClient(config["MONGODB_URI"])[config["DB_NAME"]]["server"]
    server = monogo_client.find_one({"_id": ObjectId(job["server_id"])})
    # print(server)
    audit_result = audit_cis(server["path"])
    print(audit_result)
    env = Environment(loader=FileSystemLoader("./templates/cis/hardening/vars"))
    template = env.get_template("main-auto.yml.j2")
    render_file = template.render(audit_result)
    print(render_file)
    # cmd = f"ansible-playbook -i {server['path']+'/hosts'} {server['path']+'/audit/tasks/main.yml'}"
    # print(cmd)
    # asyncio.create_task(run_proc(cmd, job["server_id"]))
    return {"msg": "running"}
