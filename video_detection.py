import argparse
import collections
import cv2
import numpy as np
from PIL import Image
from PIL import ImageDraw
from pycoral.adapters import common
from pycoral.adapters import detect
from pycoral.utils.dataset import read_label_file
from pycoral.utils.edgetpu import make_interpreter

Object = collections.namedtuple('Object', ['id', 'label', 'score', 'bbox'])

def nms(objects, iou_threshold):
    if not objects:
        return []
    objects = sorted(objects, key=lambda x: x.score, reverse=True)
    keep = []
    while objects:
        largest = objects.pop(0)
        keep.append(largest)
        objects = [obj for obj in objects if IoU(obj.bbox, largest.bbox) < iou_threshold]
    return keep

def IoU(box1, box2):
    x1, y1, x2, y2 = box1
    x1_, y1_, x2_, y2_ = box2
    xi1, yi1, xi2, yi2 = max(x1, x1_), max(y1, y1_), min(x2, x2_), min(y2, y2_)
    if xi2 <= xi1 or yi2 <= yi1:
        return 0
    inter_area = (xi2 - xi1) * (yi2 - yi1)
    box1_area = (x2 - x1) * (y2 - y1)
    box2_area = (x2_ - x1_) * (y2_ - y1_)
    union_area = box1_area + box2_area - inter_area
    return inter_area / union_area

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--model', required=True)
    parser.add_argument('--label')
    parser.add_argument('--score_threshold', type=float, default=0.1)
    parser.add_argument('--iou_threshold', type=float, default=0.2)
    args = parser.parse_args()

    interpreter = make_interpreter(args.model)
    interpreter.allocate_tensors()

    labels = read_label_file(args.label) if args.label else {}

    cap = cv2.VideoCapture(0)

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        # Convert the image from OpenCV BGR format to PIL RGB format
        img = Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))

        draw = ImageDraw.Draw(img)

        _, scale = common.set_resized_input(interpreter, img.size,
                                            lambda size: img.resize(size, Image.NEAREST))
        interpreter.invoke()
        objs = detect.get_objects(interpreter, args.score_threshold, scale)

        objects = [Object(obj.id, labels.get(obj.id, obj.id), obj.score, [obj.bbox.xmin, obj.bbox.ymin, obj.bbox.xmax, obj.bbox.ymax]) for obj in objs]
        objects = nms(objects, args.iou_threshold)

        for obj in objects:
            draw.rectangle(obj.bbox, outline='red')
            draw.text((obj.bbox[0], obj.bbox[3]), '%s\n%.2f' % (labels.get(obj.id, obj.id), obj.score), fill='red')

        # Convert PIL Image back to OpenCV format
        frame = cv2.cvtColor(np.array(img), cv2.COLOR_RGB2BGR)
        cv2.imshow("Live Object Detection", frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()

if __name__ == '__main__':
    main()
