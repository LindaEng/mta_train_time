"""Local dev entrypoint that combines the separate api/*.py apps onto one port.

Vercel deploys each api/*.py file as its own serverless function (see vercel.json),
so each defines its own FastAPI() app. This mounts their routers together for
`uvicorn dev_server:app --reload --port 8000` so all /api/* routes work locally.
"""
from dotenv import load_dotenv

load_dotenv()

from fastapi import FastAPI

from api.buses import app as buses_app
from api.location import app as location_app
from api.trains import app as trains_app

app = FastAPI()
app.include_router(trains_app.router)
app.include_router(buses_app.router)
app.include_router(location_app.router)
