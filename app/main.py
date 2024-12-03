from fastapi import FastAPI
from mangum import Mangum
from pydantic import BaseModel
from datetime import date
from typing import Optional
import boto3
import uuid

app = FastAPI()
handler = Mangum(app)

local_development = True

class Player(BaseModel):
    name: str
    country: str
    date_of_birth: date
    team: str
    position: str
    shirt_number: int


@app.get("/")
def root():
    return {"statusCode": 200, "body": "Hello Player! Welcome To The Beautiful Game"}


@app.post("/players/")
async def add_player(player: Player):
    
    player_id = uuid.uuid5(uuid.NAMESPACE_DNS, f"{player.name}-{player.country}")

    item = {
        "id": str(player_id),
        "name": player.name,
        "country": player.country,
        "date_of_birth": player.date_of_birth.isoformat(),
        "team": player.team,
        "position": player.position,
        "shirt_number": player.shirt_number,
    }

    # Add player to Dynamo DB Table
    try:
        table = get_dynamoddb_table()
        table.put_item(Item=item)
        return {"player_id": item["id"], "player_name": item["name"]}
    except Exception as e:
        print(f"An error occurred: {e}")


@app.get("/players/{id}")
async def get_player(id: str):
    # Retrieve player data by id from table
    table = get_dynamoddb_table()
    response = table.get_item(Key={"id": id})
    item = response.get("Item")
    return item


# @app.put

# @app.delete

def get_dynamoddb_table():
    table_name = "Players"

    if local_development:
        return boto3.resource("dynamodb",
                          endpoint_url="http://localhost:7001",
                          region_name="af-south",
                          aws_access_key_id="myid",
                          aws_secret_access_key="myaccesskey").Table(table_name)
    else:
        return boto3.resource("dynamodb").Table(table_name)
