from fastapi import APIRouter, Path, HTTPException
from starlette.websockets import WebSocketState
from dotenv import dotenv_values
from pymongo import MongoClient
from jinja2 import Environment, FileSystemLoader
from fastapi.encoders import jsonable_encoder
from models import *
from typing import List
from bson.objectid import ObjectId
import subprocess, asyncio, logging, re
import configparser
from routers.job import create_hardening_job
from routers.hardening import run_job_auto, send_message_ws

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
                await send_message_ws(out)
                # print(out.decode())
    except Exception as e:
        print(e)
    check_output = result_output.split(b"\n")[-3].decode()
    if "failed=1" in check_output or "unreachable=1" in check_output:
        raise HTTPException(status_code=400, detail="failed to audit")


@router.post("/audit")
async def run_job(job: Job):
    job = job.model_dump()
    monogo_client = MongoClient(config["MONGODB_URI"])[config["DB_NAME"]]["server"]
    server = monogo_client.find_one({"_id": ObjectId(job["server_id"])})
    if server == None:
        raise HTTPException(status_code=404, detail="server not found")
    cmd = f"ansible-playbook -i {server['path']+'/hosts'} {server['path']+'/audit/tasks/main.yml'}"
    # print(cmd)
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
            audit_result["rule_2_2_1"] = {}
            audit_result["rule_2_2_1"]["value"] = audit_file["Privilege Rights"][
                "SeTrustedCredManAccessPrivilege"
            ]
            audit_result["rule_2_2_1"]["status"] = False
        except:
            audit_result["rule_2_2_1"] = {}
            audit_result["rule_2_2_1"]["value"] = "N/A"
            audit_result["rule_2_2_1"]["status"] = True
        # 2.2.3
        try:
            audit_result["rule_2_2_3"] = {}
            audit_result["rule_2_2_3"]["value"] = audit_file["Privilege Rights"][
                "SeNetworkLogonRight"
            ]
            audit_result["rule_2_2_3"]["status"] = (
                audit_file["Privilege Rights"]["SeNetworkLogonRight"]
                == f"{auth_users_sid},{admin_sid}"
            )
        except:
            audit_result["rule_2_2_3"] = {}
            audit_result["rule_2_2_3"]["value"] = "N/A"
            audit_result["rule_2_2_3"]["status"] = False
        # 2.2.4
        try:
            audit_result["rule_2_2_4"] = {}
            audit_result["rule_2_2_4"]["value"] = audit_file["Privilege Rights"][
                "SeTcbPrivilege"
            ]
            audit_result["rule_2_2_4"]["status"] = (
                audit_file["Privilege Rights"]["SeTcbPrivilege"] == ""
            )
        except:
            audit_result["rule_2_2_4"] = {}
            audit_result["rule_2_2_4"]["value"] = "N/A"
            audit_result["rule_2_2_4"]["status"] = True
        # 2.2.6
        try:
            audit_result["rule_2_2_6"] = {}
            audit_result["rule_2_2_6"]["value"] = audit_file["Privilege Rights"][
                "SeIncreaseQuotaPrivilege"
            ]
            audit_result["rule_2_2_6"]["status"] = (
                audit_file["Privilege Rights"]["SeIncreaseQuotaPrivilege"]
                == f"{local_svc_sid},{local_net_sid},{admin_sid}"
            )
        except:
            audit_result["rule_2_2_6"] = {}
            audit_result["rule_2_2_6"]["value"] = "N/A"
            audit_result["rule_2_2_6"]["status"] = False
        # 2.2.7
        try:
            audit_result["rule_2_2_7"] = {}
            audit_result["rule_2_2_7"]["value"] = audit_file["Privilege Rights"][
                "SeInteractiveLogonRight"
            ]
            audit_result["rule_2_2_7"]["status"] = (
                audit_file["Privilege Rights"]["SeInteractiveLogonRight"]
                == f"{admin_sid}"
            )
        except:
            audit_result["rule_2_2_7"] = {}
            audit_result["rule_2_2_7"]["value"] = "N/A"
            audit_result["rule_2_2_7"]["status"] = False
        # 2.2.9
        try:
            audit_result["rule_2_2_9"] = {}
            audit_result["rule_2_2_9"]["value"] = audit_file["Privilege Rights"][
                "SeRemoteInteractiveLogonRight"
            ]
            audit_result["rule_2_2_9"]["status"] = (
                audit_file["Privilege Rights"]["SeRemoteInteractiveLogonRight"]
                == f"{admin_sid},{remote_desktop_sid}"
            )
        except:
            audit_result["rule_2_2_9"] = {}
            audit_result["rule_2_2_9"]["value"] = "N/A"
            audit_result["rule_2_2_9"]["status"] = False
        # 2.2.10
        try:
            audit_result["rule_2_2_10"] = {}
            audit_result["rule_2_2_10"]["value"] = audit_file["Privilege Rights"][
                "SeBackupPrivilege"
            ]
            audit_result["rule_2_2_10"]["status"] = (
                audit_file["Privilege Rights"]["SeBackupPrivilege"] == f"{admin_sid}"
            )
        except:
            audit_result["rule_2_2_10"] = {}
            audit_result["rule_2_2_10"]["value"] = "N/A"
            audit_result["rule_2_2_10"]["status"] = False
        # 2.2.11
        try:
            audit_result["rule_2_2_11"] = {}
            audit_result["rule_2_2_11"]["value"] = audit_file["Privilege Rights"][
                "SeSystemTimePrivilege"
            ]
            audit_result["rule_2_2_11"]["status"] = (
                audit_file["Privilege Rights"]["SeSystemTimePrivilege"]
                == f"{local_svc_sid},{admin_sid}"
            )
        except:
            audit_result["rule_2_2_11"] = {}
            audit_result["rule_2_2_11"]["value"] = "N/A"
            audit_result["rule_2_2_11"]["status"] = False
        # 2.2.12
        try:
            audit_result["rule_2_2_12"] = {}
            audit_result["rule_2_2_12"]["value"] = audit_file["Privilege Rights"][
                "SeTimeZonePrivilege"
            ]
            audit_result["rule_2_2_12"]["status"] = (
                audit_file["Privilege Rights"]["SeTimeZonePrivilege"]
                == f"{local_svc_sid},{admin_sid}"
            )
        except:
            audit_result["rule_2_2_12"] = {}
            audit_result["rule_2_2_12"]["value"] = "N/A"
            audit_result["rule_2_2_12"]["status"] = False
        # 2.2.13
        try:
            audit_result["rule_2_2_13"] = {}
            audit_result["rule_2_2_13"]["value"] = audit_file["Privilege Rights"][
                "SeCreatePagefilePrivilege"
            ]
            audit_result["rule_2_2_13"]["status"] = (
                audit_file["Privilege Rights"]["SeCreatePagefilePrivilege"]
                == f"{admin_sid}"
            )
        except:
            audit_result["rule_2_2_13"] = {}
            audit_result["rule_2_2_13"]["value"] = "N/A"
            audit_result["rule_2_2_13"]["status"] = False
        # 2.2.14
        try:
            audit_result["rule_2_2_14"] = {}
            audit_result["rule_2_2_14"]["value"] = audit_file["Privilege Rights"][
                "SeCreateTokenPrivilege"
            ]
            audit_result["rule_2_2_14"]["status"] = (
                audit_file["Privilege Rights"]["SeCreateTokenPrivilege"] == ""
            )
        except:
            audit_result["rule_2_2_14"] = {}
            audit_result["rule_2_2_14"]["value"] = "N/A"
            audit_result["rule_2_2_14"]["status"] = True
        # 2.2.15
        try:
            audit_result["rule_2_2_15"] = {}
            audit_result["rule_2_2_15"]["value"] = audit_file["Privilege Rights"][
                "SeCreateGlobalPrivilege"
            ]
            audit_result["rule_2_2_15"]["status"] = (
                audit_file["Privilege Rights"]["SeCreateGlobalPrivilege"]
                == f"{local_svc_sid},{local_net_sid},{admin_sid},*S-1-5-6"
            )
        except:
            audit_result["rule_2_2_15"] = {}
            audit_result["rule_2_2_15"]["value"] = "N/A"
            audit_result["rule_2_2_15"]["status"] = False
        # 2.2.16
        try:
            audit_result["rule_2_2_16"] = {}
            audit_result["rule_2_2_16"]["value"] = audit_file["Privilege Rights"][
                "SeCreatePermanentPrivilege"
            ]
            audit_result["rule_2_2_16"]["status"] = (
                audit_file["Privilege Rights"]["SeCreatePermanentPrivilege"] == ""
            )
        except:
            audit_result["rule_2_2_16"] = {}
            audit_result["rule_2_2_16"]["value"] = "N/A"
            audit_result["rule_2_2_16"]["status"] = True
        # 2.2.18
        try:
            audit_result["rule_2_2_18"] = {}
            audit_result["rule_2_2_18"]["value"] = audit_file["Privilege Rights"][
                "SeCreateSymbolicLinkPrivilege"
            ]
            audit_result["rule_2_2_18"]["status"] = (
                audit_file["Privilege Rights"]["SeCreateSymbolicLinkPrivilege"]
                == f"{admin_sid}"
            )
        except:
            audit_result["rule_2_2_18"] = {}
            audit_result["rule_2_2_18"]["value"] = "N/A"
            audit_result["rule_2_2_18"]["status"] = False
        # 2.2.19
        try:
            audit_result["rule_2_2_19"] = {}
            audit_result["rule_2_2_19"]["value"] = audit_file["Privilege Rights"][
                "SeDebugPrivilege"
            ]
            audit_result["rule_2_2_19"]["status"] = (
                audit_file["Privilege Rights"]["SeDebugPrivilege"] == f"{admin_sid}"
            )
        except:
            audit_result["rule_2_2_19"] = {}
            audit_result["rule_2_2_19"]["value"] = "N/A"
            audit_result["rule_2_2_19"]["status"] = False
        # 2.2.21
        try:
            audit_result["rule_2_2_21"] = {}
            audit_result["rule_2_2_21"]["value"] = audit_file["Privilege Rights"][
                "DenyNetworkLogonRight"
            ]
            audit_result["rule_2_2_21"]["status"] = (
                audit_file["Privilege Rights"]["DenyNetworkLogonRight"] == ""
            )
        except:
            audit_result["rule_2_2_21"] = {}
            audit_result["rule_2_2_21"]["value"] = "N/A"
            audit_result["rule_2_2_21"]["status"] = True
        # 2.2.22
        try:
            audit_result["rule_2_2_22"] = {}
            audit_result["rule_2_2_22"]["value"] = audit_file["Privilege Rights"][
                "SeDenyBatchLogonRight"
            ]
            audit_result["rule_2_2_22"]["status"] = (
                audit_file["Privilege Rights"]["SeDenyBatchLogonRight"]
                == f"{guest_sid}"
            )
        except:
            audit_result["rule_2_2_22"] = {}
            audit_result["rule_2_2_22"]["value"] = "N/A"
            audit_result["rule_2_2_22"]["status"] = False
        # 2.2.23
        try:
            audit_result["rule_2_2_23"] = {}
            audit_result["rule_2_2_23"]["value"] = audit_file["Privilege Rights"][
                "SeDenyServiceLogonRight"
            ]
            audit_result["rule_2_2_23"]["status"] = (
                audit_file["Privilege Rights"]["SeDenyServiceLogonRight"]
                == f"{guest_sid}"
            )
        except:
            audit_result["rule_2_2_23"] = {}
            audit_result["rule_2_2_23"]["value"] = "N/A"
            audit_result["rule_2_2_23"]["status"] = False
        # 2.2.24
        try:
            audit_result["rule_2_2_24"] = {}
            audit_result["rule_2_2_24"]["value"] = audit_file["Privilege Rights"][
                "SeDenyInteractiveLogonRight"
            ]
            audit_result["rule_2_2_24"]["status"] = (
                audit_file["Privilege Rights"]["SeDenyInteractiveLogonRight"]
                == f"{guest_sid}"
            )
        except:
            audit_result["rule_2_2_24"] = {}
            audit_result["rule_2_2_24"]["value"] = "N/A"
            audit_result["rule_2_2_24"]["status"] = False
        # 2.2.26
        try:
            audit_result["rule_2_2_26"] = {}
            audit_result["rule_2_2_26"]["value"] = audit_file["Privilege Rights"][
                "SeDenyRemoteInteractiveLogonRight"
            ]
            audit_result["rule_2_2_26"]["status"] = (
                audit_file["Privilege Rights"]["SeDenyRemoteInteractiveLogonRight"]
                == f"*S-1-5-113,{guest_sid}"
            )
        except:
            audit_result["rule_2_2_26"] = {}
            audit_result["rule_2_2_26"]["value"] = "N/A"
            audit_result["rule_2_2_26"]["status"] = False
        # 2.2.28
        try:
            audit_result["rule_2_2_28"] = {}
            audit_result["rule_2_2_28"]["value"] = audit_file["Privilege Rights"][
                "EnableDelegationPrivilege"
            ]
            audit_result["rule_2_2_28"]["status"] = (
                audit_file["Privilege Rights"]["EnableDelegationPrivilege"] == ""
            )
        except:
            audit_result["rule_2_2_28"] = {}
            audit_result["rule_2_2_28"]["value"] = "N/A"
            audit_result["rule_2_2_28"]["status"] = True
        # 2.2.29
        try:
            audit_result["rule_2_2_29"] = {}
            audit_result["rule_2_2_29"]["value"] = audit_file["Privilege Rights"][
                "SeRemoteShutdownPrivilege"
            ]
            audit_result["rule_2_2_29"]["status"] = (
                audit_file["Privilege Rights"]["SeRemoteShutdownPrivilege"]
                == f"{admin_sid}"
            )
        except:
            audit_result["rule_2_2_29"] = {}
            audit_result["rule_2_2_29"]["value"] = "N/A"
            audit_result["rule_2_2_29"]["status"] = False
        # 2.2.30
        try:
            audit_result["rule_2_2_30"] = {}
            audit_result["rule_2_2_30"]["value"] = audit_file["Privilege Rights"][
                "SeAuditPrivilege"
            ]
            audit_result["rule_2_2_30"]["status"] = (
                audit_file["Privilege Rights"]["SeAuditPrivilege"]
                == f"{local_svc_sid},{local_net_sid}"
            )
        except:
            audit_result["rule_2_2_30"] = {}
            audit_result["rule_2_2_30"]["value"] = "N/A"
            audit_result["rule_2_2_30"]["status"] = False
        # 2.2.32
        try:
            audit_result["rule_2_2_32"] = {}
            audit_result["rule_2_2_32"]["value"] = audit_file["Privilege Rights"][
                "SeDelegateSessionUserImpersonatePrivilege"
            ]
            audit_result["rule_2_2_32"]["status"] = (
                audit_file["Privilege Rights"][
                    "SeDelegateSessionUserImpersonatePrivilege"
                ]
                == f"{admin_sid}"
            )
        except:
            audit_result["rule_2_2_32"] = {}
            audit_result["rule_2_2_32"]["value"] = "N/A"
            audit_result["rule_2_2_32"]["status"] = False
        # 2.2.33
        try:
            audit_result["rule_2_2_33"] = {}
            audit_result["rule_2_2_33"]["value"] = audit_file["Privilege Rights"][
                "SeIncreaseBasePriorityPrivilege"
            ]
            audit_result["rule_2_2_33"]["status"] = (
                audit_file["Privilege Rights"]["SeIncreaseBasePriorityPrivilege"]
                == f"{admin_sid},*S-1-5-90-0"
            )
        except:
            audit_result["rule_2_2_33"] = {}
            audit_result["rule_2_2_33"]["value"] = "N/A"
            audit_result["rule_2_2_33"]["status"] = False
        # 2.2.34
        try:
            audit_result["rule_2_2_34"] = {}
            audit_result["rule_2_2_34"]["value"] = audit_file["Privilege Rights"][
                "SeLoadDriverPrivilege"
            ]
            audit_result["rule_2_2_34"]["status"] = (
                audit_file["Privilege Rights"]["SeLoadDriverPrivilege"]
                == f"{admin_sid}"
            )
        except:
            audit_result["rule_2_2_34"] = {}
            audit_result["rule_2_2_34"]["value"] = "N/A"
            audit_result["rule_2_2_34"]["status"] = False
        # 2.2.35
        try:
            audit_result["rule_2_2_35"] = {}
            audit_result["rule_2_2_35"]["value"] = audit_file["Privilege Rights"][
                "SeLockMemoryPrivilege"
            ]
            audit_result["rule_2_2_35"]["status"] = (
                audit_file["Privilege Rights"]["SeLockMemoryPrivilege"] == ""
            )
        except:
            audit_result["rule_2_2_35"] = {}
            audit_result["rule_2_2_35"]["value"] = "N/A"
            audit_result["rule_2_2_35"]["status"] = True
        # 2.2.38
        try:
            audit_result["rule_2_2_38"] = {}
            audit_result["rule_2_2_38"]["value"] = audit_file["Privilege Rights"][
                "SeSecurityPrivilege"
            ]
            audit_result["rule_2_2_38"]["status"] = (
                audit_file["Privilege Rights"]["SeSecurityPrivilege"] == f"{admin_sid}"
            )
        except:
            audit_result["rule_2_2_38"] = {}
            audit_result["rule_2_2_38"]["value"] = "N/A"
            audit_result["rule_2_2_38"]["status"] = False
        # 2.2.39
        try:
            audit_result["rule_2_2_39"] = {}
            audit_result["rule_2_2_39"]["value"] = audit_file["Privilege Rights"][
                "SeReLabelPrivilege"
            ]
            audit_result["rule_2_2_39"]["status"] = (
                audit_file["Privilege Rights"]["SeReLabelPrivilege"] == ""
            )
        except:
            audit_result["rule_2_2_39"] = {}
            audit_result["rule_2_2_39"]["value"] = "N/A"
            audit_result["rule_2_2_39"]["status"] = True
        # 2.2.40
        try:
            audit_result["rule_2_2_40"] = {}
            audit_result["rule_2_2_40"]["value"] = audit_file["Privilege Rights"][
                "SeSystemEnvironmentPrivilege"
            ]
            audit_result["rule_2_2_40"]["status"] = (
                audit_file["Privilege Rights"]["SeSystemEnvironmentPrivilege"]
                == f"{admin_sid}"
            )
        except:
            audit_result["rule_2_2_40"] = {}
            audit_result["rule_2_2_40"]["value"] = "N/A"
            audit_result["rule_2_2_40"]["status"] = False
        # 2.2.41
        try:
            audit_result["rule_2_2_41"] = {}
            audit_result["rule_2_2_41"]["value"] = audit_file["Privilege Rights"][
                "SeManageVolumePrivilege"
            ]
            audit_result["rule_2_2_41"]["status"] = (
                audit_file["Privilege Rights"]["SeManageVolumePrivilege"]
                == f"{admin_sid}"
            )
        except:
            audit_result["rule_2_2_41"] = {}
            audit_result["rule_2_2_41"]["value"] = "N/A"
            audit_result["rule_2_2_41"]["status"] = False
        # 2.2.42
        try:
            audit_result["rule_2_2_42"] = {}
            audit_result["rule_2_2_42"]["value"] = audit_file["Privilege Rights"][
                "SeProfileSingleProcessPrivilege"
            ]
            audit_result["rule_2_2_42"]["status"] = (
                audit_file["Privilege Rights"]["SeProfileSingleProcessPrivilege"]
                == f"{admin_sid}"
            )
        except:
            audit_result["rule_2_2_42"] = {}
            audit_result["rule_2_2_42"]["value"] = "N/A"
            audit_result["rule_2_2_42"]["status"] = False
        # 2.2.43
        try:
            audit_result["rule_2_2_43"] = {}
            audit_result["rule_2_2_43"]["value"] = audit_file["Privilege Rights"][
                "SeSystemProfilePrivilege"
            ]
            check_2_2_43 = audit_file["Privilege Rights"][
                "SeSystemProfilePrivilege"
            ].split(",")
            audit_result["rule_2_2_43"]["status"] = (
                check_2_2_43[0] == f"{admin_sid}" and f"{nt_svc_sid}" in check_2_2_43[1]
            )
            # print(re.match(f"{nt_svc_sid}", check_2_2_43[1]))

        except:
            audit_result["rule_2_2_43"] = {}
            audit_result["rule_2_2_43"]["value"] = "N/A"
            audit_result["rule_2_2_43"]["status"] = False
        # 2.2.44
        try:
            audit_result["rule_2_2_44"] = {}
            audit_result["rule_2_2_44"]["value"] = audit_file["Privilege Rights"][
                "SeAssignPrimaryTokenPrivilege"
            ]
            audit_result["rule_2_2_44"]["status"] = (
                audit_file["Privilege Rights"]["SeAssignPrimaryTokenPrivilege"]
                == f"{local_svc_sid},{local_net_sid}"
            )
        except:
            audit_result["rule_2_2_44"] = {}
            audit_result["rule_2_2_44"]["value"] = "N/A"
            audit_result["rule_2_2_44"]["status"] = False
        # 2.2.46
        try:
            audit_result["rule_2_2_46"] = {}
            audit_result["rule_2_2_46"]["value"] = audit_file["Privilege Rights"][
                "SeShutdownPrivilege"
            ]
            audit_result["rule_2_2_46"]["status"] = (
                audit_file["Privilege Rights"]["SeShutdownPrivilege"]
                == f"{admin_sid},{backup_sid}"
            )
        except:
            audit_result["rule_2_2_46"] = {}
            audit_result["rule_2_2_46"]["value"] = "N/A"
            audit_result["rule_2_2_46"]["status"] = False
        # 2.2.48
        try:
            audit_result["rule_2_2_48"] = {}
            audit_result["rule_2_2_48"]["value"] = audit_file["Privilege Rights"][
                "SeTakeOwnershipPrivilege"
            ]
            audit_result["rule_2_2_48"]["status"] = (
                audit_file["Privilege Rights"]["SeTakeOwnershipPrivilege"]
                == f"{admin_sid}"
            )
        except:
            audit_result["rule_2_2_48"] = {}
            audit_result["rule_2_2_48"]["value"] = "N/A"
            audit_result["rule_2_2_48"]["status"] = False
        # 2.3.1.1
        try:
            audit_result["rule_2_3_1_1"] = {}
            audit_result["rule_2_3_1_1"]["value"] = audit_file["System Access"][
                "EnableAdminAccount"
            ]
            audit_result["rule_2_3_1_1"]["status"] = (
                audit_file["System Access"]["EnableAdminAccount"] == "1"
            )
        except:
            audit_result["rule_2_3_1_1"] = {}
            audit_result["rule_2_3_1_1"]["value"] = "N/A"
            audit_result["rule_2_3_1_1"]["status"] = False
        # 2.3.1.2
        try:
            audit_result["rule_2_3_1_2"] = {}
            audit_result["rule_2_3_1_2"]["value"] = audit_file["Registry Values"][
                "MACHINE\\SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\Policies\\System\\NoConnectedUser"
            ]
            audit_result["rule_2_3_1_2"]["status"] = (
                audit_file["Registry Values"][
                    "MACHINE\\SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\Policies\\System\\NoConnectedUser"
                ]
                == "4,3"
            )
        except:
            audit_result["rule_2_3_1_2"] = {}
            audit_result["rule_2_3_1_2"]["value"] = "N/A"
            audit_result["rule_2_3_1_2"]["status"] = False
        # 2.3.1.3
        try:
            audit_result["rule_2_3_1_3"] = {}
            audit_result["rule_2_3_1_3"]["value"] = audit_file["System Access"][
                "EnableGuestAccount"
            ]
            audit_result["rule_2_3_1_3"]["status"] = (
                audit_file["System Access"]["EnableGuestAccount"] == "0"
            )
        except:
            audit_result["rule_2_3_1_3"] = {}
            audit_result["rule_2_3_1_3"]["value"] = "N/A"
            audit_result["rule_2_3_1_3"]["status"] = False
        # 2.3.1.4
        try:
            audit_result["rule_2_3_1_4"] = {}
            audit_result["rule_2_3_1_4"]["value"] = audit_file["Registry Values"][
                "MACHINE\\SYSTEM\\CurrentControlSet\\Control\\Lsa\\LimitBlankPasswordUse"
            ]
            audit_result["rule_2_3_1_4"]["status"] = (
                audit_file["Registry Values"][
                    "MACHINE\\SYSTEM\\CurrentControlSet\\Control\\Lsa\\LimitBlankPasswordUse"
                ]
                == "4,1"
            )
        except:
            audit_result["rule_2_3_1_4"] = {}
            audit_result["rule_2_3_1_4"]["value"] = "N/A"
            audit_result["rule_2_3_1_4"]["status"] = False
        # 2.3.1.5
        try:
            audit_result["rule_2_3_1_5"] = {}
            audit_result["rule_2_3_1_5"]["value"] = audit_file["System Access"][
                "NewAdministratorName"
            ].replace('"', "")
            audit_result["rule_2_3_1_5"]["status"] = (
                audit_file["System Access"]["NewAdministratorName"].replace('"', "")
                != "Administrator"
            )
        except:
            audit_result["rule_2_3_1_5"] = {}
            audit_result["rule_2_3_1_5"]["value"] = "N/A"
            audit_result["rule_2_3_1_5"]["status"] = False
        # 2.3.1.6
        try:
            audit_result["rule_2_3_1_6"] = {}
            audit_result["rule_2_3_1_6"]["value"] = audit_file["System Access"][
                "NewGuestName"
            ].replace('"', "")
            audit_result["rule_2_3_1_6"]["status"] = (
                audit_file["System Access"]["NewGuestName"].replace('"', "") != "Guest"
            )
        except:
            audit_result["rule_2_3_1_6"] = {}
            audit_result["rule_2_3_1_6"]["value"] = "N/A"
            audit_result["rule_2_3_1_6"]["status"] = False
        # 2.3.2.1
        try:
            audit_result["rule_2_3_2_1"] = {}
            audit_result["rule_2_3_2_1"]["value"] = audit_file["Registry Values"][
                "MACHINE\\SYSTEM\\CurrentControlSet\\Control\\Lsa\\SCENoApplyLegacyAuditPolicy"
            ]
            audit_result["rule_2_3_2_1"]["status"] = (
                audit_file["Registry Values"][
                    "MACHINE\\SYSTEM\\CurrentControlSet\\Control\\Lsa\\SCENoApplyLegacyAuditPolicy"
                ]
                == "4,1"
            )
        except:
            audit_result["rule_2_3_2_1"] = {}
            audit_result["rule_2_3_2_1"]["value"] = "N/A"
            audit_result["rule_2_3_2_1"]["status"] = False

        # 2.3.2.2
        try:
            audit_result["rule_2_3_2_2"] = {}
            audit_result["rule_2_3_2_2"]["value"] = audit_file["Registry Values"][
                "MACHINE\\SYSTEM\\CurrentControlSet\\Control\\Lsa\\CrashOnAuditFail"
            ]
            audit_result["rule_2_3_2_2"]["status"] = (
                audit_file["Registry Values"][
                    "MACHINE\\SYSTEM\\CurrentControlSet\\Control\\Lsa\\CrashOnAuditFail"
                ]
                == "4,0"
            )
        except:
            audit_result["rule_2_3_2_2"] = {}
            audit_result["rule_2_3_2_2"]["value"] = "N/A"
            audit_result["rule_2_3_2_2"]["status"] = False

        # 2.3.4.1
        try:
            audit_result["rule_2_3_4_1"] = {}
            audit_result["rule_2_3_4_1"]["value"] = audit_file["Registry Values"][
                "MACHINE\\Software\\Microsoft\\Windows NT\\CurrentVersion\\Winlogon\\AllocateDASD"
            ].replace('"', "")
            audit_result["rule_2_3_4_1"]["status"] = (
                audit_file["Registry Values"][
                    "MACHINE\\Software\\Microsoft\\Windows NT\\CurrentVersion\\Winlogon\\AllocateDASD"
                ].replace('"', "")
                == "1,0"
            )
        except:
            audit_result["rule_2_3_4_1"] = {}
            audit_result["rule_2_3_4_1"]["value"] = "N/A"
            audit_result["rule_2_3_4_1"]["status"] = False

        # 2.3.4.2
        try:
            audit_result["rule_2_3_4_2"] = {}
            audit_result["rule_2_3_4_2"]["value"] = audit_file["Registry Values"][
                "MACHINE\\System\\CurrentControlSet\\Control\\Print\\Providers\\LanMan Print Services\\Servers\\AddPrinterDrivers"
            ]
            audit_result["rule_2_3_4_2"]["status"] = (
                audit_file["Registry Values"][
                    "MACHINE\\System\\CurrentControlSet\\Control\\Print\\Providers\\LanMan Print Services\\Servers\\AddPrinterDrivers"
                ]
                == "4,1"
            )
        except:
            audit_result["rule_2_3_4_2"] = {}
            audit_result["rule_2_3_4_2"]["value"] = "N/A"
            audit_result["rule_2_3_4_2"]["status"] = False

        # 2.3.6.1
        try:
            audit_result["rule_2_3_6_1"] = {}
            audit_result["rule_2_3_6_1"]["value"] = audit_file["Registry Values"][
                "MACHINE\\System\\CurrentControlSet\\Services\\Netlogon\\Parameters\\RequireSignOrSeal"
            ]
            audit_result["rule_2_3_6_1"]["status"] = (
                audit_file["Registry Values"][
                    "MACHINE\\System\\CurrentControlSet\\Services\\Netlogon\\Parameters\\RequireSignOrSeal"
                ]
                == "4,1"
            )
        except:
            audit_result["rule_2_3_6_1"] = {}
            audit_result["rule_2_3_6_1"]["value"] = "N/A"
            audit_result["rule_2_3_6_1"]["status"] = False

        # 2.3.6.2
        try:
            audit_result["rule_2_3_6_2"] = {}
            audit_result["rule_2_3_6_2"]["value"] = audit_file["Registry Values"][
                "MACHINE\\System\\CurrentControlSet\\Services\\Netlogon\\Parameters\\SealSecureChannel"
            ]
            audit_result["rule_2_3_6_2"]["status"] = (
                audit_file["Registry Values"][
                    "MACHINE\\System\\CurrentControlSet\\Services\\Netlogon\\Parameters\\SealSecureChannel"
                ]
                == "4,1"
            )
        except:
            audit_result["rule_2_3_6_2"] = {}
            audit_result["rule_2_3_6_2"]["value"] = "N/A"
            audit_result["rule_2_3_6_2"]["status"] = False

        # 2.3.6.3
        try:
            audit_result["rule_2_3_6_3"] = {}
            audit_result["rule_2_3_6_3"]["value"] = audit_file["Registry Values"][
                "MACHINE\\System\\CurrentControlSet\\Services\\Netlogon\\Parameters\\SignSecureChannel"
            ]
            audit_result["rule_2_3_6_3"]["status"] = (
                audit_file["Registry Values"][
                    "MACHINE\\System\\CurrentControlSet\\Services\\Netlogon\\Parameters\\SignSecureChannel"
                ]
                == "4,1"
            )
        except:
            audit_result["rule_2_3_6_3"] = {}
            audit_result["rule_2_3_6_3"]["value"] = "N/A"
            audit_result["rule_2_3_6_3"]["status"] = False

        # 2.3.6.4
        try:
            audit_result["rule_2_3_6_4"] = {}
            audit_result["rule_2_3_6_4"]["value"] = audit_file["Registry Values"][
                "MACHINE\\System\\CurrentControlSet\\Services\\Netlogon\\Parameters\\DisablePasswordChange"
            ]
            audit_result["rule_2_3_6_4"]["status"] = (
                audit_file["Registry Values"][
                    "MACHINE\\System\\CurrentControlSet\\Services\\Netlogon\\Parameters\\DisablePasswordChange"
                ]
                == "4,0"
            )
        except:
            audit_result["rule_2_3_6_4"] = {}
            audit_result["rule_2_3_6_4"]["value"] = "N/A"
            audit_result["rule_2_3_6_4"]["status"] = False

        # 2.3.6.5
        try:
            audit_result["rule_2_3_6_5"] = {}
            audit_result["rule_2_3_6_5"]["value"] = audit_file["Registry Values"][
                "MACHINE\\System\\CurrentControlSet\\Services\\Netlogon\\Parameters\\MaximumPasswordAge"
            ]
            audit_result["rule_2_3_6_5"]["status"] = (
                audit_file["Registry Values"][
                    "MACHINE\\System\\CurrentControlSet\\Services\\Netlogon\\Parameters\\MaximumPasswordAge"
                ]
                == "4,30"
            )
        except:
            audit_result["rule_2_3_6_5"] = {}
            audit_result["rule_2_3_6_5"]["value"] = "N/A"
            audit_result["rule_2_3_6_5"]["status"] = False

        # 2.3.6.6
        try:
            audit_result["rule_2_3_6_6"] = {}
            audit_result["rule_2_3_6_6"]["value"] = audit_file["Registry Values"][
                "MACHINE\\System\\CurrentControlSet\\Services\\Netlogon\\Parameters\\RequireStrongKey"
            ]
            audit_result["rule_2_3_6_6"]["status"] = (
                audit_file["Registry Values"][
                    "MACHINE\\System\\CurrentControlSet\\Services\\Netlogon\\Parameters\\RequireStrongKey"
                ]
                == "4,1"
            )
        except:
            audit_result["rule_2_3_6_6"] = {}
            audit_result["rule_2_3_6_6"]["value"] = "N/A"
            audit_result["rule_2_3_6_6"]["status"] = False

        # 2.3.7.1
        try:
            audit_result["rule_2_3_7_1"] = {}
            audit_result["rule_2_3_7_1"]["value"] = audit_file["Registry Values"][
                "MACHINE\\SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\Policies\\System\\DisableCAD"
            ]
            audit_result["rule_2_3_7_1"]["status"] = (
                audit_file["Registry Values"][
                    "MACHINE\\SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\Policies\\System\\DisableCAD"
                ]
                == "4,0"
            )
        except:
            audit_result["rule_2_3_7_1"] = {}
            audit_result["rule_2_3_7_1"]["value"] = "N/A"
            audit_result["rule_2_3_7_1"]["status"] = False

        # 2.3.7.2
        try:
            audit_result["rule_2_3_7_2"] = {}
            audit_result["rule_2_3_7_2"]["value"] = audit_file["Registry Values"][
                "MACHINE\\SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\Policies\\System\\DontDisplayLastUserName"
            ]
            audit_result["rule_2_3_7_2"]["status"] = (
                audit_file["Registry Values"][
                    "MACHINE\\SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\Policies\\System\\DontDisplayLastUserName"
                ]
                == "4,1"
            )
        except:
            audit_result["rule_2_3_7_2"] = {}
            audit_result["rule_2_3_7_2"]["value"] = "N/A"
            audit_result["rule_2_3_7_2"]["status"] = False

        # 2.3.7.3
        try:
            audit_result["rule_2_3_7_3"] = {}
            audit_result["rule_2_3_7_3"]["value"] = audit_file["Registry Values"][
                "MACHINE\\SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\Policies\\System\\InactivityTimeoutSecs"
            ]
            audit_result["rule_2_3_7_3"]["status"] = (
                audit_file["Registry Values"][
                    "MACHINE\\SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\Policies\\System\\InactivityTimeoutSecs"
                ]
                == "4,900"
            )
        except:
            audit_result["rule_2_3_7_3"] = {}
            audit_result["rule_2_3_7_3"]["value"] = "N/A"
            audit_result["rule_2_3_7_3"]["status"] = False

        # 2.3.7.4
        try:
            audit_result["rule_2_3_7_4"] = {}
            audit_result["rule_2_3_7_4"]["value"] = audit_file["Registry Values"][
                "MACHINE\\SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\Policies\\System\\LegalNoticeText"
            ]
            audit_result["rule_2_3_7_4"]["status"] = (
                audit_file["Registry Values"][
                    "MACHINE\\SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\Policies\\System\\LegalNoticeText"
                ]
                != ""
            )
        except:
            audit_result["rule_2_3_7_4"] = {}
            audit_result["rule_2_3_7_4"]["value"] = "N/A"
            audit_result["rule_2_3_7_4"]["status"] = False

        # 2.3.7.5
        try:
            audit_result["rule_2_3_7_5"] = {}
            audit_result["rule_2_3_7_5"]["value"] = audit_file["Registry Values"][
                "MACHINE\\SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\Policies\\System\\LegalNoticeCaption"
            ].replace('"', "")
            audit_result["rule_2_3_7_5"]["status"] = (
                audit_file["Registry Values"][
                    "MACHINE\\SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\Policies\\System\\LegalNoticeCaption"
                ].replace('"', "")
                != ""
            )
        except:
            audit_result["rule_2_3_7_5"] = {}
            audit_result["rule_2_3_7_5"]["value"] = "N/A"
            audit_result["rule_2_3_7_5"]["status"] = False

        # 2.3.7.7
        try:
            audit_result["rule_2_3_7_7"] = {}
            audit_result["rule_2_3_7_7"]["value"] = audit_file["Registry Values"][
                "MACHINE\\SOFTWARE\\Microsoft\\Windows NT\\CurrentVersion\\Winlogon\\PasswordExpiryWarning"
            ]
            audit_result["rule_2_3_7_7"]["status"] = (
                audit_file["Registry Values"][
                    "MACHINE\\SOFTWARE\\Microsoft\\Windows NT\\CurrentVersion\\Winlogon\\PasswordExpiryWarning"
                ].split(",")[1]
                >= "5"
                or audit_file["Registry Values"][
                    "MACHINE\\SOFTWARE\\Microsoft\\Windows NT\\CurrentVersion\\Winlogon\\PasswordExpiryWarning"
                ].split(",")[1]
                <= "14"
            )
        except:
            audit_result["rule_2_3_7_7"] = {}
            audit_result["rule_2_3_7_7"]["value"] = "N/A"
            audit_result["rule_2_3_7_7"]["status"] = False

        # 2.3.7.8
        try:
            audit_result["rule_2_3_7_8"] = {}
            audit_result["rule_2_3_7_8"]["value"] = audit_file["Registry Values"][
                "MACHINE\\SOFTWARE\\Microsoft\\Windows NT\\CurrentVersion\\Winlogon\\ForceUnlockLogon"
            ]
            audit_result["rule_2_3_7_8"]["status"] = (
                audit_file["Registry Values"][
                    "MACHINE\\SOFTWARE\\Microsoft\\Windows NT\\CurrentVersion\\Winlogon\\ForceUnlockLogon"
                ]
                == "4,1"
            )
        except:
            audit_result["rule_2_3_7_8"] = {}
            audit_result["rule_2_3_7_8"]["value"] = "N/A"
            audit_result["rule_2_3_7_8"]["status"] = False

        # 2.3.7.9
        try:
            audit_result["rule_2_3_7_9"] = {}
            audit_result["rule_2_3_7_9"]["value"] = (
                audit_file["Registry Values"][
                    "MACHINE\\SOFTWARE\\Microsoft\\Windows NT\\CurrentVersion\\Winlogon\\ScRemoveOption"
                ]
                .replace('"', "")
                .split(",")[1]
            )
            audit_result["rule_2_3_7_9"]["status"] = (
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
            audit_result["rule_2_3_7_9"] = {}
            audit_result["rule_2_3_7_9"]["value"] = "N/A"
            audit_result["rule_2_3_7_9"]["status"] = False

        # 2.3.8.1
        try:
            audit_result["rule_2_3_8_1"] = {}
            audit_result["rule_2_3_8_1"]["value"] = audit_file["Registry Values"][
                "MACHINE\\SYSTEM\\CurrentControlSet\\Services\\LanmanWorkStation\\Parameters\\RequireSecuritySignature"
            ]
            audit_result["rule_2_3_8_1"]["status"] = (
                audit_file["Registry Values"][
                    "MACHINE\\SYSTEM\\CurrentControlSet\\Services\\LanmanWorkStation\\Parameters\\RequireSecuritySignature"
                ]
                == "4,1"
            )
        except:
            audit_result["rule_2_3_8_1"] = {}
            audit_result["rule_2_3_8_1"]["value"] = "N/A"
            audit_result["rule_2_3_8_1"]["status"] = False

        # 2.3.8.2
        try:
            audit_result["rule_2_3_8_2"] = {}
            audit_result["rule_2_3_8_2"]["value"] = audit_file["Registry Values"][
                "MACHINE\\SYSTEM\\CurrentControlSet\\Services\\LanmanWorkStation\\Parameters\\EnableSecuritySignature"
            ]
            audit_result["rule_2_3_8_2"]["status"] = (
                audit_file["Registry Values"][
                    "MACHINE\\SYSTEM\\CurrentControlSet\\Services\\LanmanWorkStation\\Parameters\\EnableSecuritySignature"
                ]
                == "4,1"
            )
        except:
            audit_result["rule_2_3_8_2"] = {}
            audit_result["rule_2_3_8_2"]["value"] = "N/A"
            audit_result["rule_2_3_8_2"]["status"] = False

        # 2.3.8.3
        try:
            audit_result["rule_2_3_8_3"] = {}
            audit_result["rule_2_3_8_3"]["value"] = audit_file["Registry Values"][
                "MACHINE\\SYSTEM\\CurrentControlSet\\Services\\LanmanWorkStation\\Parameters\\EnablePlainTextPassword"
            ]
            audit_result["rule_2_3_8_3"]["status"] = (
                audit_file["Registry Values"][
                    "MACHINE\\SYSTEM\\CurrentControlSet\\Services\\LanmanWorkStation\\Parameters\\EnablePlainTextPassword"
                ]
                == "4,0"
            )
        except:
            audit_result["rule_2_3_8_3"] = {}
            audit_result["rule_2_3_8_3"]["value"] = "N/A"
            audit_result["rule_2_3_8_3"]["status"] = False

        # 2.3.9.1
        try:
            audit_result["rule_2_3_9_1"] = {}
            audit_result["rule_2_3_9_1"]["value"] = audit_file["Registry Values"][
                "MACHINE\\SYSTEM\\CurrentControlSet\\Services\\LanmanServer\\Parameters\\AutoDisconnect"
            ].split(",")[1]
            audit_result["rule_2_3_9_1"]["status"] = (
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
            audit_result["rule_2_3_9_1"] = {}
            audit_result["rule_2_3_9_1"]["value"] = "N/A"
            audit_result["rule_2_3_9_1"]["status"] = False

        # 2.3.9.2
        try:
            audit_result["rule_2_3_9_2"] = {}
            audit_result["rule_2_3_9_2"]["value"] = audit_file["Registry Values"][
                "MACHINE\\System\\CurrentControlSet\\Services\\LanManServer\\Parameters\\RequireSecuritySignature"
            ]
            audit_result["rule_2_3_9_2"]["status"] = (
                audit_file["Registry Values"][
                    "MACHINE\\System\\CurrentControlSet\\Services\\LanManServer\\Parameters\\RequireSecuritySignature"
                ]
                == "4,1"
            )
        except:
            audit_result["rule_2_3_9_2"] = {}
            audit_result["rule_2_3_9_2"]["value"] = "N/A"
            audit_result["rule_2_3_9_2"]["status"] = False

        # 2.3.9.3
        try:
            audit_result["rule_2_3_9_3"] = {}
            audit_result["rule_2_3_9_3"]["value"] = audit_file["Registry Values"][
                "MACHINE\\System\\CurrentControlSet\\Services\\LanManServer\\Parameters\\EnableSecuritySignature"
            ]
            audit_result["rule_2_3_9_3"]["status"] = (
                audit_file["Registry Values"][
                    "MACHINE\\System\\CurrentControlSet\\Services\\LanManServer\\Parameters\\EnableSecuritySignature"
                ]
                == "4,1"
            )
        except:
            audit_result["rule_2_3_9_3"] = {}
            audit_result["rule_2_3_9_3"]["value"] = "N/A"
            audit_result["rule_2_3_9_3"]["status"] = False

        # 2.3.9.4
        try:
            audit_result["rule_2_3_9_4"] = {}
            audit_result["rule_2_3_9_4"]["value"] = audit_file["Registry Values"][
                "MACHINE\\System\\CurrentControlSet\\Services\\LanManServer\\Parameters\\EnableForcedLogOff"
            ]
            audit_result["rule_2_3_9_4"]["status"] = (
                audit_file["Registry Values"][
                    "MACHINE\\System\\CurrentControlSet\\Services\\LanManServer\\Parameters\\EnableForcedLogOff"
                ]
                == "4,1"
            )
        except:
            audit_result["rule_2_3_9_4"] = {}
            audit_result["rule_2_3_9_4"]["value"] = "N/A"
            audit_result["rule_2_3_9_4"]["status"] = False

        # 2.3.10.1
        try:
            audit_result["rule_2_3_10_1"] = {}
            audit_result["rule_2_3_10_1"]["value"] = audit_file["System Access"][
                "LSAAnonymousNameLookup"
            ]
            audit_result["rule_2_3_10_1"]["status"] = (
                audit_file["System Access"]["LSAAnonymousNameLookup"] == "0"
            )
        except:
            audit_result["rule_2_3_10_1"] = {}
            audit_result["rule_2_3_10_1"]["value"] = "N/A"
            audit_result["rule_2_3_10_1"]["status"] = False

        # 2.3.10.2
        try:
            audit_result["rule_2_3_10_2"] = {}
            audit_result["rule_2_3_10_2"]["value"] = audit_file["Registry Values"][
                "MACHINE\\SYSTEM\\CurrentControlSet\\Control\\Lsa\\RestrictAnonymousSAM"
            ]
            audit_result["rule_2_3_10_2"]["status"] = (
                audit_file["Registry Values"][
                    "MACHINE\\SYSTEM\\CurrentControlSet\\Control\\Lsa\\RestrictAnonymousSAM"
                ]
                == "4,1"
            )
        except:
            audit_result["rule_2_3_10_2"] = {}
            audit_result["rule_2_3_10_2"]["value"] = "N/A"
            audit_result["rule_2_3_10_2"]["status"] = False

        # 2.3.10.3
        try:
            audit_result["rule_2_3_10_3"] = {}
            audit_result["rule_2_3_10_3"]["value"] = audit_file["Registry Values"][
                "MACHINE\\SYSTEM\\CurrentControlSet\\Control\\Lsa\\RestrictAnonymous"
            ]
            audit_result["rule_2_3_10_3"]["status"] = (
                audit_file["Registry Values"][
                    "MACHINE\\SYSTEM\\CurrentControlSet\\Control\\Lsa\\RestrictAnonymous"
                ]
                == "4,1"
            )
        except:
            audit_result["rule_2_3_10_3"] = {}
            audit_result["rule_2_3_10_3"]["value"] = "N/A"
            audit_result["rule_2_3_10_3"]["status"] = False

        # 2.3.10.5
        try:
            audit_result["rule_2_3_10_5"] = {}
            audit_result["rule_2_3_10_5"]["value"] = audit_file["Registry Values"][
                "MACHINE\\SYSTEM\\CurrentControlSet\\Control\\Lsa\\EveryoneIncludesAnonymous"
            ]
            audit_result["rule_2_3_10_5"]["status"] = (
                audit_file["Registry Values"][
                    "MACHINE\\SYSTEM\\CurrentControlSet\\Control\\Lsa\\EveryoneIncludesAnonymous"
                ]
                == "4,0"
            )
        except:
            audit_result["rule_2_3_10_5"] = {}
            audit_result["rule_2_3_10_5"]["value"] = "N/A"
            audit_result["rule_2_3_10_5"]["status"] = False

        # 2.3.10.7
        try:
            audit_result["rule_2_3_10_7"] = {}
            audit_result["rule_2_3_10_7"]["value"] = audit_file["Registry Values"][
                "MACHINE\\SYSTEM\\CurrentControlSet\\Services\\LanmanServer\\Parameters\\NullSessionPipes"
            ]
            audit_result["rule_2_3_10_7"]["status"] = (
                audit_file["Registry Values"][
                    "MACHINE\\SYSTEM\\CurrentControlSet\\Services\\LanmanServer\\Parameters\\NullSessionPipes"
                ]
                == "7,"
            )
        except:
            audit_result["rule_2_3_10_7"] = {}
            audit_result["rule_2_3_10_7"]["value"] = "N/A"
            audit_result["rule_2_3_10_7"]["status"] = False

        # 2.3.10.8
        try:
            audit_result["rule_2_3_10_8"] = {}
            audit_result["rule_2_3_10_8"]["value"] = audit_file["Registry Values"][
                "MACHINE\\SYSTEM\\CurrentControlSet\\Control\\SecurePipeServers\\winreg\\AllowedExactPaths\\Machine"
            ]
            audit_result["rule_2_3_10_8"]["status"] = (
                audit_file["Registry Values"][
                    "MACHINE\\SYSTEM\\CurrentControlSet\\Control\\SecurePipeServers\\winreg\\AllowedExactPaths\\Machine"
                ]
                == "7,System\\CurrentControlSet\\Control\\ProductOptions,System\\CurrentControlSet\\Control\\Server Applications,Software\\Microsoft\\Windows NT\\CurrentVersion"
            )
        except:
            audit_result["rule_2_3_10_8"] = {}
            audit_result["rule_2_3_10_8"]["value"] = "N/A"
            audit_result["rule_2_3_10_8"]["status"] = False

        # 2.3.10.9
        try:
            audit_result["rule_2_3_10_9"] = {}
            audit_result["rule_2_3_10_9"]["value"] = audit_file["Registry Values"][
                "MACHINE\\SYSTEM\\CurrentControlSet\\Control\\SecurePipeServers\\winreg\\AllowedPaths\\Machine"
            ]
            audit_result["rule_2_3_10_9"]["status"] = (
                audit_file["Registry Values"][
                    "MACHINE\\SYSTEM\\CurrentControlSet\\Control\\SecurePipeServers\\winreg\\AllowedPaths\\Machine"
                ]
                == "7,System\\CurrentControlSet\\Control\\Print\\Printers,System\\CurrentControlSet\\Services\\Eventlog,Software\\Microsoft\\OLAP Server,Software\\Microsoft\\Windows NT\\CurrentVersion\\Print,Software\\Microsoft\\Windows NT\\CurrentVersion\\Windows,System\\CurrentControlSet\\Control\\ContentIndex,System\\CurrentControlSet\\Control\\Terminal Server,System\\CurrentControlSet\\Control\\Terminal Server\\UserConfig,System\\CurrentControlSet\\Control\\Terminal Server\\DefaultUserConfiguration,Software\\Microsoft\\Windows NT\\CurrentVersion\\Perflib,System\\CurrentControlSet\\Services\\WINS,System\\CurrentControlSet\\Services\\CertSvc,System\\CurrentControlSet\\Services\\SysmonLog"
            )
        except:
            audit_result["rule_2_3_10_9"] = {}
            audit_result["rule_2_3_10_9"]["value"] = "N/A"
            audit_result["rule_2_3_10_9"]["status"] = False

        # 2.3.10.10
        try:
            audit_result["rule_2_3_10_10"] = {}
            audit_result["rule_2_3_10_10"]["value"] = audit_file["Registry Values"][
                "MACHINE\\SYSTEM\\CurrentControlSet\\Services\\LanmanServer\\Parameters\\RestrictNullSessAccess"
            ]
            audit_result["rule_2_3_10_10"]["status"] = (
                audit_file["Registry Values"][
                    "MACHINE\\SYSTEM\\CurrentControlSet\\Services\\LanmanServer\\Parameters\\RestrictNullSessAccess"
                ]
                == "4,1"
            )
        except:
            audit_result["rule_2_3_10_10"] = {}
            audit_result["rule_2_3_10_10"]["value"] = "N/A"
            audit_result["rule_2_3_10_10"]["status"] = False

        # 2.3.10.11
        try:
            audit_result["rule_2_3_10_11"] = {}
            audit_result["rule_2_3_10_11"]["value"] = audit_file["Registry Values"][
                "MACHINE\\SYSTEM\\CurrentControlSet\\Control\\Lsa\\restrictremotesam"
            ]
            audit_result["rule_2_3_10_11"]["status"] = (
                audit_file["Registry Values"][
                    "MACHINE\\SYSTEM\\CurrentControlSet\\Control\\Lsa\\restrictremotesam"
                ].replace('"', "")
                == "1,O:BAG:BAD:(A;;RC;;;BA)"
            )
        except:
            audit_result["rule_2_3_10_11"] = {}
            audit_result["rule_2_3_10_11"]["value"] = "N/A"
            audit_result["rule_2_3_10_11"]["status"] = False

        # 2.3.10.12
        try:
            audit_result["rule_2_3_10_12"] = {}
            audit_result["rule_2_3_10_12"]["value"] = audit_file["Registry Values"][
                "MACHINE\\SYSTEM\\CurrentControlSet\\Services\\LanmanServer\\Parameters\\NullSessionShares"
            ]
            audit_result["rule_2_3_10_12"]["status"] = (
                audit_file["Registry Values"][
                    "MACHINE\\SYSTEM\\CurrentControlSet\\Services\\LanmanServer\\Parameters\\NullSessionShares"
                ]
                == "7,"
            )
        except:
            audit_result["rule_2_3_10_12"] = {}
            audit_result["rule_2_3_10_12"]["value"] = "N/A"
            audit_result["rule_2_3_10_12"]["status"] = False

        # 2.3.10.13
        try:
            audit_result["rule_2_3_10_13"] = {}
            audit_result["rule_2_3_10_13"]["value"] = audit_file["Registry Values"][
                "MACHINE\\SYSTEM\\CurrentControlSet\\Control\\Lsa\\ForceGuest"
            ]
            audit_result["rule_2_3_10_13"]["status"] = (
                audit_file["Registry Values"][
                    "MACHINE\\SYSTEM\\CurrentControlSet\\Control\\Lsa\\ForceGuest"
                ]
                == "4,0"
            )
        except:
            audit_result["rule_2_3_10_13"] = {}
            audit_result["rule_2_3_10_13"]["value"] = "N/A"
            audit_result["rule_2_3_10_13"]["status"] = False

        # 2.3.11.1
        try:
            audit_result["rule_2_3_11_1"] = {}
            audit_result["rule_2_3_11_1"]["value"] = audit_file["Registry Values"][
                "MACHINE\\SYSTEM\\CurrentControlSet\\Control\\Lsa\\UseMachineId"
            ]
            audit_result["rule_2_3_11_1"]["status"] = (
                audit_file["Registry Values"][
                    "MACHINE\\SYSTEM\\CurrentControlSet\\Control\\Lsa\\UseMachineId"
                ]
                == "4,1"
            )
        except:
            audit_result["rule_2_3_11_1"] = {}
            audit_result["rule_2_3_11_1"]["value"] = "N/A"
            audit_result["rule_2_3_11_1"]["status"] = False

        # 2.3.11.2
        try:
            audit_result["rule_2_3_11_2"] = {}
            audit_result["rule_2_3_11_2"]["value"] = audit_file["Registry Values"][
                "MACHINE\\SYSTEM\\CurrentControlSet\\Control\\Lsa\\MSV1_0\\AllowNullSessionFallback"
            ]
            audit_result["rule_2_3_11_2"]["status"] = (
                audit_file["Registry Values"][
                    "MACHINE\\SYSTEM\\CurrentControlSet\\Control\\Lsa\\MSV1_0\\AllowNullSessionFallback"
                ]
                == "4,0"
            )
        except:
            audit_result["rule_2_3_11_2"] = {}
            audit_result["rule_2_3_11_2"]["value"] = "N/A"
            audit_result["rule_2_3_11_2"]["status"] = False

        # 2.3.11.3
        try:
            audit_result["rule_2_3_11_3"] = {}
            audit_result["rule_2_3_11_3"]["value"] = audit_file["Registry Values"][
                "MACHINE\\SYSTEM\\CurrentControlSet\\Control\\Lsa\\pku2u\\AllowOnlineID"
            ]
            audit_result["rule_2_3_11_3"]["status"] = (
                audit_file["Registry Values"][
                    "MACHINE\\SYSTEM\\CurrentControlSet\\Control\\Lsa\\pku2u\\AllowOnlineID"
                ]
                == "4,0"
            )
        except:
            audit_result["rule_2_3_11_3"] = {}
            audit_result["rule_2_3_11_3"]["value"] = "N/A"
            audit_result["rule_2_3_11_3"]["status"] = False

        # 2.3.11.4
        try:
            audit_result["rule_2_3_11_4"] = {}
            audit_result["rule_2_3_11_4"]["value"] = audit_file["Registry Values"][
                "MACHINE\\SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\Policies\\System\\Kerberos\\Parameters\\SupportedEncryptionTypes"
            ]
            audit_result["rule_2_3_11_4"]["status"] = (
                audit_file["Registry Values"][
                    "MACHINE\\SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\Policies\\System\\Kerberos\\Parameters\\SupportedEncryptionTypes"
                ]
                == "4,2147483640"
            )
        except:
            audit_result["rule_2_3_11_4"] = {}
            audit_result["rule_2_3_11_4"]["value"] = "N/A"
            audit_result["rule_2_3_11_4"]["status"] = False

        # 2.3.11.5
        try:
            audit_result["rule_2_3_11_5"] = {}
            audit_result["rule_2_3_11_5"]["value"] = audit_file["Registry Values"][
                "MACHINE\\SYSTEM\\CurrentControlSet\\Control\\Lsa\\NoLMHash"
            ]
            audit_result["rule_2_3_11_5"]["status"] = (
                audit_file["Registry Values"][
                    "MACHINE\\SYSTEM\\CurrentControlSet\\Control\\Lsa\\NoLMHash"
                ]
                == "4,1"
            )
        except:
            audit_result["rule_2_3_11_5"] = {}
            audit_result["rule_2_3_11_5"]["value"] = "N/A"
            audit_result["rule_2_3_11_5"]["status"] = False

        # 2.3.11.6
        try:
            audit_result["rule_2_3_11_6"] = {}
            audit_result["rule_2_3_11_6"]["value"] = audit_file["Registry Values"][
                "MACHINE\\System\\CurrentControlSet\\Services\\LanManServer\\Parameters\\EnableForcedLogOff"
            ]
            audit_result["rule_2_3_11_6"]["status"] = (
                audit_file["Registry Values"][
                    "MACHINE\\System\\CurrentControlSet\\Services\\LanManServer\\Parameters\\EnableForcedLogOff"
                ]
                == "4,1"
            )
        except:
            audit_result["rule_2_3_11_6"] = {}
            audit_result["rule_2_3_11_6"]["value"] = "N/A"
            audit_result["rule_2_3_11_6"]["status"] = False

        # 2.3.11.7
        try:
            audit_result["rule_2_3_11_7"] = {}
            audit_result["rule_2_3_11_7"]["value"] = audit_file["Registry Values"][
                "MACHINE\\SYSTEM\\CurrentControlSet\\Control\\Lsa\\LmCompatibilityLevel"
            ]
            audit_result["rule_2_3_11_7"]["status"] = (
                audit_file["Registry Values"][
                    "MACHINE\\SYSTEM\\CurrentControlSet\\Control\\Lsa\\LmCompatibilityLevel"
                ]
                == "4,5"
            )
        except:
            audit_result["rule_2_3_11_7"] = {}
            audit_result["rule_2_3_11_7"]["value"] = "N/A"
            audit_result["rule_2_3_11_7"]["status"] = False

        # 2.3.11.8
        try:
            audit_result["rule_2_3_11_8"] = {}
            audit_result["rule_2_3_11_8"]["value"] = audit_file["Registry Values"][
                "MACHINE\\SYSTEM\\CurrentControlSet\\Services\\LDAP\\LDAPClientIntegrity"
            ]
            audit_result["rule_2_3_11_8"]["status"] = (
                audit_file["Registry Values"][
                    "MACHINE\\SYSTEM\\CurrentControlSet\\Services\\LDAP\\LDAPClientIntegrity"
                ].split(",")[1]
                == "1"
                or audit_file["Registry Values"][
                    "MACHINE\\SYSTEM\\CurrentControlSet\\Services\\LDAP\\LDAPClientIntegrity"
                ].split(",")[1]
                == "2"
            )
        except:
            audit_result["rule_2_3_11_8"] = {}
            audit_result["rule_2_3_11_8"]["value"] = "N/A"
            audit_result["rule_2_3_11_8"]["status"] = False

        # 2.3.11.9
        try:
            audit_result["rule_2_3_11_9"] = {}
            audit_result["rule_2_3_11_9"]["value"] = audit_file["Registry Values"][
                "MACHINE\\SYSTEM\\CurrentControlSet\\Control\\Lsa\\MSV1_0\\NTLMMinClientSec"
            ]
            audit_result["rule_2_3_11_9"]["status"] = (
                audit_file["Registry Values"][
                    "MACHINE\\SYSTEM\\CurrentControlSet\\Control\\Lsa\\MSV1_0\\NTLMMinClientSec"
                ]
                == "4,537395200"
            )
        except:
            audit_result["rule_2_3_11_9"] = {}
            audit_result["rule_2_3_11_9"]["value"] = "N/A"
            audit_result["rule_2_3_11_9"]["status"] = False

        # 2.3.11.10
        try:
            audit_result["rule_2_3_11_10"] = {}
            audit_result["rule_2_3_11_10"]["value"] = audit_file["Registry Values"][
                "MACHINE\\SYSTEM\\CurrentControlSet\\Control\\Lsa\\MSV1_0\\NTLMMinServerSec"
            ]
            audit_result["rule_2_3_11_10"]["status"] = (
                audit_file["Registry Values"][
                    "MACHINE\\SYSTEM\\CurrentControlSet\\Control\\Lsa\\MSV1_0\\NTLMMinServerSec"
                ]
                == "4,537395200"
            )
        except:
            audit_result["rule_2_3_11_10"] = {}
            audit_result["rule_2_3_11_10"]["value"] = "N/A"
            audit_result["rule_2_3_11_10"]["status"] = False

        # 2.3.13.1
        try:
            audit_result["rule_2_3_13_1"] = {}
            audit_result["rule_2_3_13_1"]["value"] = audit_file["Registry Values"][
                "MACHINE\\SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\Policies\\System\\ShutdownWithoutLogon"
            ]
            audit_result["rule_2_3_13_1"]["status"] = (
                audit_file["Registry Values"][
                    "MACHINE\\SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\Policies\\System\\ShutdownWithoutLogon"
                ]
                == "4,0"
            )
        except:
            audit_result["rule_2_3_13_1"] = {}
            audit_result["rule_2_3_13_1"]["value"] = "N/A"
            audit_result["rule_2_3_13_1"]["status"] = False

        # 2.3.15.1
        try:
            audit_result["rule_2_3_15_1"] = {}
            audit_result["rule_2_3_15_1"]["value"] = audit_file["Registry Values"][
                "MACHINE\\SYSTEM\\CurrentControlSet\\Control\\Session Manager\\kernel\\ObCaseInsensitive"
            ]
            audit_result["rule_2_3_15_1"]["status"] = (
                audit_file["Registry Values"][
                    "MACHINE\\SYSTEM\\CurrentControlSet\\Control\\Session Manager\\kernel\\ObCaseInsensitive"
                ]
                == "4,1"
            )
        except:
            audit_result["rule_2_3_15_1"] = {}
            audit_result["rule_2_3_15_1"]["value"] = "N/A"
            audit_result["rule_2_3_15_1"]["status"] = False

        # 2.3.15.2
        try:
            audit_result["rule_2_3_15_2"] = {}
            audit_result["rule_2_3_15_2"]["value"] = audit_file["Registry Values"][
                "MACHINE\\SYSTEM\\CurrentControlSet\\Control\\Session Manager\\ProtectionMode"
            ]
            audit_result["rule_2_3_15_2"]["status"] = (
                audit_file["Registry Values"][
                    "MACHINE\\SYSTEM\\CurrentControlSet\\Control\\Session Manager\\ProtectionMode"
                ]
                == "4,1"
            )
        except:
            audit_result["rule_2_3_15_2"] = {}
            audit_result["rule_2_3_15_2"]["value"] = "N/A"
            audit_result["rule_2_3_15_2"]["status"] = False

        # 2.3.17.1
        try:
            audit_result["rule_2_3_17_1"] = {}
            audit_result["rule_2_3_17_1"]["value"] = audit_file["Registry Values"][
                "MACHINE\\SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\Policies\\System\\FilterAdministratorToken"
            ]
            audit_result["rule_2_3_17_1"]["status"] = (
                audit_file["Registry Values"][
                    "MACHINE\\SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\Policies\\System\\FilterAdministratorToken"
                ]
                == "4,1"
            )
        except:
            audit_result["rule_2_3_17_1"] = {}
            audit_result["rule_2_3_17_1"]["value"] = "N/A"
            audit_result["rule_2_3_17_1"]["status"] = False

        # 2.3.17.2
        try:
            audit_result["rule_2_3_17_2"] = {}
            audit_result["rule_2_3_17_2"]["value"] = audit_file["Registry Values"][
                "MACHINE\\SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\Policies\\System\\ConsentPromptBehaviorAdmin"
            ]
            audit_result["rule_2_3_17_2"]["status"] = (
                audit_file["Registry Values"][
                    "MACHINE\\SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\Policies\\System\\ConsentPromptBehaviorAdmin"
                ]
                == "4,2"
            )
        except:
            audit_result["rule_2_3_17_2"] = {}
            audit_result["rule_2_3_17_2"]["value"] = "N/A"
            audit_result["rule_2_3_17_2"]["status"] = False

        # 2.3.17.3
        try:
            audit_result["rule_2_3_17_3"] = {}
            audit_result["rule_2_3_17_3"]["value"] = audit_file["Registry Values"][
                "MACHINE\\SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\Policies\\System\\ConsentPromptBehaviorUser"
            ]
            audit_result["rule_2_3_17_3"]["status"] = (
                audit_file["Registry Values"][
                    "MACHINE\\SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\Policies\\System\\ConsentPromptBehaviorUser"
                ]
                == "4,0"
            )
        except:
            audit_result["rule_2_3_17_3"] = {}
            audit_result["rule_2_3_17_3"]["value"] = "N/A"
            audit_result["rule_2_3_17_3"]["status"] = False

        # 2.3.17.4
        try:
            audit_result["rule_2_3_17_4"] = {}
            audit_result["rule_2_3_17_4"]["value"] = audit_file["Registry Values"][
                "MACHINE\\SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\Policies\\System\\EnableInstallerDetection"
            ]
            audit_result["rule_2_3_17_4"]["status"] = (
                audit_file["Registry Values"][
                    "MACHINE\\SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\Policies\\System\\EnableInstallerDetection"
                ]
                == "4,1"
            )
        except:
            audit_result["rule_2_3_17_4"] = {}
            audit_result["rule_2_3_17_4"]["value"] = "N/A"
            audit_result["rule_2_3_17_4"]["status"] = False

        # 2.3.17.5
        try:
            audit_result["rule_2_3_17_5"] = {}
            audit_result["rule_2_3_17_5"]["value"] = audit_file["Registry Values"][
                "MACHINE\\SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\Policies\\System\\EnableSecureUIAPaths"
            ]
            audit_result["rule_2_3_17_5"]["status"] = (
                audit_file["Registry Values"][
                    "MACHINE\\SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\Policies\\System\\EnableSecureUIAPaths"
                ]
                == "4,1"
            )
        except:
            audit_result["rule_2_3_17_5"] = {}
            audit_result["rule_2_3_17_5"]["value"] = "N/A"
            audit_result["rule_2_3_17_5"]["status"] = False

        # 2.3.17.6
        try:
            audit_result["rule_2_3_17_6"] = {}
            audit_result["rule_2_3_17_6"]["value"] = audit_file["Registry Values"][
                "MACHINE\\SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\Policies\\System\\EnableLUA"
            ]
            audit_result["rule_2_3_17_6"]["status"] = (
                audit_file["Registry Values"][
                    "MACHINE\\SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\Policies\\System\\EnableLUA"
                ]
                == "4,1"
            )
        except:
            audit_result["rule_2_3_17_6"] = {}
            audit_result["rule_2_3_17_6"]["value"] = "N/A"
            audit_result["rule_2_3_17_6"]["status"] = False

        # 2.3.17.7
        try:
            audit_result["rule_2_3_17_7"] = {}
            audit_result["rule_2_3_17_7"]["value"] = audit_file["Registry Values"][
                "MACHINE\\SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\Policies\\System\\PromptOnSecureDesktop"
            ]
            audit_result["rule_2_3_17_7"]["status"] = (
                audit_file["Registry Values"][
                    "MACHINE\\SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\Policies\\System\\PromptOnSecureDesktop"
                ]
                == "4,1"
            )
        except:
            audit_result["rule_2_3_17_7"] = {}
            audit_result["rule_2_3_17_7"]["value"] = "N/A"
            audit_result["rule_2_3_17_7"]["status"] = False

        # 2.3.17.8
        try:
            audit_result["rule_2_3_17_8"] = {}
            audit_result["rule_2_3_17_8"]["value"] = audit_file["Registry Values"][
                "MACHINE\\SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\Policies\\System\\EnableVirtualization"
            ]
            audit_result["rule_2_3_17_8"]["status"] = (
                audit_file["Registry Values"][
                    "MACHINE\\SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\Policies\\System\\EnableVirtualization"
                ]
                == "4,1"
            )
        except:
            audit_result["rule_2_3_17_8"] = {}
            audit_result["rule_2_3_17_8"]["value"] = "N/A"
            audit_result["rule_2_3_17_8"]["status"] = False

    except Exception as e:
        return {"error": str(e)}
    return audit_result


@router.get("/audit/{server_id}")
async def get_audit_jobs(server_id: Annotated[str, Path(...)]):
    monogo_client = MongoClient(config["MONGODB_URI"])[config["DB_NAME"]]["server"]
    server = monogo_client.find_one({"_id": ObjectId(server_id)})
    if server == None:
        raise HTTPException(status_code=404, detail="server not found")
    result = audit_cis(server["path"])
    # final_result = {
    #     key: not result[key]["status"]
    #     for key in result
    #     if result[key]["status"] == False
    # }
    return result


@router.post("/auto-hardening")
async def auto_hardening(job: Job):
    if not ObjectId.is_valid(job.server_id):
        raise HTTPException(status_code=400, detail="invalid object id")
    job = job.model_dump()
    monogo_client = MongoClient(config["MONGODB_URI"])[config["DB_NAME"]]["server"]
    server = monogo_client.find_one({"_id": ObjectId(job["server_id"])})
    if server == None:
        raise HTTPException(status_code=404, detail="server not found")
    # audit
    cmd_audit = f"ansible-playbook -i {server['path']+'/hosts'} {server['path']+'/audit/tasks/main.yml'}"
    await asyncio.create_task(run_proc(cmd_audit, job["server_id"]))
    audit_result = audit_cis(server["path"])
    print(audit_result)

    job_auto_id = create_hardening_job(job)
    env = Environment(loader=FileSystemLoader("./templates/cis/hardening/vars"))
    template = env.get_template("main-auto.yml.j2")
    render_file = template.render(audit_result)
    with open(f"{server['path'] + '/hardening/vars'}/main-auto.yml", "w") as file:
        file.write(render_file)

    job_auto = {
        "job_id": job_auto_id,
        "topic_select": {
            key: not audit_result[key]["status"]
            for key in audit_result
            if audit_result[key]["status"] == False
        },
    }
    run_job_auto(job_auto)

    return {"msg": "running"}
