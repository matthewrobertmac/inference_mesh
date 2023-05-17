import argparse
import collections

import numpy as np
from PIL import Image
from PIL import ImageDraw

from pycoral.adapters import common
from pycoral.adapters import detect
from pycoral.utils.dataset import read_label_file
from pycoral.utils.edgetpu import make_interpreter

Object = collections.namedtuple('Object', ['id', 'label', 'score', 'bbox'])

object_labels_list = []

def tiles_location_gen(img_size, tile_size, overlap):
  tile_width, tile_height = tile_size
  img_width, img_height = img_size
  h_stride = tile_height - overlap
  w_stride = tile_width - overlap
  for h in range(0, img_height, h_stride):
    for w in range(0, img_width, w_stride):
      yield [w, h, min(img_width, w + tile_width), min(img_height, h + tile_height)]

def non_max_suppression(objects, threshold):
  boxes = np.array([o.bbox for o in objects])
  xmins = boxes[:, 0]
  ymins = boxes[:, 1]
  xmaxs = boxes[:, 2]
  ymaxs = boxes[:, 3]
  areas = (xmaxs - xmins) * (ymaxs - ymins)
  scores = [o.score for o in objects]
  idxs = np.argsort(scores)

  selected_idxs = []
  while len(idxs):
    selected_idx = idxs[-1]
    selected_idxs.append(selected_idx)
    overlapped_xmins = np.maximum(xmins[selected_idx], xmins[idxs[:-1]])
    overlapped_ymins = np.maximum(ymins[selected_idx], ymins[idxs[:-1]])
    overlapped_xmaxs = np.minimum(xmaxs[selected_idx], xmaxs[idxs[:-1]])
    overlapped_ymaxs = np.minimum(ymaxs[selected_idx], ymaxs[idxs[:-1]])
    w = np.maximum(0, overlapped_xmaxs - overlapped_xmins)
    h = np.maximum(0, overlapped_ymaxs - overlapped_ymins)
    intersections = w * h
    unions = areas[idxs[:-1]] + areas[selected_idx] - intersections
    ious = intersections / unions
    idxs = np.delete(idxs, np.concatenate(([len(idxs) - 1], np.where(ious > threshold)[0])))
  return selected_idxs

def draw_object(draw, obj, labels):
  draw.rectangle(obj.bbox, outline='red')
  draw.text((obj.bbox[0], obj.bbox[3]), '%s\n%.2f' % (labels.get(obj.id, obj.id), obj.score), fill='red')

def reposition_bounding_box(bbox, tile_location):
  bbox[0] += tile_location[0]
  bbox[1] += tile_location[1]
  bbox[2] += tile_location[0]
  bbox[3] += tile_location[1]
  return bbox

def main():
  parser = argparse.ArgumentParser()
  parser.add_argument('--model', required=True)
  parser.add_argument('--label')
  parser.add_argument('--score_threshold', type=float, default=0.1)
  parser.add_argument('--tile_sizes', required=True)
  parser.add_argument('--tile_overlap', type=int, default=15)
  parser.add_argument('--iou_threshold', type=float, default=.1)
  parser.add_argument('--input', required=True)
  parser.add_argument('--output')
  args = parser.parse_args()

  interpreter = make_interpreter(args.model)
  interpreter.allocate_tensors()

  labels = read_label_file(args.label) if args.label else {}
  
  img = Image.open(args.input).convert('RGB')
  draw = ImageDraw.Draw(img)

  img_size = img.size
  tile_sizes = [list(map(int, size.split('x'))) for size in args.tile_sizes.split(',')]
  
  objects = []
  for tile_size in tile_sizes:
    for tile_location in tiles_location_gen(img_size, tile_size, args.tile_overlap):
      tile = img.crop(tile_location)
      _, scale = common.set_resized_input(interpreter, tile.size,
                                          lambda size, img=tile: img.resize(size, Image.NEAREST))
      interpreter.invoke()
      objs = detect.get_objects(interpreter, args.score_threshold, scale)
      for obj in objs:
        bbox = [obj.bbox.xmin, obj.bbox.ymin, obj.bbox.xmax, obj.bbox.ymax]
        bbox = reposition_bounding_box(bbox, tile_location)
        objects.append(Object(obj.id, labels.get(obj.id, obj.id), obj.score, bbox))

  idxs = non_max_suppression(objects, args.iou_threshold)


  for idx in idxs:
    draw_object(draw, objects[idx], labels)
    print(f"Label: {objects[idx].label}, Probability: {objects[idx].score}")
    object_labels = f"Label: {objects[idx].label}, Probability: {objects[idx].score}"
    object_labels_list.append(object_labels)


  img.show()

  if args.output:
    img.save(args.output)
 #   print(f"Saved result at {args.output}")
   # print(object_labels_list)


  return object_labels_list

if __name__ == '__main__':
  print(main())
