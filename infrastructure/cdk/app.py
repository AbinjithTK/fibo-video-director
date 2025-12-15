#!/usr/bin/env python3
"""AWS CDK App for FIBO Video Director Infrastructure"""
import os
import aws_cdk as cdk
from stacks.backend_stack import FiboBackendStack

app = cdk.App()

# Get environment from context or use defaults
env = cdk.Environment(
    account=os.environ.get("CDK_DEFAULT_ACCOUNT"),
    region=os.environ.get("CDK_DEFAULT_REGION", "us-east-1")
)

FiboBackendStack(
    app, 
    "FiboVideoDirectorBackend",
    env=env,
    description="FIBO Video Director Backend - FastAPI on ECS Fargate"
)

app.synth()
