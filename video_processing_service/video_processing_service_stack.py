from aws_cdk import (
    Stack,
    aws_s3 as s3,
    aws_lambda as _lambda,
    Duration,
    aws_sqs as sqs,
    aws_iam as iam,
    aws_lambda_event_sources as lambda_event_sources,
)
from constructs import Construct
import os

class VideoProcessingServiceStack(Stack):

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        
        existing_bucket_name = "joe-video-bucket" 
        video_bucket = s3.Bucket.from_bucket_name(self, "ExistingVideoBucket", existing_bucket_name)

        existing_queue = sqs.Queue.from_queue_arn(
            self, "ExistingQueue",
            queue_arn="arn:aws:sqs:ap-southeast-2:474668413547:VideoProcessingQueue" 
        )
        
        video_processing_lambda = _lambda.Function(
            self,
            "VideoProcessingFunction",
            runtime=_lambda.Runtime.PYTHON_3_9,
            handler="lambda_function.lambda_handler",  # Entry point in the lambda_function.py
            code=_lambda.Code.from_asset(os.path.join(os.getcwd(), "src")),  # Path to lambda code and FFmpeg
            environment={
                'VIDEO_BUCKET': video_bucket.bucket_name,  # Pass the existing bucket name to Lambda
            },
            timeout=Duration.minutes(15),  # Allow longer processing time for video processing
            memory_size=1024,  # Adjust memory size as necessary
        )

        # Grant Lambda permissions to read/write from the existing S3 bucket
        video_bucket.grant_read_write(video_processing_lambda)

         # Grant permissions to Lambda to receive messages from the existing SQS queue
        existing_queue.grant_consume_messages(video_processing_lambda)

        # Add the SQS queue as an event source for the Lambda function
        video_processing_lambda.add_event_source(lambda_event_sources.SqsEventSource(existing_queue))
