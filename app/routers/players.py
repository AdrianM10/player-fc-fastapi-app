import botocore.exceptions
import boto3
import botocore
import uuid
import logging

from fastapi import FastAPI, HTTPException, status
from models.players import Player, UpdatePlayer
from fastapi import APIRouter

router = APIRouter()

def get_dynamodb_table(local_development: bool = False):
    """Retrieve DynamoDB Table connection based on environment"""

    table_name = "Players"

    if local_development:
        return boto3.resource("dynamodb",
                              endpoint_url="http://localhost:7001",
                              region_name="af-south",
                              aws_access_key_id="myid",
                              aws_secret_access_key="myaccesskey").Table(table_name)
    else:
        return boto3.resource("dynamodb").Table(table_name)

@router.post("/players")
def create_player(player: Player) -> dict:
    """Create player in DynamoDB Table"""

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
    except botocore.exceptions.ClientError as e:
        logging.exception(f"An error occurred: {e}")
        raise HTTPException(status_code=500, detail="An error occurred creating player.")

@router.get("/players")
def get_all_players():
    """Retrieve all players from DynamoDB Table"""
    table = get_dynamodb_table()

    try:
        response = table.scan()
        items = response["Items"]

        if len(items) == 0:
            return {"message": "No players found"}
        else:
            return {"count": len(items), "players": items}
    except botocore.exceptions.ClientError as e:
        logging.exception(f"An error occurred: {e}")
        raise HTTPException(status_code=500, detail="An error occurred retrieving all players.")
    
@router.get("/players/{id}")
def get_player(id: str):
    """Retrieve player data by id from DynamoDB Table"""
    table = get_dynamodb_table()
    response = table.get_item(Key={"id": id})
    item = response.get("Item")

    if not item:
        raise HTTPException(status_code=404, detail=f"Player '{id}' not found")
    return item    

@router.patch("/players/{id}")
def update_player(id: str, player: UpdatePlayer):
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

    # Dynamically build 'ExpressionAttributeNames'

    expression_attribute_names = {f"#{key}": str(
        key) for key in update_fields.keys()}

    # Dynamically build 'ExpressionAttributeValues'
    expression_attribute_values = {
        f":{key}": value for key, value in update_fields.items()}

    try:
        response = table.update_item(
            Key={"id": id},
            UpdateExpression=update_expression,
            ExpressionAttributeNames=expression_attribute_names,
            ExpressionAttributeValues=expression_attribute_values,
            ReturnValues="UPDATED_NEW",

        )
        return {"id": id, "attributes": response["Attributes"]}
    except botocore.exceptions.ClientError as e:
        logging.exception(f"An error occurred: {e}")

@router.delete("/players/{id}")
def delete_player(id: str):
    """Delete player from DynamoDB Table"""
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
        raise HTTPException(status_code=500, detail="An error occurred deleting player.")




