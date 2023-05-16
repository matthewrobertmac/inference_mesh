import os
import cv2
import numpy as np
from google.cloud import storage, vision

def count_objects(data, context):
    # Extract the bucket and file information from the event data
    bucket_name = data['bucket']
    file_name = data['name']

    # Only process photos and videos with the specified prefixes
    if not file_name.startswith(('photo', 'video')):
        return

    # Set up the Cloud Vision API client
    client = vision.ImageAnnotatorClient()

    # Get the updated file path for saving annotated file
    updated_file_path = os.path.join('/tmp', file_name)

    # Download the file from Cloud Storage to a temporary location
    storage_client = storage.Client('pullupnyc')
    bucket = storage_client.get_bucket(bucket_name)
    blob = bucket.blob(file_name)
    blob.download_to_filename(updated_file_path)

    # Perform object detection based on file type
    if file_name.startswith('photo'):
        # Read the image file
        with open(updated_file_path, 'rb') as image_file:
            content = image_file.read()

        # Create an image instance
        image = vision.Image(content=content)

        # Perform object detection
        response = client.object_localization(image=image)
        objects = response.localized_object_annotations

        # Load image for drawing
        nparr = np.frombuffer(content, np.uint8)
        img_np = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

        # Draw bounding boxes and labels on the image
        for object_ in objects:
            # Draw bounding box
            for vertex in object_.bounding_poly.normalized_vertices:
                cv2.circle(img_np, (int(vertex.x * img_np.shape[1]), int(vertex.y * img_np.shape[0])), 5, (255, 0, 0), -1)
            
            # Draw label
            cv2.putText(img_np, object_.name, (int(object_.bounding_poly.normalized_vertices[0].x * img_np.shape[1]), int(object_.bounding_poly.normalized_vertices[0].y * img_np.shape[0])), cv2.FONT_HERSHEY_SIMPLEX, 1, (255,255,255), 2, cv2.LINE_AA)

        # Save the updated image with object count annotation
        cv2.imwrite(updated_file_path, img_np)

    elif file_name.startswith('video'):
        # Perform object detection on each frame of the video
        # Implementation of video object detection depends on the specific requirements and libraries used.
        # You may need to use tools like OpenCV or a dedicated video processing library to process the frames.

        # Sample implementation:
        # Read the video file using OpenCV and process each frame
        video = cv2.VideoCapture(updated_file_path)

        # Create a writer to save the updated video with object count annotation
        frame_width = int(video.get(cv2.CAP_PROP_FRAME_WIDTH))
        frame_height = int(video.get(cv2.CAP_PROP_FRAME_HEIGHT))
        fps = video.get(cv2.CAP_PROP_FPS)
        writer = cv2.VideoWriter(updated_file_path, cv2.VideoWriter_fourcc(*'mp4v'), fps, (frame_width, frame_height))

        # Process each frame and perform object detection
        while video.isOpened():
            ret, frame = video.read()
            if not ret:
                break

            # Convert the frame to an image instance
            image = vision.Image(content=cv2.imencode('.jpg', frame)[1].tostring())

            # Perform object detection
            response = client.object_localization(image=image)
            objects = response.localized_object_annotations

            # Draw object count annotation on the frame
            # Modify this section to suit your specific requirements for drawing object count on each frame

            # Draw bounding boxes and labels on the frame
            for object_ in objects:
                # Draw bounding box
                for vertex in object_.bounding_poly.normalized_vertices:
                    cv2.circle(frame, (int(vertex.x * frame.shape[1]), int(vertex.y * frame.shape[0])), 5, (255, 0, 0), -1)
                
                # Draw label
                cv2.putText(frame, object_.name, (int(object_.bounding_poly.normalized_vertices[0].x * frame.shape[1]), int(object_.bounding_poly.normalized_vertices[0].y * frame.shape[0])), cv2.FONT_HERSHEY_SIMPLEX, 1, (255,255,255), 2, cv2.LINE_AA)

            # Write the frame with object count annotation to the video writer
            writer.write(frame)

        # Release the video capture and writer
        video.release()
        writer.release()
    else:
        return

    # Upload the updated file back to Cloud Storage
    updated_blob = bucket.blob(file_name)
    updated_blob.upload_from_filename(updated_file_path)

    # Delete the temporary file
    os.remove(updated_file_path)

    # Log the object count and updated file path
    print(f"Object count: {len(objects)}")
    print(f"Updated file path: gs://{bucket_name}/{file_name}")

    # Return the updated file path
    return f"gs://{bucket_name}/{file_name}"

