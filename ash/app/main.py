from fastapi import FastAPI
import uvicorn, logging
from routers import project, server, hardening, document, job, audit
from fastapi.middleware.cors import CORSMiddleware

# app = FastAPI(docs_url=None, redoc_url=None)
logging.basicConfig(level=logging.DEBUG)
app = FastAPI()
app.include_router(job.router)
app.include_router(server.router)
app.include_router(hardening.router)
app.include_router(document.router)
app.include_router(project.router)
app.include_router(audit.router)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # You can replace "*" with your specific frontend's URL
    allow_credentials=True,
    allow_methods=["*"],  # You can specify the HTTP methods that are allowed
    allow_headers=["*"],  # You can specify the HTTP headers that are allowed
)

if __name__ == "__main__":
    uvicorn.run("main:app", reload=True, log_level="info", host="0.0.0.0")

# @app.on_event("startup")
# def startup_db_client():
#     app.mongodb_client = MongoClient(config["MONGODB_URI"])
#     app.database = app.mongodb_client[config["DB_NAME"]]
#     print("Connected to the MongoDB database!")

# @app.on_event("shutdown")
# def shutdown_db_client():
#     app.mongodb_client.close()
