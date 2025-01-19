import pytest
import boto3
import os
import json
from fastapi.testclient import TestClient
from moto import mock_aws
from app.main import app

client = TestClient(app)


@pytest.fixture
def player_data():
    """Sample data to provide consistent player test data"""
    return {
        "id": "4d6d8412-c021-52bc-8c47-feed545b0ced",
        "name": "Christopher Nkunku",
        "country": "France",
        "date_of_birth": "1997-11-14",
        "team": "Chelsea",
        "position": "Forward",
        "club_number": 18,
        "national_team_number": 12
    }


@pytest.fixture(scope="module")
def aws_credentials():
    """Mocked AWS Credentials for moto."""
    os.environ["AWS_ACCESS_KEY_ID"] = "testing"
    os.environ["AWS_SECRET_ACCESS_KEY"] = "testing"
    os.environ["AWS_SECURITY_TOKEN"] = "testing"
    os.environ["AWS_SESSION_TOKEN"] = "testing"
    os.environ["AWS_DEFAULT_REGION"] = "af-south-1"


@pytest.fixture
def dynamodb_table(aws_credentials):
    """Mock DynamoDB table for testing"""
    dynamodb = boto3.resource('dynamodb', region_name='af-south-1')

    with mock_aws():
        table = dynamodb.create_table(
            TableName="Players",
            KeySchema=[{"AttributeName": "id", "KeyType": "HASH"}],
            AttributeDefinitions=[
                {"AttributeName": "id", "AttributeType": "S"}],
            BillingMode='PAY_PER_REQUEST'
        )
        yield table


def test_root():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {
        "message": "Welcome to the Players FC API!",
        "description": "More than just a Game"
    }


def test_create_and_get_player(dynamodb_table, player_data):

    # print("=================================== \n")
    # print(f"Sending player data: \n\n {json.dumps(player_data, indent=2)}")

    response = client.post("/players", json=player_data)
    assert response.status_code == 200
    data = response.json()

    created_player_id = data['player_id']

    # print("=================================== \n")
    # print(f"API response: \n\n {json.dumps(data, indent=2)}")

    # Verify persistence in DynamoDB table
    dynamodb_response = dynamodb_table.get_item(
        Key={'id': player_data['id']}
    )

    # print("=================================== \n")
    # print(f"DynamoDB Item Attributes : \n\n {dynamodb_response}")

    assert dynamodb_response['Item'] == player_data
    assert dynamodb_response['Item']['id'] == created_player_id


def test_update_player(dynamodb_table, player_data):

    # Initially create player
    response = client.post(f"/players", json=player_data)
    assert response.status_code == 200
    data = response.json()
    player_id = data['player_id']

    # Update player details

    update_player_data = {
        "team": "Bayern Munich",
        "club_number": 10,
    }

    updated_response = client.patch(
        f"/players/{player_id}", json=update_player_data)
    assert updated_response.status_code == 200

    dynamodb_response = dynamodb_table.get_item(
        Key={'id': player_data['id']}
    )

    # Verify if player data has been updated

    assert dynamodb_response['Item']['team'] == update_player_data['team']
    assert dynamodb_response['Item']['club_number'] == update_player_data['club_number']


# def test_delete_player(dynamodb_table, player_data):

#     id = player_data['id']

#     dynamodb_table.put_item(Item=player_data)
#     response = dynamodb_table.get_item(
#         Key={'id': '4d6d8412-c021-52bc-8c47-feed545b0ced'})

#     dynamodb_table.delete_item(Key={'id': id})
#     assert response['ResponseMetadata']['HTTPStatusCode'] == 200
#     assert response['Item']['id'] == '4d6d8412-c021-52bc-8c47-feed545b0ced'

#     updated_response = dynamodb_table.get_item(
#         Key={'id': '4d6d8412-c021-52bc-8c47-feed545b0ced'}
#     )
#     assert 'Item' not in updated_response
