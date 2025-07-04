from aws_cdk import (
    Stack,
    Duration,
    RemovalPolicy,
    aws_dynamodb as dynamodb,
    aws_lambda as _lambda,
    aws_lambda_python_alpha as _alambda,
    aws_cognito as cognito,
    aws_apigatewayv2 as apigatewayv2,
    aws_apigatewayv2_integrations as gateway_integrations,
    aws_apigatewayv2_authorizers as gateway_authorizers,
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

        # Create Full Access Scope
        full_access_scope = cognito.ResourceServerScope(
            scope_name="read_write",
            scope_description="Full access to Player FC API"
        )

        # Create Resource Server
        user_pool_resource_server = user_pool.add_resource_server(
            "PlayerFCResourceServer",
            identifier="playerfc-m2m-resource-server",
            scopes=[full_access_scope]
        )

        # Create User Pool Client
        user_pool_client = user_pool.add_client(
            "CognitoUserPoolClient",
            user_pool_client_name="PlayerFC-M2M-Client",
            generate_secret=True,
            supported_identity_providers=[],
            auth_flows=cognito.AuthFlow(custom=True),
            o_auth=cognito.OAuthSettings(
                flows=cognito.OAuthFlows(client_credentials=True),
                scopes=[
                    cognito.OAuthScope.resource_server(
                        user_pool_resource_server, full_access_scope),
                ]
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
        http_api = apigatewayv2.HttpApi(
            self, "PlayerFCHttpApi",
            create_default_stage=True,
            description="PlayerFC API Gateway")

        # Create JWT Authorizer
        jwt_authorizer = gateway_authorizers.HttpJwtAuthorizer("JWTAuthorizer",
                                                               identity_source=[
                                                                   "$request.header.Authorization"],
                                                               jwt_audience=[
                                                                   user_pool_client.user_pool_client_id],
                                                               jwt_issuer=user_pool.user_pool_provider_url)

        # Add route to add, retrieve player(s)
        http_api.add_routes(
            path="/players",
            methods=[apigatewayv2.HttpMethod.GET, apigatewayv2.HttpMethod.POST],
            integration=gateway_integrations.HttpLambdaIntegration(
                "LambdaIntegration",
                api
            ),
            authorizer=jwt_authorizer
        )

        # Add route to retrieve a single player
        http_api.add_routes(
            path="/players/{player_id}",
            methods=[apigatewayv2.HttpMethod.GET],
            integration=gateway_integrations.HttpLambdaIntegration(
                "LambdaIntegration",
                api
            )
        )
   
