import uvicorn as uvicorn
from fastapi import FastAPI

from routes.user_route import u_router

app = FastAPI()

app.include_router(u_router)

if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8006)