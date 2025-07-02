from aws_cdk import (
    Stack,
    Duration,
    RemovalPolicy,
    aws_dynamodb as dynamodb,
    aws_lambda as _lambda,
    aws_lambda_python_alpha as _alambda,
    aws_cognito as cognito,
    aws_apigatewayv2 as gateway,
    aws_apigatewayv2_integrations as gateway_integrations,
    Fn,
    CfnOutput

)
from constructs import Construct


class IacStack(Stack):

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # Create Amazon Cognito User Pool
        user_pool = cognito.UserPool(self, "PlayerFCUserPool",
                                     user_pool_name="PlayerFCUserPool",
                                     removal_policy=RemovalPolicy.DESTROY,)

        # Create Amazon Cognito User Pool Domain
        user_pool_domain = user_pool.add_domain(
            "PlayerFcCognitoDomain",
            cognito_domain=cognito.CognitoDomainOptions(
                domain_prefix="playerfc",
            ),
        )

        # Create Resource Server
        user_pool_resource_server = user_pool.add_resource_server(
            "PlayerFCResourceServer",
            identifier="playerfc-m2m-resource-server",
            user_pool_resource_server_name="PlayerFCResourceServer",
            scopes=[
                cognito.ResourceServerScope(
                    scope_name="read_write",
                    scope_description="Read & Write access for Player FC M2M application"
                )
            ]
        )

        # Create User Pool Client
        user_pool_client = user_pool.add_client(
            "CognitoUserPoolClient",
            user_pool_client_name="PlayerFC-M2M-Client",
            generate_secret=True,
            supported_identity_providers=[
                cognito.UserPoolClientIdentityProvider.COGNITO],
            auth_flows=cognito.AuthFlow(
                user_password=False,
                user_srp=False,
            )
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

        # Create API Gateway
        http_api = gateway.HttpApi(
            self, "PlayerFCHttpApi", 
            create_default_stage=True, 
            description="PlayerFC API Gateway")
        

        
        