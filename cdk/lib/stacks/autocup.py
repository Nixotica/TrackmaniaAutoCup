from aws_cdk import (
    core,
    aws_lambda as lambda_,
    aws_events as events,
    aws_events_targets as targets
)

class MyStack(core.Stack):
    def __init__(self, scope: core.Construct, id: str, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        # Create the Lambda function
        my_lambda = lambda_.Function(
            self, "MyLambda",
            runtime=lambda_.Runtime.PYTHON_3_8,
            handler="index.handler",
            code=lambda_.Code.from_asset("lambda_function")
        )

        # Create the EventBridge scheduler
        rule = events.Rule(
            self, "MyRule",
            schedule=events.Schedule.cron(
                week_day="SUN",
                hour="20",
                minute="0"
            ),
        )

        # Add the Lambda function as the target of the scheduler
        rule.add_target(targets.LambdaFunction(my_lambda))
