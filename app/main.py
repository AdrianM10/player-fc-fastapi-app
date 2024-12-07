from fastapi import FastAPI
from mangum import Mangum
from models.players import Player, UpdatePlayer
from routers.players import router as players_router

import logging

logger = logging.getLogger()
logger.setLevel("INFO")


app = FastAPI()

app.include_router(players_router)

handler = Mangum(app)


@app.get("/")
def root():
    return {"message": "Welcome to the Players FC API!",
            "description": "Some say 'No player is bigger than the club.' Let's be real, we care more about players than the actual team most of the time.",
            }
