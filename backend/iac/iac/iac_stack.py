from aws_cdk import (
    Stack,
    aws_dynamodb as dynamodb,
    aws_lambda as _lambda,
    aws_lambda_python_alpha as _alambda,
    CfnOutput

)
from constructs import Construct


class IacStack(Stack):

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # Create DynamoDB Table
        table = dynamodb.TableV2(self, "Table",
                                 table_name="Players",
                                 partition_key=dynamodb.Attribute(
                                     name="PlayerId", type=dynamodb.AttributeType.STRING),
                                 billing=dynamodb.BillingMode.PAY_PER_REQUEST,

                                 )

        # Create Lambda function for API endpoint
        api = _alambda.PythonFunction(
            self,
            "API",
            entry="../app",
            runtime=_lambda.Runtime.PYTHON_3_12,
            index="main.py",
            handler="handler",

        )

        # Create Lambda Function URL
        functionUrl = api.add_function_url(
            auth_type=_lambda.FunctionUrlAuthType.NONE,
            cors=_lambda.FunctionUrlCorsOptions(
                allowed_origins=["*"],
                allowed_methods=[_lambda.HttpMethod.ALL],
                allowed_headers=["*"]
            )
        )

        # Print the Function URL
        CfnOutput(self, "FunctionUrl", value=functionUrl.url)
