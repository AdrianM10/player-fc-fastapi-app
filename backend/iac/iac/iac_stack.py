from aws_cdk import (
    Stack,
    aws_dynamodb as dynamodb,
    
)
from constructs import Construct

class IacStack(Stack):

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # Create DynamoDB Table
        table = dynamodb.TableV2(self, "Table",
                                 table_name="Players",
        partition_key=dynamodb.Attribute(name="PlayerId", type=dynamodb.AttributeType.STRING)
)