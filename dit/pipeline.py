TEMP_OUTPUT_NAME="temp.jpg"
IMAGES_DIR='out_images'

# for the DiT part
import cv2

from object_detection.ditod import add_vit_config

import torch
from time import time

from detectron2.config import get_cfg
from detectron2.utils.visualizer import ColorMode, Visualizer
from detectron2.data import MetadataCatalog
from detectron2.engine import DefaultPredictor


# for the tesseract part
import matplotlib.pyplot as plt
from subprocess import check_output, run
import pandas as pd
import subprocess
from os import path, makedirs
from sys import argv


if len(argv) < 3:
    print("Usage: python pipeline.py <input_image> <output_file>")
    exit(1)

INPUT_IMAGE = argv[1]
OUTPUT_FILE = argv[2]

print("done with imports")

# Step 1: instantiate config
cfg = get_cfg()
add_vit_config(cfg)
cfg.merge_from_file("./object_detection/publaynet_configs/maskrcnn/maskrcnn_dit_base.yaml")

# Step 2: add model weights URL to config
cfg.merge_from_list(["MODEL.WEIGHTS","./model_final.pth"])

# Step 3: set device
device = "cuda" if torch.cuda.is_available() else "cpu"
cfg.MODEL.DEVICE = device

# Step 4: define model
predictor = DefaultPredictor(cfg)

# Step 5: run inference
img = cv2.imread(INPUT_IMAGE)

md = MetadataCatalog.get(cfg.DATASETS.TEST[0])
md.set(thing_classes=["text","h1","code","ul","figure", "ol", "h2", "h3", "h4", "h5", "h6"])

print("running inference")

t = time()
output = predictor(img)["instances"]
print(time()-t)

# filter data by confidence
output = output[output.scores > 0.5]

def merge_overlapping_bbs():
    # find overlapping bounding boxes
    overlaps = []
    for i in range(output.pred_boxes.tensor.shape[0]):
        for j in range(i+1, output.pred_boxes.tensor.shape[0]):
            bb1 = output.pred_boxes.tensor[i]
            bb2 = output.pred_boxes.tensor[j]

            if bb1[0] < bb2[2] and bb1[2] > bb2[0] and bb1[1] < bb2[3] and bb1[3] > bb2[1]:
                overlaps.append((i,j))

    # merge them
    for i,j in overlaps:
        bb1 = output.pred_boxes.tensor[i]
        bb2 = output.pred_boxes.tensor[j]
        
        # index where we will save the merged bbox
        index = i if output.scores[i] > output.scores[j] else j
        # index of the other bbox, to be deleted
        todelete = i if output.scores[i] <= output.scores[j] else j          


        # merge bboxes
        output.pred_boxes.tensor[index] = torch.tensor(
            [min(bb1[0],bb2[0]), min(bb1[1],bb2[1]), max(bb1[2],bb2[2]), max(bb1[3],bb2[3])]
        )

        # delete other element from all tensors
        output.pred_boxes.tensor = torch.cat((output.pred_boxes.tensor[:todelete], output.pred_boxes.tensor[todelete+1:]))
        output.pred_classes = torch.cat((output.pred_classes[:todelete], output.pred_classes[todelete+1:]))
        output.scores = torch.cat((output.scores[:todelete], output.scores[todelete+1:]))

# deduplicate bounding boxes
merge_overlapping_bbs()

# sort all tensors by y coordinate
index_order = output.pred_boxes.tensor[:,1].argsort()
output.pred_boxes.tensor = output.pred_boxes.tensor[index_order]
output.pred_classes = output.pred_classes[index_order]
output.scores = output.scores[index_order]

txt = ""

# for each, save them and run tesseract on them
for i in range(output.pred_classes.shape[0]):
    bbs = output.pred_boxes[i].tensor[0].int()
    cropped = img[bbs[1]:bbs[3],bbs[0]:bbs[2]]
    
    out = ""

    # run tesseract if it isn't a figure
    if output.pred_classes[i] != 4:
        cv2.imwrite(TEMP_OUTPUT_NAME, cropped)
        if output.pred_classes[i] == 0:
            run(['python', '../../dataset-retriever/font-style-classifier/gen_section_md.py', TEMP_OUTPUT_NAME, 'temp.md'])
            out = open('temp.md', 'r').read()
        else:
            out = check_output(['tesseract', TEMP_OUTPUT_NAME, "-", "-l", "eng"], stderr=subprocess.DEVNULL).decode('utf-8')
        
    
    if output.pred_classes[i] == 0:
        txt += out + '\n\n'
    elif output.pred_classes[i] == 1:
        txt += '# '+ out + '\n\n'
    elif output.pred_classes[i] == 2:
        txt += '```'
        txt += out
        txt += '```\n\n'
    elif output.pred_classes[i] == 3:
        for el in out.splitlines():
            if el.isspace() or el == '':
                continue
            txt+='* ' + el+'\n'
        txt+='\n'
    elif output.pred_classes[i] == 4:
        if not path.exists(IMAGES_DIR):
            makedirs(IMAGES_DIR)
        img_path = path.join(IMAGES_DIR, i)
        cv2.imwrite(img_path, cropped)
        txt+=f'![]({img_path})\n\n'
    elif output.pred_classes[i] == 5:
        for el in out.splitlines():
            if el.isspace() or el == '':
                continue
            txt+='1. ' + el+'\n'
        txt+='\n'
    else: # output.pred_classes[i] >= 6
        txt += '#'*(output.pred_classes[i]-4)+ ' '+ out+'\n\n'


with open(OUTPUT_FILE, 'a') as f:
    f.write(txt)




