import subprocess
from os import makedirs, path
from google.cloud import storage
import time
import glob

class Photo:
    GCS_BUCKET = "raspberrypi4"
    GOOGLE_CLOUD_PROJECT = "pullupnyc"
    PHOTOS_DIR = "photos"
    PREFIX = "processed_"
    model = "ssd_mobilenet_v2_coco_quant_no_nms_edgetpu.tflite"
    labels = "coco_labels.txt"

    def __init__(self, photo_id, bucket_name, client_name=GOOGLE_CLOUD_PROJECT):
        self.photo_id = photo_id
        self.photo_path = f'photo_{photo_id}.jpg'
        self.bucket_name = bucket_name
        self.storage_client = storage.Client(client_name)
        self.bucket = self.storage_client.bucket(bucket_name)
        self.blob = None
        self.processed_photo_path = None
        self.added_labels = []

        makedirs(self.PHOTOS_DIR, exist_ok=True)

        if not path.exists(self.model):
            raise FileNotFoundError(f"Model file '{self.model}' not found.")
        if not path.exists(self.labels):
            raise FileNotFoundError(f"Labels file '{self.labels}' not found.")

    def take(self):
        subprocess.run(['ffmpeg', '-f', 'avfoundation', '-video_size', '1280x720', '-i', 'default', '-vframes', '1', self.photo_path])

    def process_image_with_google_coral_edge_tpu(self):
        self.processed_photo_path = self.PREFIX + path.basename(self.photo_path)

        cmd = [
            "python3",
            "object_detection.py",
            "--model", self.model,
            "--label", self.labels,
            "--input", self.photo_path,
            "--iou_threshold", "0.2",
            "--score_threshold", "0.20",
            "--output", self.processed_photo_path
        ]
        subprocess.run(cmd, check=True)

        new_blob = self.bucket.blob(self.PREFIX + self.blob.name)
        new_blob.upload_from_filename(self.processed_photo_path)

    def upload(self, destination_blob_prefix='photo'):
        self.blob = self.bucket.blob(f'{destination_blob_prefix}{self.photo_id}.jpg')
        self.blob.upload_from_filename(self.photo_path)
        self.blob.make_public()
        self.process_image_with_google_coral_edge_tpu()

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

def upload_a_photo():
    bucket_name = 'raspberrypi4'
    photo_counter = Photo.list_bucket_images(bucket_name)
    while True:
        photo_path = input("Enter the path to your photo (or 'q' to quit): ")
        if photo_path.lower() == 'q':
           return terminal_interface('6')
        if not path.exists(photo_path):
            print("File does not exist, please enter a valid file path.")
            continue
        photo = Photo(photo_counter, bucket_name)
        photo.photo_path = photo_path
        photo_url = photo.upload()
        photo_counter += 1
        if input("Continue uploading photos? (y/n): ").lower() != 'y':
            terminal_interface('6')
            break

def upload_all_photos_in_directory():
    bucket_name = 'raspberrypi4'
    photo_counter = Photo.list_bucket_images(bucket_name)
    directory_path = input("Enter the path to the directory (or 'q' to quit): ")
    if directory_path.lower() == 'q':
       return terminal_interface('6')
    if not path.exists(directory_path):
        print("Directory does not exist, please enter a valid directory path.")
        return

    file_types = ['*.jpg', '*.png', '*.jpeg']
    files_grabbed = []
    for files in file_types:
        files_grabbed.extend(glob.glob(path.join(directory_path, files)))

    for photo_path in files_grabbed:
        photo = Photo(photo_counter, bucket_name)
        photo.photo_path = photo_path
        photo_url = photo.upload()
        photo_counter += 1

    terminal_interface('6')

def take_a_photo():
    bucket_name = 'raspberrypi4'
    photo_counter = Photo.list_bucket_images(bucket_name)
    while True:
        if input("Press Enter to take a photo (or 'q' to quit): ").lower() == 'q':
           return terminal_interface('6')
        photo = Photo(photo_counter, bucket_name)
        photo.take()
        photo_url = photo.upload()
        photo_counter += 1
        if input("Continue taking photos? (y/n): ").lower() != 'y':
            terminal_interface('6')
            break

def take_photo_burst():
    bucket_name = 'raspberrypi4'
    photo_counter = Photo.list_bucket_images(bucket_name)
    while True:
        if input("Press Enter to take 10 photos (or 'q' to quit): ").lower() == 'q':
           return terminal_interface('6')
        for i in range(10):
            photo = Photo(photo_counter, bucket_name)
            photo.take()
            photo_url = photo.upload()
            photo_counter += 1
        if input("Continue taking photo bursts? (y/n): ").lower() != 'y':
            terminal_interface('6')
            break

def terminal_interface(inputV = '0'):
    if inputV == '0':
        print("What would you like to do?")
        terminal_interface('1')
    elif inputV == '1':
        print("1: Take photo")
        print("2: Take photo burst")
        print("3: Live video server")
        print("4: Upload photo")
        print("5: Upload all photos in directory")
        inp = input("Enter a number\n")
        if inp == '1':
            take_a_photo()
        elif inp == '2':
            take_photo_burst()
        elif inp == '3':
            print("Starting video server")
            subprocess.run(['python3', 'video_server.py'], check=True)
            terminal_interface('6')
        elif inp == '4':
            upload_a_photo()
        elif inp == '5':
            upload_all_photos_in_directory()
        else: 
            print("Select an option.")
            terminal_interface('1')

def main():
    terminal_interface()

if __name__ == '__main__':
    main()
