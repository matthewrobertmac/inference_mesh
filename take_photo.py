import subprocess
from os import makedirs
from os.path import join
from google.cloud import storage
import time

class Photo:
    GCS_BUCKET = "raspberrypi4"
    GOOGLE_CLOUD_PROJECT = "pullupnyc"  # replace with your actual project id
    PHOTOS_DIR = "photos"
    PREFIX = "processed_"
    model = "ssd_mobilenet_v2_coco_quant_no_nms_edgetpu.tflite"  # replace with your model path
    labels = "coco_labels.txt"  # replace with your labels path

    def __init__(self, photo_id, bucket_name, client_name=GOOGLE_CLOUD_PROJECT):
        self.photo_id = photo_id
        self.photo_path = f'photo{photo_id}.jpg'
        self.bucket_name = bucket_name
        self.storage_client = storage.Client(client_name)
        self.bucket = self.storage_client.bucket(bucket_name)
        self.blob = None
        self.processed_photo_path = None

        # Ensure the photos directory exists
        makedirs(self.PHOTOS_DIR, exist_ok=True)

    def take(self):
        # Capture a photo using fswebcam
        subprocess.run(['fswebcam', '-r', '1280x720', '--no-banner', self.photo_path])

    def upload(self, destination_blob_prefix='photo'):
        # Upload the photo to the bucket
        self.blob = self.bucket.blob(f'{destination_blob_prefix}{self.photo_id}.jpg')
        self.blob.upload_from_filename(self.photo_path)

        # Make the uploaded photo publicly accessible
        self.blob.make_public()

        # Wait for 5 seconds
        time.sleep(5)

        # Process the image with Google Coral Edge TPU after upload
        self.process_image_with_google_coral_edge_tpu()

        return self.blob.public_url

    def process_image_with_google_coral_edge_tpu(self):
       # Define the command as a list of strings
       cmd = [
           "python3",
           "small_object_detection.py",
           "--model", self.model,
           "--label", self.labels,
           "--input", join(self.PHOTOS_DIR, self.photo_path),
           "--tile_size", "1352x900,500x500,250x250",
           "--tile_overlap", "50",
           "--score_threshold", "0.25",
           "--output", join(self.PHOTOS_DIR, f"{self.PREFIX}{self.photo_path}")
       ]

       # Run the command
       subprocess.run(cmd, check=True)

       # Update the path of the processed image
       self.processed_photo_path = join(self.PHOTOS_DIR, f"{self.PREFIX}{self.photo_path}")

       # Save the processed image back to the bucket with a prefix
       new_blob = self.bucket.blob(join(self.PREFIX + self.blob.name))
       new_blob.upload_from_filename(self.processed_photo_path)

    @staticmethod
    def list_bucket_images(bucket_name):
        storage_client = storage.Client('pullupnyc')
        bucket = storage_client.bucket(bucket_name)
        blobs = bucket.list_blobs()
        image_names = [blob.name for blob in blobs if blob.content_type.startswith('image/')]
        for name in image_names:
            print(name)
        return len(image_names)
def main():
    # Configuration
    bucket_name = 'raspberrypi4'
    photo_counter = Photo.list_bucket_images(bucket_name)

    while True:
        # Prompt the user to take a photo
        input("Press Enter to take a photo (or 'q' to quit): ")

        # Create a new photo instance
        photo = Photo(photo_counter, bucket_name)

        # Capture the photo
        photo.take()

        # Upload the photo to Google Cloud Storage
        photo_url = photo.upload()

        print(f"Photo uploaded to: {photo_url}")
            
        # Increment the photo counter
        photo_counter += 1

        # Check if the user wants to quit
        if input("Continue taking photos? (y/n): ").lower() != 'y':
            break

if __name__ == '__main__':
    main()
        

"""
import subprocess
from google.cloud import storage

class Photo:
    def __init__(self, photo_id, bucket_name, client_name='pullupnyc'):
        self.photo_id = photo_id
        self.photo_path = f'photo{photo_id}.jpg'
        self.bucket_name = bucket_name
        self.storage_client = storage.Client(client_name)
        self.bucket = self.storage_client.bucket(bucket_name)
        self.blob = None

    def take(self):
        # Capture a photo using fswebcam
        subprocess.run(['fswebcam', '-r', '1280x720', '--no-banner', self.photo_path])

    def upload(self, destination_blob_prefix='photo'):
        # Upload the photo to the bucket
        self.blob = self.bucket.blob(f'{destination_blob_prefix}{self.photo_id}.jpg')
        self.blob.upload_from_filename(self.photo_path)

        # Make the uploaded photo publicly accessible
        self.blob.make_public()

        return self.blob.public_url

    @staticmethod
    def list_bucket_images(bucket_name):
        storage_client = storage.Client('pullupnyc')
        bucket = storage_client.bucket(bucket_name)
        blobs = bucket.list_blobs()
        image_names = [blob.name for blob in blobs if blob.content_type.startswith('image/')]
        for name in image_names:
            print(name)
        return len(image_names)


def main():
    # Configuration
    bucket_name = 'raspberrypi4'
    photo_counter = Photo.list_bucket_images(bucket_name)

    while True:
        # Prompt the user to take a photo
        input("Press Enter to take a photo (or 'q' to quit): ")

        # Create a new photo instance
        photo = Photo(photo_counter, bucket_name)

        # Capture the photo
        photo.take()

        # Upload the photo to Google Cloud Storage
        photo_url = photo.upload()

        print(f"Photo uploaded to: {photo_url}")
            
        # Increment the photo counter
        photo_counter += 1

        # Check if the user wants to quit
        if input("Continue taking photos? (y/n): ").lower() != 'y':
            break

if __name__ == '__main__':
    main()
"""
"""
import subprocess
from google.cloud import storage

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
"""