import configparser

config = configparser.ConfigParser()

# with open("app/audit-file/security.cfg", "r", encoding="utf-16") as r:
#     lines = r.read()
# with open("app/audit-file/security.cfg", "w") as w:
#     w.write(lines)
config.read("app/audit-file/security.cfg")
print(config.sections())
print(" ".join([i for i in config["Privilege Rights"]]))
# print(int(config["System Access"]["minimumpasswordage"]) == 24)
