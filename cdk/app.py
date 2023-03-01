#!/usr/bin/env python3
import aws_cdk
from lib.stacks.autocup import AutoCupStack, NotifStack, DeleteAutoCupStack

app = aws_cdk.App()

AutoCupStack(app, "AutoCup")
NotifStack(app, "AutoCupNotifications")
DeleteAutoCupStack(app, "DeleteAutoCup")

app.synth()
