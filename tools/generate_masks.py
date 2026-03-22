import os
import cv2
import numpy as np
from xml.dom import minidom
import cv2  


def get_list_based_lines(polylines_list):

    if len(polylines_list)==0:
        return False

    lines = []
    for i in range(len(polylines_list)):
        temp_points = str(polylines_list[i].attributes['points'].value)
        res = temp_points.split(';')
        points = []
        for x in res:
            points.append((int(float(x.split(',')[0])), int(float(x.split(',')[1]))))
        lines.append(points)
    return lines


def fill_contour(polygons,width, height,color=(255,255,255)):
    image = np.zeros((height,width,3), np.uint8)
    if polygons:
        for polygon in polygons:
            polygon = np.array(polygon)
            polygon = np.int32([polygon]) 
            cv2.fillPoly(image,polygon, color)
    return image

def draw_lines(lines,width,height,line_thickness,color=(255,255,255)):
    image = np.zeros((height,width,3), np.uint8)
    for line in lines:
        for i,point in enumerate(line[1:]):
            previous_point = line[i]
            cv2.line(image, previous_point, point,color, thickness=line_thickness)
    return image[0]/255        


def draw_lines_from_polylines(polygons, width, height, name):
    polygons_roofs = [x for x in polygons if x.getAttribute('label')=='Roof']
    flag = False
    lines_roofs = get_list_based_lines(polygons_roofs)
    if lines_roofs:
        flag = True
    img_poly = fill_contour(lines_roofs,width,height)
#         img_lines = draw_lines(lines_roofs,width,height,line_thickness)
#         cv2.imwrite('roofs/id_{}_lines.png'.format(img_id),img_lines)
    cv2.imwrite(f'dataset_roofs/annotations/{name}.png', img_poly)
    return img_poly, flag
 


# def save_weighted(img, mask, name):
#     weighted = cv2.addWeighted(img, 0.8, mask, 0.5, 0.0)
#     cv2.imwrite(f'roofs/{name}_weighted.png',weighted)
    

# width = 5000
# height = 5000
line_thickness = 20
path_to_xml = 'annotations_sec.xml'
# n = 30

xmldoc = minidom.parse(path_to_xml)
images = xmldoc.getElementsByTagName("image")
print(len(images))
count = 0
for image in images:
    img_id = image.getAttribute('id')
    name = image.getAttribute('name')
    if name=='big_12_8.tif':
        continue
    print(name)
    original = cv2.imread(f'dataset_roofs/images/{name}')
    print(original.shape)
    name = name.split('.')[0]
    print(name)
    height = int(image.getAttribute('height'))
    width = int(image.getAttribute('width'))
#     print(f'{img_id},{height}, {width}')
    polygons = image.getElementsByTagName("polygon")
#     print(polygons)
    img_poly, flag = draw_lines_from_polylines(polygons,width,height, name)
    if flag:
        count+=1
print(count)    
    # if img_poly is not None:
    #     save_weighted(original,img_poly,name)
        
