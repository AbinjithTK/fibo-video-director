"""FIBO Video Director Backend Stack - ECS Fargate with ALB"""
from constructs import Construct
from aws_cdk import (
    Stack,
    Duration,
    RemovalPolicy,
    CfnOutput,
    aws_ec2 as ec2,
    aws_ecs as ecs,
    aws_ecs_patterns as ecs_patterns,
    aws_ecr_assets as ecr_assets,
    aws_s3 as s3,
    aws_iam as iam,
    aws_logs as logs,
    aws_secretsmanager as secretsmanager,
)
import os


class FiboBackendStack(Stack):
    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # VPC
        vpc = ec2.Vpc(
            self, "FiboVpc",
            max_azs=2,
            nat_gateways=1,
        )

        # S3 Bucket for frame caching
        frames_bucket = s3.Bucket(
            self, "FiboFramesBucket",
            bucket_name=f"fibo-frames-cache-{self.account}-{self.region}",
            versioned=True,
            removal_policy=RemovalPolicy.RETAIN,
            lifecycle_rules=[
                s3.LifecycleRule(
                    id="ExpireOldFrames",
                    expiration=Duration.days(30),
                    prefix="fibo-frames/"
                )
            ],
            cors=[
                s3.CorsRule(
                    allowed_methods=[s3.HttpMethods.GET, s3.HttpMethods.PUT],
                    allowed_origins=["*"],
                    allowed_headers=["*"],
                    max_age=3600
                )
            ],
            block_public_access=s3.BlockPublicAccess.BLOCK_ALL,
            encryption=s3.BucketEncryption.S3_MANAGED,
        )

        # Secrets for API keys
        api_secrets = secretsmanager.Secret(
            self, "FiboApiSecrets",
            secret_name="fibo-video-director/api-keys",
            description="API keys for FIBO Video Director",
            generate_secret_string=secretsmanager.SecretStringGenerator(
                secret_string_template='{"GOOGLE_API_KEY":"","FAL_KEY":""}',
                generate_string_key="placeholder"
            )
        )

        # ECS Cluster
        cluster = ecs.Cluster(
            self, "FiboCluster",
            vpc=vpc,
            container_insights=True,
        )

        # Build Docker image from project root
        docker_image = ecr_assets.DockerImageAsset(
            self, "FiboBackendImage",
            directory="../../",  # Project root
            file="Dockerfile",
            exclude=["frontend/node_modules", ".venv", "__pycache__", ".git", "infrastructure"]
        )

        # Task execution role
        task_role = iam.Role(
            self, "FiboTaskRole",
            assumed_by=iam.ServicePrincipal("ecs-tasks.amazonaws.com"),
        )

        # Grant S3 access
        frames_bucket.grant_read_write(task_role)

        # Grant secrets access
        api_secrets.grant_read(task_role)

        # CloudWatch Logs
        log_group = logs.LogGroup(
            self, "FiboBackendLogs",
            log_group_name="/ecs/fibo-video-director",
            retention=logs.RetentionDays.TWO_WEEKS,
            removal_policy=RemovalPolicy.DESTROY,
        )

        # Fargate Service with ALB
        fargate_service = ecs_patterns.ApplicationLoadBalancedFargateService(
            self, "FiboBackendService",
            cluster=cluster,
            cpu=512,
            memory_limit_mib=1024,
            desired_count=1,
            task_image_options=ecs_patterns.ApplicationLoadBalancedTaskImageOptions(
                image=ecs.ContainerImage.from_docker_image_asset(docker_image),
                container_port=8000,
                task_role=task_role,
                log_driver=ecs.LogDrivers.aws_logs(
                    stream_prefix="fibo-backend",
                    log_group=log_group,
                ),
                environment={
                    "FIBO_S3_BUCKET": frames_bucket.bucket_name,
                    "AWS_DEFAULT_REGION": self.region,
                },
                secrets={
                    "GOOGLE_API_KEY": ecs.Secret.from_secrets_manager(api_secrets, "GOOGLE_API_KEY"),
                    "FAL_KEY": ecs.Secret.from_secrets_manager(api_secrets, "FAL_KEY"),
                }
            ),
            public_load_balancer=True,
            assign_public_ip=True,
        )

        # Health check configuration
        fargate_service.target_group.configure_health_check(
            path="/",
            healthy_http_codes="200",
            interval=Duration.seconds(30),
            timeout=Duration.seconds(10),
        )

        # Auto-scaling
        scaling = fargate_service.service.auto_scale_task_count(
            min_capacity=1,
            max_capacity=4,
        )
        scaling.scale_on_cpu_utilization(
            "CpuScaling",
            target_utilization_percent=70,
            scale_in_cooldown=Duration.seconds(60),
            scale_out_cooldown=Duration.seconds(60),
        )

        # Outputs
        CfnOutput(
            self, "BackendUrl",
            value=f"http://{fargate_service.load_balancer.load_balancer_dns_name}",
            description="Backend API URL - use this in Amplify REACT_APP_API_URL",
            export_name="FiboBackendUrl"
        )

        CfnOutput(
            self, "FramesBucketName",
            value=frames_bucket.bucket_name,
            description="S3 bucket for frame caching",
            export_name="FiboFramesBucket"
        )

        CfnOutput(
            self, "SecretsArn",
            value=api_secrets.secret_arn,
            description="Secrets Manager ARN - update with your API keys",
            export_name="FiboSecretsArn"
        )
