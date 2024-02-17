import configparser

config = configparser.ConfigParser()
config.read("audit-file/security.cfg", encoding="utf-16")
print(config.sections())
# t = """MACHINE\Software\Microsoft\Windows\CurrentVersion\Policies\System\NoConnectedUser"""
# print(" ".join([i for i in config["Registry Values"]]))
r = config["Registry Values"][
    r"MACHINE\Software\Microsoft\Windows\CurrentVersion\Policies\System\NoConnectedUser"
]
print(r)

# print(int(config["System Access"]["minimumpasswordage"]) == 24)
