from fastapi import FastAPI, HTTPException, status
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
    return {"message": "Welcome to the Players FC API!",
            "description": "We all know young fans support players over the team.",
            }


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
        table = get_dynamodb_table()
        table.put_item(Item=item)
        return {"player_id": item["id"], "player_name": item["name"]}
    except Exception as e:
        print(f"An error occurred: {e}")


@app.get("/players/{id}")
async def get_player(id: str):
    """Retrieve player data by id from DynamoDB Table"""
    table = get_dynamodb_table()
    response = table.get_item(Key={"id": id})
    item = response.get("Item")

    if not item:
        raise HTTPException(status_code=404, detail=f"Player '{id}' not found")
    return item


@app.get("/players")
async def get_all_players():
    """Retrieve all players from DynamoDB Table"""
    table = get_dynamodb_table()
    response = table.scan()
    items = response["Items"]

    if len(items) == 0:
        return {"message": "No players found"}
    else:
        return {"count": len(items), "players": items}


@app.patch("/players/{id}")
async def update_player(id: str, player: UpdatePlayer):
    """Update player details in DynamoDB Table"""

    table = get_dynamodb_table()

    # Check if id exists before performing patch operation
    response = table.get_item(Key={"id": id})
    item = response.get("Item")

    if not item:
        raise HTTPException(status_code=404, detail=f"Player '{
                            id}' does not exist")

    update_fields = {
        key: value for key, value in player
        if value is not None
    }

    # Dynamically build 'UpdateExpression'
    update_expression = "set " + \
        ", ".join(f"#{key} = :{key}" for key in update_fields.keys())
    
    return {"message": update_expression}

    # try:
    #     response = table.update_item(
    #         Key={"id": id},
    #         UpdateExpression="set #team = :team, #position = :position, #club_number = :club_number, #national_team_number = :national_team_number",
    #         ExpressionAttributeNames={
    #             "#team": "team",
    #             "#position": "position",
    #             "#club_number": "club_number",
    #             "#national_team_number": "national_team_number",
    #         },
    #         ExpressionAttributeValues={
    #             ":team": player.team,
    #             ":position": player.position,
    #             ":club_number": player.club_number,
    #             ":national_team_number": player.national_team_number
    #         },
    #         ReturnValues="UPDATED_NEW",

    #     )
    #     return {"id": id, "attributes": response["Attributes"]}
    # except Exception as e:
    #     print(f"An error occurred updating {id}: {e}")


@app.delete("/players/{id}")
async def delete_player(id: str):
    # Delete player from DynamoDB Table
    table = get_dynamodb_table()

    try:

        response = table.get_item(Key={"id": id})

        if "Item" not in response:
            raise HTTPException(
                status_code=404, detail=f"Player '{id}' not found")

        table.delete_item(Key={
            "id": id
        })

        return {"message": f"'{id}' successfully deleted."}

    except HTTPException:

        raise

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


def get_dynamodb_table():
    table_name = "Players"

    if local_development:
        return boto3.resource("dynamodb",
                              endpoint_url="http://localhost:7001",
                              region_name="af-south",
                              aws_access_key_id="myid",
                              aws_secret_access_key="myaccesskey").Table(table_name)
    else:
        return boto3.resource("dynamodb").Table(table_name)
