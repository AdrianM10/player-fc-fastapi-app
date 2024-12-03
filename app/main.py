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
    club_number: int
    national_team_number: int


class UpdatePlayer(BaseModel):
    team: Optional[str] = None
    position: Optional[str] = None
    club_number: Optional[int] = None
    national_team_number: Optional[int] = None


@app.get("/")
def root():
    return {"statusCode": 200, "body": "Hello Player! Welcome To The Beautiful Game"}


@app.post("/players")
async def create_player(player: Player):

    player_id = uuid.uuid5(
        uuid.NAMESPACE_DNS,
        f"{player.name}-{player.country}"
    )

    item = {
        "id": str(player_id),
        "name": player.name,
        "country": player.country,
        "date_of_birth": player.date_of_birth.isoformat(),
        "team": player.team,
        "position": player.position,
        "club_number": player.club_number,
        "national_team_number": player.national_team_number
    }

    # Add player to DynamoDB Table
    try:
        table = get_dynamoddb_table()
        table.put_item(Item=item)
        return {"player_id": item["id"], "player_name": item["name"]}
    except Exception as e:
        print(f"An error occurred: {e}")


@app.get("/players/{id}")
async def get_player(id: str):
    # Retrieve player data by id from DynamoDB Table
    table = get_dynamoddb_table()
    response = table.get_item(Key={"id": id})
    item = response.get("Item")
    return item


@app.get("/players/")
async def get_all_players():
    # Retrieve all players from DynamoDB Table
    table = get_dynamoddb_table()
    response = table.scan()
    items = response["Items"]
    return {"players": items}


@app.patch("/players/{id}")
async def update_player(id: str, player: UpdatePlayer):
    # Update player details in DynamoDB Table
    table = get_dynamoddb_table()
    try:
        response = table.update_item(
            Key={"id": id},
            UpdateExpression="set #team = :team, #position = :position, #club_number = :club_number, #national_team_number = :national_team_number",
            ExpressionAttributeNames={
                "#team": "team",
                "#position": "position",
                "#club_number": "club_number",
                "#national_team_number": "national_team_number",
            },
            ExpressionAttributeValues={
                ":team": player.team,
                ":position": player.position,
                ":club_number": player.club_number,
                ":national_team_number": player.national_team_number
            },
            ReturnValues="UPDATED_NEW",

        )
        return {"attributes": response["Attributes"]}
    except Exception as e:
        print(f"An error occurred updating {id}: {e}")


@app.delete("/players/{id}")
async def delete_player(id: str):
    # Delete player from DynamoDB Table
    table = get_dynamoddb_table()
    response = table.delete_item(Key={
        "id": id
    })
    return {"deleted_id": id}


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
