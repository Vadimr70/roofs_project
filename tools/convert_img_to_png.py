import os
import cv2

path = 'dataset_roofs/images'
names = os.listdir(path)
for name in names:
    img = cv2.imread(path+'/' + name)
    name = name.split('.')[0] + '.png'
    print(name)
    cv2.imwrite(path+'/'+ name , img)