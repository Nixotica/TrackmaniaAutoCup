#!/usr/bin/env python3
import aws_cdk
from lib.stacks.autocup import AutocupStack, NotifStack

app = aws_cdk.App()

AutocupStack(app, "AutoCup")
NotifStack(app, "AutoCupNotifications")

app.synth()
