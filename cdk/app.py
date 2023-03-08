#!/usr/bin/env python3
import aws_cdk
from lib.stacks.autocup import AutoCupStack

app = aws_cdk.App()

AutoCupStack(app, "AutoCup")

app.synth()
