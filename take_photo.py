import subprocess
from google.cloud import storage

def take_photo(photo_path):
    # Capture a photo using fswebcam
    subprocess.run(['fswebcam', '-r', '1280x720', '--no-banner', photo_path])

def upload_to_cloud_storage(photo_path, bucket_name, destination_blob_name):
    # Set up Google Cloud Storage client
    storage_client = storage.Client()

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

def main():
    # Configuration
    bucket_name = 'raspberrypi4'
    destination_blob_prefix = 'photo'
    photo_counter = 1

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

