from fastapi import FastAPI
from mangum import Mangum
from pydantic import BaseModel
from datetime import date
import boto3

app = FastAPI()
handler = Mangum(app)


class Player(BaseModel):
    name: str
    country: str
    # date_of_birth: date
    team: str
    position: str
    shirt_number: int


@app.get("/")
def root():
    return {"statusCode": 200, "body": "Hello Player! Welcome To The Beautiful Game"}


def get_local_dynamodb_table():
    table_name = "Players"
    return boto3.resource("dynamodb",
                          endpoint_url="http://localhost:7001",
                          region_name="af-south",
                          aws_access_key_id="myid",
                          aws_secret_access_key="myaccesskey").Table(table_name)


def get_dynamoddb_table():
    table_name = "Players"
    return boto3.resource("dynamodb").Table(table_name)

# @app.get("/players/{}")


@app.post("/players/")
async def add_player(player: Player):
    item = {
        "PlayerId": "1",
        "name": player.name,
        "country": player.country,
        # "date_of_birth": player.date_of_birth,
        "team": player.team,
        "position": player.position,
        "shirt_number": player.shirt_number,
    }

    # Add player to Dynamo DB Table
    table = get_local_dynamodb_table()
    table.put_item(Item=item)
    return {"player": item}


# @app.put

# @app.delete
