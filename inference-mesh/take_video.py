import subprocess
from google.cloud import storage

def record_video(video_path, duration):
    # Record a video using ffmpeg
    subprocess.run(['ffmpeg', '-f', 'v4l2', '-i', '/dev/video0', '-t', str(duration), video_path])

def upload_to_cloud_storage(video_path, bucket_name, destination_blob_name):
    # Set up Google Cloud Storage client
    storage_client = storage.Client('pullupnyc')

    # Get the bucket
    bucket = storage_client.bucket(bucket_name)

    # Upload the video to the bucket
    blob = bucket.blob(destination_blob_name)
    blob.upload_from_filename(video_path)

    # Make the uploaded video publicly accessible
    blob.make_public()

    # Get the public URL of the uploaded video
    video_url = blob.public_url

    return video_url

def list_bucket_videos(bucket_name):
    # Set up Google Cloud Storage client
    storage_client = storage.Client('pullupnyc')

    # Get the bucket
    bucket = storage_client.bucket(bucket_name)

    # List all blobs (videos) in the bucket
    blobs = bucket.list_blobs()

    # Filter and print only the video names
    video_names = [blob.name for blob in blobs if blob.content_type.startswith('video/')]
    for name in video_names:
        print(name)

    return len(video_names)

def main():
    # Configuration
    bucket_name = 'raspberrypi4'
    destination_blob_prefix = 'video'
    video_counter = list_bucket_videos(bucket_name)

    while True:
        # Prompt the user to record a video
        input("Press Enter to record a video (or 'q' to quit): ")

        # Specify the video path
        video_path = f'video{video_counter}.mp4'

        # Record the video
        duration = 3  # Duration in seconds
        record_video(video_path, duration)

        # Upload the video to Google Cloud Storage
        destination_blob_name = f'{destination_blob_prefix}{video_counter}.mp4'
        video_url = upload_to_cloud_storage(video_path, bucket_name, destination_blob_name)

        print(f"Video uploaded to: {video_url}")

        # Increment the video counter
        video_counter += 1

        # Check if the user wants to quit
        if input("Continue recording videos? (y/n): ").lower() != 'y':
            break

if __name__ == '__main__':
    main()



