from fastapi import FastAPI
from fastapi.responses import HTMLResponse
import uvicorn, logging
from routers import project, server, hardening, document
from fastapi.middleware.cors import CORSMiddleware

# app = FastAPI(docs_url=None, redoc_url=None)
logging.basicConfig(level=logging.DEBUG)
app = FastAPI()
app.include_router(server.router)
app.include_router(hardening.router)
app.include_router(document.router)
app.include_router(project.router)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # You can replace "*" with your specific frontend's URL
    allow_credentials=True,
    allow_methods=["*"],  # You can specify the HTTP methods that are allowed
    allow_headers=["*"],  # You can specify the HTTP headers that are allowed
)

html = """
<!DOCTYPE html>
<html>
    <head>
        <title>Chat</title>
    </head>
    <body>
        <h1>WebSocket Chat</h1>
        <form action="" onsubmit="sendMessage(event)">
            <input type="text" id="messageText" autocomplete="off"/>
            <button>Send</button>
        </form>
        <ul id='messages'>
        </ul>
        <script>
            var ws = new WebSocket("ws://127.0.0.1:8000/api/ws");
            ws.onmessage = function(event) {
                var messages = document.getElementById('messages')
                var message = document.createElement('li')
                var content = document.createTextNode(event.data)
                message.appendChild(content)
                messages.appendChild(message)
            };
            function sendMessage(event) {
                var input = document.getElementById("messageText")
                ws.send(input.value)
                input.value = ''
                event.preventDefault()
            }
        </script>
    </body>
</html>
"""


@app.get("/")
async def root():
    return HTMLResponse(html)


if __name__ == "__main__":
    uvicorn.run("main:app", reload=True, log_level="info")

# @app.on_event("startup")
# def startup_db_client():
#     app.mongodb_client = MongoClient(config["MONGODB_URI"])
#     app.database = app.mongodb_client[config["DB_NAME"]]
#     print("Connected to the MongoDB database!")

# @app.on_event("shutdown")
# def shutdown_db_client():
#     app.mongodb_client.close()
