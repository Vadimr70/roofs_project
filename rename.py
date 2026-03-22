import os
from shutil import copy2
import cv2
from PIL import Image
import shutil
import click


def remove_folders(folder_path):
    names = os.listdir(folder_path)
    for name in names:
        if name == 'all':
            continue
        shutil.rmtree(folder_path + '/' + name)


def remove_png(folder_path):
    files = os.listdir(folder_path)
    pngs = [fl for fl in files if fl[-4:]=='.png']
    for png in pngs:
        os.remove(folder_path + '/' + png)


def resize(images_dir):
    names  = os.listdir(images_dir)
    img_names = [name for name in names if name[-4:]=='.png']
    for name in img_names:
        img_path = images_dir + '/' + name
        new_path = images_dir + '/' + name
        img = cv2.imread(img_path)
        w, h = img.shape[0],img.shape[1]
        new_path = images_dir + '/' + name.split('.')[0] + '.tif'
        cropSize = int(w*(0.7)), int(h*(0.7))
        img = Image.open(img_path)
        img.thumbnail(cropSize, Image.ANTIALIAS)
        img.save(new_path)
        

def rename_imgs(folder_path):

    folders_names = os.listdir(folder_path)
    for name in folders_names:
        new_path = folder_path + '/' + name
        img_names = os.listdir(new_path)
        for img_name in img_names:
            
            new_img_name = name + '_' + img_name
            os.rename(new_path + '/' + img_name, new_path + '/' + new_img_name)


def change_location(folder_path):
    folders_names = os.listdir(folder_path)
    for name in folders_names:
        if name == 'all':
            continue
        new_path = folder_path + '/' + name
        img_names = os.listdir(new_path)
        for img_name in img_names:
            copy2(new_path + '/' + img_name,  folder_path + '/all/' + img_name)


@click.command()
@click.option('--path')
@click.option('--layer')
def main(path, layer):

    dir = os.path.dirname(path)
    os.makedirs(dir + 'all_locations', exist_ok=True)

    names = os.listdir(path)
    processed_names = []
    if os.path.exists('process_log.txt'):
        with open('process_log.txt','r') as f:
            processed_names = f.readlines()
            processed_names = [n[:-1] for n in processed_names]
        not_process_names = [name for name in names if name not in processed_names]
    else:
        not_process_names = names       

    if len(not_process_names) == 0:
        print(not_process_names)
        print('All folders have been processed already!')

    for name in not_process_names:
        temp_path = os.path.join(path, name)
        temp_path = os.path.join(temp_path, layer)
        if not os.path.isdir(temp_path):
            continue
        print(f'processing {name}')
        folder_path = temp_path
        new_folder_path = os.path.join(folder_path, 'all')
        os.makedirs(new_folder_path, exist_ok=True)
        rename_imgs(folder_path) 
        change_location(folder_path)
        resize(new_folder_path)
        remove_png(new_folder_path)
        
        for file in os.listdir(new_folder_path):
            copy2(new_folder_path + '/' + file, 'all_locations/' + file)
    
        processed_names.append(name)
        with open('process_log.txt','a') as f:
            f.write(name + '\n')
            print(f'Processed {name}!')
    
if __name__ == "__main__":
    main()