from aws_cdk import (
    Stack,
    Duration,
    RemovalPolicy,
    aws_dynamodb as dynamodb,
    aws_lambda as _lambda,
    aws_lambda_python_alpha as _alambda,
    aws_cognito as cognito,
    CfnOutput

)
from constructs import Construct


class IacStack(Stack):

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # Create Amazon Cognito User Pool
        user_pool = cognito.UserPool(
            self, "PlayerFCUserPool",
            user_pool_name="Player FC User Pool",
            removal_policy=RemovalPolicy.DESTROY
        )

        # Create DynamoDB Table
        table = dynamodb.TableV2(self, "Table",
                                 table_name="Players",
                                 partition_key=dynamodb.Attribute(
                                     name="id", type=dynamodb.AttributeType.STRING),
                                 removal_policy=RemovalPolicy.DESTROY,
                                 )

        # Create Lambda function for API endpoint
        api = _alambda.PythonFunction(
            self,
            "API",
            entry="../app",
            function_name="player_fc_api",
            runtime=_lambda.Runtime.PYTHON_3_12,
            index="main.py",
            handler="handler",
            timeout=Duration.seconds(60)

        )

        # Create Lambda Function URL
        functionUrl = api.add_function_url(
            auth_type=_lambda.FunctionUrlAuthType.AWS_IAM,
            cors=_lambda.FunctionUrlCorsOptions(
                allowed_origins=["*"],
                allowed_methods=[_lambda.HttpMethod.ALL],
                allowed_headers=["*"]
            )
        )

        # Print the Function URL
        CfnOutput(self, "FunctionUrl", value=f"{functionUrl.url}docs")

        # Permissions for Function to access DynamoDB
        table.grant_read_write_data(api)
