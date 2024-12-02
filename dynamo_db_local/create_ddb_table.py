import boto3
from botocore.exceptions import ClientError


def main():

    # Create DynamoDB Client
    dynamodb = boto3.resource(
        "dynamodb",
        endpoint_url="http://localhost:7001",
        region_name="af-south",
        aws_access_key_id="myid",
        aws_secret_access_key="myaccesskey",
    )

    create_dynamodb_table(dynamodb)


def create_dynamodb_table(dynamodb):

    # Check if DynamoDB Table exists
    table_name = "Players"

    existing_tables = dynamodb.meta.client.list_tables()["TableNames"]

    if table_name not in existing_tables:

        try:

            # Create DynamoDB Table

            table = dynamodb.create_table(
                TableName=table_name,
                KeySchema=[{"AttributeName": "id", "KeyType": "HASH"}],
                AttributeDefinitions=[
                    {"AttributeName": "id", "AttributeType": "S"}],
                BillingMode='PAY_PER_REQUEST'
            )

            print(f"Successfully created table: {table.table_name}")

        except ClientError as e:
            print(e)

    else:
        print(f"Table '{table_name}' already exists.")


if __name__ == "__main__":
    main()
