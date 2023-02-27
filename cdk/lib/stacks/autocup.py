import os

from aws_cdk import (
    Duration,
    Stack,
    aws_lambda as lambda_,
    aws_events as events,
    aws_events_targets as targets,
    aws_lambda_python_alpha as _alambda
)

from constructs import Construct

class AutocupStack(Stack):
    def __init__(self, scope: Construct, id: str, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        # Create the Lambda function
        my_lambda = _alambda.PythonFunction(
            self, "CreateEventLambda",
            runtime=lambda_.Runtime.PYTHON_3_8,
            entry="./lib/lambdas/create_autocup/",
            index="autocup.py",
            handler="lambda_handler",
            timeout=Duration.minutes(1),
            environment={
                "AUTHORIZATION": os.environ["AUTHORIZATION"]
            }
        )

        # Create the EventBridge scheduler
        rule = events.Rule(
            self, "TriggerEventCreation",
            schedule=events.Schedule.cron(
                week_day="SUN",
                hour="20",
                minute="0"
            ),
        )

        # Add the Lambda function as the target of the scheduler
        rule.add_target(targets.LambdaFunction(my_lambda))
