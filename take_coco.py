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
    model = "ssd_mobilenet_v2_coco_quant_no_nms_edgetpu.tflite.tflite"  # replace with your model path
    labels = "coco_labels_smaller.txt"  # replace with your labels path

    def __init__(self, photo_id, bucket_name, client_name=GOOGLE_CLOUD_PROJECT):
        self.photo_id = photo_id
        self.photo_path = f'photo_{photo_id}.jpg'
        self.bucket_name = bucket_name
        self.storage_client = storage.Client(client_name)
        self.bucket = self.storage_client.bucket(bucket_name)
        self.blob = None
        self.processed_photo_path = None
        self.added_labels = []

        # Ensure the photos directory exists
        makedirs(self.PHOTOS_DIR, exist_ok=True)

class Photo:
    GCS_BUCKET = "raspberrypi4"
    GOOGLE_CLOUD_PROJECT = "pullupnyc"  # replace with your actual project id
    PHOTOS_DIR = "photos"
    PREFIX = "processed_"
    model = "ssd_mobilenet_v2_coco_quant_no_nms_edgetpu.tflite"  # replace with your model path
    labels = "coco_labels.txt"  # replace with your labels path

    def __init__(self, photo_id, bucket_name, client_name=GOOGLE_CLOUD_PROJECT):
        self.photo_id = photo_id
        self.photo_path = f'photo_{photo_id}.jpg'
        self.bucket_name = bucket_name
        self.storage_client = storage.Client(client_name)
        self.bucket = self.storage_client.bucket(bucket_name)
        self.blob = None
        self.processed_photo_path = None
        self.added_labels = []

        # Ensure the photos directory exists
        makedirs(self.PHOTOS_DIR, exist_ok=True)

    def take(self):
        # Capture a photo using fswebcam
        subprocess.run(['fswebcam', '-r', '1280x720', '--no-banner', self.photo_path])
        
    def process_image_with_google_coral_edge_tpu(self):
       # Define the command as a list of strings
       cmd = [
           "python3",
           "small_object_detection.py",
           "--model", self.model,
           "--label", self.labels,
           "--input", join(self.photo_path),
           "--tile_size", "1352x900,700x700, 500x500, 250x250",
           "--tile_overlap", "50",
           "--score_threshold", "0.25",
           "--output", join(f"{self.PREFIX}{self.photo_path}")
       ]

       # Run the command
       subprocess.run(cmd, check=True)

       # Update the path of the processed image
       self.processed_photo_path = join(f"{self.PREFIX}{self.photo_path}")
   # Call the function from small_object_detection.py and get the object labels list

   # Add the object labels list to added_labels
      # self.added_labels.extend(object_labels_list)
     #  print(self.added_labels)

       # Save the processed image back to the bucket with a prefix
       new_blob = self.bucket.blob(join(self.PREFIX + self.blob.name))

       new_blob.upload_from_filename(self.processed_photo_path)
      # new_blob.metadata = {'added_labels': ','.join(self.added_labels)}
     # new_blob.patch()

       #TODO: Add the processed image url as an attribute to the instance of the Photo class


    def upload(self, destination_blob_prefix='photo'):
        # Upload the photo to the bucket
        self.blob = self.bucket.blob(f'{destination_blob_prefix}{self.photo_id}.jpg')
        self.blob.upload_from_filename(self.photo_path)

    #    self.blob.metadata = {'added_labels': (self.added_labels)}
     #   self.blob.patch()

        # Make the uploaded photo publicly accessible
        self.blob.make_public()

        # Process the image with Google Coral Edge TPU after upload
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
    
def terminal_interface(inputV = '0'):
    
    if inputV == '0':
        print("Welcome to this poorly scripted terminal interface, by yours truly Bobster 🗿")
        time.sleep(2)
        print("What would you like to do for today from the list?")
        time.sleep(1)
        terminal_interface('1')
    elif inputV == '1':
        print("1: I would like to take a photo in 4k")
        print("2: I would like to take a video in 8k")
        print("3: Let's do some people watching today")
        print("4: Would you like to learn more about Tensorflow Lite")
        print("5: Would you like to learn about Mobile Net ?(The Model)")
        inp = input("Enter a number please\n")
        if inp == '1':
            take_a_photo()
           
        elif inp == '2':
            print("Taking Video")
            time.sleep(2)
            terminal_interface('6')

        elif inp == '3':
            print("Lets watch people :)")
            time.sleep(2)
            terminal_interface('6')
         
        elif inp == '4':
            print("TensorFlow Lite is a lightweight machine learning framework developed by Google that allows efficient deployment of machine learning models on resource-constrained devices such as smartphones, IoT devices, and microcontrollers. It provides a way to optimize and compress models to reduce their size while maintaining high performance, making them suitable for on-device inference. TensorFlow Lite supports a wide range of hardware accelerators, enabling efficient execution of models, and offers APIs for various programming languages, facilitating integration into different application ecosystems. With TensorFlow Lite, developers can bring the power of machine learning to edge devices, enabling them to perform tasks such as image recognition, voice recognition, and natural language processing directly on the device, without relying on a cloud server.")
            time.sleep(2)
            terminal_interface('6')
        elif inp == '5':
           
            print("MobileNetV2 is a highly efficient and lightweight convolutional neural network architecture designed for mobile and embedded devices. It builds upon the success of its predecessor, MobileNetV1, by introducing improvements that enhance accuracy while maintaining low computational complexity. MobileNetV2 incorporates a combination of depthwise separable convolutions, bottleneck structures, and linear bottlenecks, which reduce the number of parameters and operations required for inference. It also employs a novel inverted residual block that enhances information flow and allows for better feature representation. MobileNetV2 achieves an optimal balance between model size and accuracy, making it well-suited for applications such as real-time object detection, image classification, and semantic segmentation on resource-constrained devices.")             
            time.sleep(2)
            terminal_interface('6')
        else: 
            print("Please select from the options below.")
            time.sleep(1.5)
            terminal_interface('1')
    elif inputV == '6':
        print("Would you like to do anything else ? y / n ")
        inp2 = input()
        if inp2 == 'y':
            time.sleep(1.25)
            terminal_interface('1')
        elif inp2 == 'n':
            print("Committing force closure :(")
            return print("Successfully went to sleep")
        else: 
            print("A simple yes or no question is it not ? 🤨")
            terminal_interface('6')
    

def take_a_photo():
        # Configuration

    bucket_name = 'raspberrypi4'
    photo_counter = Photo.list_bucket_images(bucket_name)
     # Prompt the user to take a photo
    while True:
        if input("Press Enter to take a photo (or 'q' to quit): ").lower() == 'q':
           return terminal_interface('6')
       

    #     # Create a new photo instance
        photo = Photo(photo_counter, bucket_name)

    #     # Capture the photo
        photo.take()

    #     # Upload the photo to Google Cloud Storage
        photo_url = photo.upload()

    #     print(f"Photo uploaded to: {photo_url}")

    #   #  photo.added_labels.extend(object_labels_list)
    #    # print(photo.added_labels)
            
    #     # Increment the photo counter
        photo_counter += 1

        # Check if the user wants to quit

        if input("Continue taking photos? (y/n): ").lower() != 'y':
            terminal_interface('6')
            break
        
            

def main():
    
        terminal_interface()
        
       

if __name__ == '__main__':
    main()
        

"""
import subprocess
from os import makedirs
from os.path import join
from google.cloud import storage
# from small_object_detection import object_labels_list

class Photo:
    GCS_BUCKET = "raspberrypi4"
    GOOGLE_CLOUD_PROJECT = "pullupnyc"  # replace with your actual project id
    PHOTOS_DIR = "photos"
    PREFIX = "processed_"
    model = "ssd_mobilenet_v2_coco_quant_no_nms_edgetpu.tflite"  # replace with your model path
    labels = "coco_labels.txt"  # replace with your labels path

    def __init__(self, photo_id, bucket_name, client_name=GOOGLE_CLOUD_PROJECT):
        self.photo_id = photo_id
        self.photo_path = f'photo_{photo_id}.jpg'
        self.bucket_name = bucket_name
        self.storage_client = storage.Client(client_name)
        self.bucket = self.storage_client.bucket(bucket_name)
        self.blob = None
        self.processed_photo_path = None
        self.added_labels = []

        # Ensure the photos directory exists
        makedirs(self.PHOTOS_DIR, exist_ok=True)

    def take(self):
        # Capture a photo using fswebcam
        subprocess.Popen(['fswebcam', '-r', '1280x720', '--no-banner', self.photo_path])

    def process_image_with_google_coral_edge_tpu(self):
        # Define the command as a list of strings
        cmd = [
            "python3",
            "small_object_detection.py",
            "--model", self.model,
            "--label", self.labels,
            "--input", self.photo_path,
            "--tile_size", "1352x900,500x500,250x250",
            "--tile_overlap", "50",
            "--score_threshold", "0.25",
            "--output", f"{self.PREFIX}{self.photo_path}"
        ]

        # Run the command
        result = subprocess.run(cmd, capture_output=True, text=True)
        object_labels_list = result.stdout.strip().split('\n')[-1].split(',')

        # Update the path of the processed image
        self.processed_photo_path = f"{self.PREFIX}{self.photo_path}"

        return object_labels_list

    def upload(self, destination_blob_prefix='photo'):
        # Process image with Google Coral Edge TPU
        object_labels_list = self.process_image_with_google_coral_edge_tpu()

        # Upload the photo to the bucket
        self.blob = self.bucket.blob(f'{destination_blob_prefix}{self.photo_id}.jpg')
        self.blob.upload_from_filename(self.processed_photo_path)

        # Add metadata
        self.blob.metadata = {'added_labels': ','.join(object_labels_list)}
        self.blob.patch()

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

   #     photo.added_labels.extend(main_function())
    #    print(photo.added_labels)
            
        # Increment the photo counter
        photo_counter += 1

        # Check if the user wants to quit
        if input("Continue taking photos? (y/n): ").lower() != 'y':
            break

if __name__ == '__main__':
    main()
"""