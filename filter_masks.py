import imageio
import numpy as np
import os
import cv2 
from PIL import Image
path = 'outputs/masks/'
viz_path = 'outputs/visualization/'
masks = os.listdir(path)
print(len(masks))

def filter_masks(masks_path):
    viz = 'outputs/visualization/'
    masks = os.listdir(masks_path)
    cnt = 0
    for mask in masks:
        viz_path = viz + mask.split('.')[0] + '.png'
        mask_path = masks_path + mask
        array = np.load(mask_path)
        img = array.astype(np.uint8)
        non_zero = cv2.countNonZero(img)
        if non_zero < 17000:
            os.remove(mask_path)
            os.remove(viz_path)
            cnt+=1

    print(f'removed {cnt} out of {len(masks)}')
        
filter_masks(path)