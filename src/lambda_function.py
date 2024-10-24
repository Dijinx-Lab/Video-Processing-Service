import os
import json
import boto3
import subprocess
import time
import requests 


s3_client = boto3.client('s3')
FFMPEG_PATH = "/opt/bin/ffmpeg"  # Path to FFmpeg binary in Lambda Layer

# Initialize the S3 client
s3_client = boto3.client('s3', region_name='ap-southeast-2')

def lambda_handler(event, context):
    bucket = os.environ.get('VIDEO_BUCKET')  

    for record in event['Records']:
        # Parse the message body from SQS
        message_body = json.loads(record['body'])
        exerciseId = message_body.get('exerciseId')
        video_path = message_body.get('videoPath')
        key = message_body.get('key')
        
        trimmedKey = key.split('/')[-1]
        download_path = f'/tmp/{trimmedKey}'
        timestamp = int(time.time())
        compressed_output_path = f'/tmp/compressed_video_{timestamp}.mp4'
        thumbnail_output_path = f'/tmp/thumbnail_{timestamp}.png'

        # Download video from S3
        s3_client.download_file(bucket, key, download_path)

        # Process the video
        lossless_compress_video(download_path, compressed_output_path)
        generate_thumbnail(download_path, thumbnail_output_path)

        # Upload results back to S3
        s3_client.upload_file(compressed_output_path, bucket, f'exercises/{exerciseId}/video.mp4')
        s3_client.upload_file(thumbnail_output_path, bucket, f'exercises/{exerciseId}/thumbnail.png')

        print(f"Files uploaded successfully to s3")

        api_url = f"https://api.trainerjoe.ai/api/v1/exercise/processed/{exerciseId}"

        try:
            response = requests.put(api_url)  # Send a PUT request
            response.raise_for_status()  # Raise an error for bad responses
            print(f"API call successful: {response.status_code}, {response.text}")
        except requests.exceptions.RequestException as e:
            print(f"Error calling API: {e}")

    return {
        'statusCode': 200,
        'body': 'Video processed successfully!'
    }

def lossless_compress_video(video_path, output_path, crf=23):
    command = [
        'ffmpeg',
        '-i', video_path,
        '-c:v', 'libx264',
        '-crf', str(crf),  
        '-preset', 'veryslow',
        '-c:a', 'copy',  
        output_path
    ]

    try:
        subprocess.run(command, check=True)
        print(f"Video compressed successfully to {output_path}")
    except subprocess.CalledProcessError as e:
        print(f"Error compressing video: {e}")

def generate_thumbnail(video_path, output_path, time='00:00:03'):
    command = [
        'ffmpeg',
        '-i', video_path,
        '-ss', time, 
        '-vframes', '1', 
        output_path
    ]

    try:
        subprocess.run(command, check=True)
        print(f"Thumbnail generated successfully to {output_path}")
    except subprocess.CalledProcessError as e:
        print(f"Error generating thumbnail: {e}")
