import aws_cdk as core
import aws_cdk.assertions as assertions

from video_processing_service.video_processing_service_stack import VideoProcessingServiceStack

# example tests. To run these tests, uncomment this file along with the example
# resource in video_processing_service/video_processing_service_stack.py
def test_sqs_queue_created():
    app = core.App()
    stack = VideoProcessingServiceStack(app, "video-processing-service")
    template = assertions.Template.from_stack(stack)

#     template.has_resource_properties("AWS::SQS::Queue", {
#         "VisibilityTimeout": 300
#     })
