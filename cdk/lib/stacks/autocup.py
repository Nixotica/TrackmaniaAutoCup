import os

from aws_cdk import (
    Duration,
    Stack,
    aws_lambda as lambda_,
    aws_events as events,
    aws_events_targets as targets,
    aws_s3 as s3,
    aws_lambda_python_alpha as _alambda
)

from constructs import Construct

class AutoCupStack(Stack):
    def __init__(self, scope: Construct, id: str, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        """
        00:01 --> Create Registration Event
        19:00 --> Notify Event Starting in 1 Hour
        19:59 --> Delete Registration Event and Create New
        23:59 --> Delete Finished Event
        """

    ### Infrastructure

        # Create the s3 bucket to store the relevant info for this event
        event_storage = s3.Bucket(
            self, "EventStorage",
            bucket_name="autocup-storage"
        )

    ### Registration Event

        # Lambda creating the initial event to be registered to
        create_event_register_lambda = _alambda.PythonFunction(
            self, "CreateEventRegisterLambda",
            runtime=lambda_.Runtime.PYTHON_3_8,
            entry="./lib/lambdas/autocup/",
            index="create_autocup_register.py",
            handler="lambda_handler",
            timeout=Duration.minutes(10),
            environment={
                "AUTHORIZATION": os.environ["AUTHORIZATION"],
                "OPENAI_API_KEY": os.environ["OPENAI_API_KEY"],
                "STORAGE_BUCKET_NAME": "autocup-storage"
            }
        )

        # Create the initial event to be registered to throughout the week
        trigger_create_event_register = events.Rule(
            self, "TriggerCreateEventRegister",
            schedule=events.Schedule.cron(
                hour="0",
                minute="1"
            )
        )

        trigger_create_event_register.add_target(targets.LambdaFunction(create_event_register_lambda))
        event_storage.grant_read_write(create_event_register_lambda)

    ### Notifications

        # Create the Lambda function
        notify_event_lambda = _alambda.PythonFunction(
            self, "NotifyEventLambda",
            runtime=lambda_.Runtime.PYTHON_3_8,
            entry="./lib/lambdas/autocup/",
            index="notify_autocup_start.py",
            handler="lambda_handler",
            timeout=Duration.minutes(10),
            environment={
                "DISCORD_WEBHOOK_URL": os.environ["DISCORD_WEBHOOK_URL"]
            }
        )
        
        # Create the EventBridge scheduler
        notify_event_schedule = events.Rule(
            self, "TriggerNotification60Min",
            schedule=events.Schedule.cron(
                hour="19",
                minute="0"
            )
        )

        # Add the Lambda function as the target of the scheduler
        notify_event_schedule.add_target(targets.LambdaFunction(notify_event_lambda))

    ### Actual Event

        create_actual_event_lambda = _alambda.PythonFunction(
            self, "CreateActualEventLambda",
            runtime=lambda_.Runtime.PYTHON_3_8,
            entry="./lib/lambdas/autocup/",
            index="create_actual_autocup.py",
            handler="lambda_handler",
            timeout=Duration.minutes(10),
            environment={
                "AUTHORIZATION": os.environ["AUTHORIZATION"],
                "STORAGE_BUCKET_NAME": "autocup-storage"
            }
        )

        # Create the actual event
        trigger_create_actual_event = events.Rule(
            self, "TriggerCreateActualEvent",
            schedule=events.Schedule.cron(
                hour="19",
                minute="59"
            )
        )

        trigger_create_actual_event.add_target(targets.LambdaFunction(create_actual_event_lambda))
        event_storage.grant_read_write(create_actual_event_lambda)

    ### Event Deletion

        # Lambda deleting the finished event
        delete_event_lambda = _alambda.PythonFunction(
            self, "DeleteEventLambda",
            runtime=lambda_.Runtime.PYTHON_3_8,
            entry="./lib/lambdas/autocup/",
            index="delete_finished_autocup.py",
            handler="lambda_handler",
            timeout=Duration.minutes(10),
            environment={
                "AUTHORIZATION": os.environ["AUTHORIZATION"],
                "STORAGE_BUCKET_NAME": "autocup-storage"
            }
        )

        # Delete the event
        trigger_delete_event = events.Rule(
            self, "TriggerDeleteEvent",
            schedule=events.Schedule.cron(
                hour="23",
                minute="59"
            )
        )

        trigger_delete_event.add_target(targets.LambdaFunction(delete_event_lambda))
        event_storage.grant_read_write(delete_event_lambda)
