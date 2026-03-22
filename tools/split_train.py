import os
from shutil import copy2
imgs_path = 'dataset_1024/images_crops'
annot_path = 'dataset_1024/annotations_crops'

names = os.listdir(imgs_path)
for name in names[::14]:
    source_img = imgs_path + '/' + name
    source_ann = annot_path + '/' + name
    dest_img = f'dataset_1024/val/images/{name}'
    dest_ann = f'dataset_1024/val/annotations/{name}' 
    copy2(source_img, dest_img)
    copy2(source_ann, dest_ann)
    os.remove(source_img)
    os.remove(source_ann)
    