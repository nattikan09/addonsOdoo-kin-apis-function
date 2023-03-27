import os
from dotenv import load_dotenv
from fastapi import FastAPI
from routers import api_routes

load_dotenv()

app = FastAPI()

def set_router():
    app.include_router(api_routes.router)

set_router()

if __name__ == "__main__":
    app.run()


# python -m uvicorn app:app --reload
