#!/usr/bin/env python3
import os

import aws_cdk
from lib.stacks.autocup import AutocupStack

app = aws_cdk.App()

AutocupStack(app, "AutoCup")

app.synth()
