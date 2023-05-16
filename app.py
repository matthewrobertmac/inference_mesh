from camera import Camera
from photo import Photos
import cv2
import subprocess
from google.cloud import storage


def generate_ssh():
    pass

def start_server():
    pass

def take_photo(photo_path):
    # Capture a photo using fswebcam
    subprocess.run(['fswebcam', '-r', '1280x720', '--no-banner', photo_path])

def upload_to_cloud_storage(photo_path, bucket_name, destination_blob_name):
    # Set up Google Cloud Storage client
    storage_client = storage.Client('pullupnyc')

    # Get the bucket
    bucket = storage_client.bucket(bucket_name)

    # Upload the photo to the bucket
    blob = bucket.blob(destination_blob_name)
    blob.upload_from_filename(photo_path)

    # Make the uploaded photo publicly accessible
    blob.make_public()

    # Get the public URL of the uploaded photo
    photo_url = blob.public_url

    return photo_url

def list_bucket_images(bucket_name):
    storage_client = storage.Client('pullupnyc')
    bucket = storage_client.bucket(bucket_name)
    blobs = bucket.list_blobs()
    image_names = [blob.name for blob in blobs if blob.content_type.startswith('image/')]
    for name in image_names:
        print(name)
    return len(image_names)
        
bucket_name = 'raspberrypi4'
list_bucket_images(bucket_name)

        

def main():
    # Configuration
    bucket_name = 'raspberrypi4'
    destination_blob_prefix = 'photo'
    photo_counter = list_bucket_images(bucket_name)

    while True:
        # Prompt the user to take a photo
        input("Press Enter to take a photo (or 'q' to quit): ")

        # Specify the photo path
        photo_path = f'photo{photo_counter}.jpg'

        # Capture the photo
        take_photo(photo_path)

        # Upload the photo to Google Cloud Storage
        destination_blob_name = f'{destination_blob_prefix}{photo_counter}.jpg'
        photo_url = upload_to_cloud_storage(photo_path, bucket_name, destination_blob_name)

        print(f"Photo uploaded to: {photo_url}")

        # Increment the photo counter
        photo_counter += 1

        # Check if the user wants to quit
        if input("Continue taking photos? (y/n): ").lower() != 'y':
            break

if __name__ == '__main__':
    main()



def record_video(video_path, duration):
    # Record a video using ffmpeg
    subprocess.run(['ffmpeg', '-f', 'v4l2', '-i', '/dev/video0', '-t', str(duration), video_path])

def upload_to_cloud_storage(video_path, bucket_name, destination_blob_name):
    # Set up Google Cloud Storage client
    storage_client = storage.Client()

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
    storage_client = storage.Client()

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



def clip():
    pass

"""
import cv2

def take_photo():
    # Initialize the USB camera
    camera = cv2.VideoCapture(0)

    # Check if the camera is opened successfully
    if not camera.isOpened():
        print("Failed to open the camera.")
        return

    # Capture a photo
    ret, frame = camera.read()

    # Check if the photo was captured successfully
    if not ret:
        print("Failed to capture the photo.")
        return

    # Save the photo to a file
    photo_path = 'photo.jpg'
    cv2.imwrite(photo_path, frame)

    # Release the camera resources
    camera.release()

    print("Photo captured successfully.")

if __name__ == '__main__':
    take_photo()

    """