from fastapi import FastAPI
from mangum import Mangum
from app.routers.players import router as players_router

import logging

logger = logging.getLogger()
logger.setLevel("INFO")


app = FastAPI()

app.include_router(players_router)

handler = Mangum(app)


@app.get("/")
def root():
    return {"message": "Welcome to the Players FC API!",
            "description": "More than just a Game",
            }
