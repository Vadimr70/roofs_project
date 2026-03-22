import os
import cv2
import time
import pyproj
from pyproj import Transformer


transformer = pyproj.Transformer.from_crs(crs_from="epsg:3857", crs_to="epsg:4326")

names = os.listdir('tiles')
names = [name for name in names if name[-4:]=='.tif']
print(names)

for name in names:
    start = time.time()
    name_short = name.split('.')[0]
    if name[:3]=='til':
        d_w = 4
        d_h = 3
    elif name[:3]=='big':
        d_w = 8
        d_h = 6

    path_to_tile = 'tiles/' + name
    path_to_twf = path_to_tile[:-4] + '.tfw'

    if not os.path.isfile(path_to_twf):
        print(f'skipped {name} because no .tfw file')
        continue

    tile = cv2.imread(path_to_tile)
    print(tile.shape)

    w = int(tile.shape[1]/d_w)
    h = int(tile.shape[0]/d_h)

    x = 0
    y = 0

    with open(path_to_twf,'r') as f:
        lines = f.readlines()
    f.close()    

    x_scale = float(lines[0][:-2])
    y_scale = float(lines[3][:-2])
    x_start = float(lines[4][:-2])
    y_start = float(lines[5][:-2])

    count = 0
    for i in range(d_w):
        x += w
        y = 0
        for j in range(d_h):
            count+=1
            y += h
            temp_tile = tile[y-h:y,x-w:x]
            assert temp_tile.shape[0] == h
            assert temp_tile.shape[1] == w
            cv2.imwrite(f'outputs/{name_short}_{count}.tif', temp_tile)

            x_temp = x_start + (x-w)*x_scale
            y_temp = y_start + (y-h)*y_scale
            lng, lat = transformer.transform(x_temp, y_temp)

            with open(f'outputs/{name_short}_{count}.txt','w') as f:
                f.write(str(x_temp)+'\n')
                f.write(str(y_temp)+'\n')
                f.write(str(lng)+'\n')
                f.write(str(lat)+'\n')
                f.close()
            temp_dur = time.time() - start

    end = time.time()        
    print(f'file {name} executed in  {end - start}')