import numpy as np
import os
import cv2
import numpy as np
import pandas as pd
import requests
from xml.dom import minidom
from xml.dom.minidom import parseString
import math
from tqdm import tqdm


# request = get_adress(lat, lng, api_key)
                # xmldoc = parseString(request)
                # adresses = xmldoc.getElementsByTagName("text")
                # address = adresses[0].firstChild.nodeValue
                # print(address)
                # organizations_list = []

                # if not has_numbers(address):
                #     obj_x_coord = float(coord[0]) + cX*scale*2
                #     obj_y_coord = float(coord[1]) - cY*scale*2
                #     lng, lat = transformer.transform(obj_x_coord, obj_y_coord)
                #     request = get_adress(lat, lng, api_key)
                #     xmldoc = parseString(request)
                #     adresses = xmldoc.getElementsByTagName("text")
                #     address = adresses[0].firstChild.nodeValue

                # if has_numbers(address):
                #     organizations = get_organizations(address, api_key_org)
                #     if 'features' in organizations.keys():
                #         org_list = organizations['features']
                #     else:
                #         continue    

                #     for org in org_list:
                #         temp_dict = {}
                #         url, contacts = None, None
                #         name = org['properties']['name']
                #         name_of_categ = org['properties']['CompanyMetaData']['Categories'][0]['name']
                #         if 'url' in org['properties']['CompanyMetaData'].keys():
                #             url = org['properties']['CompanyMetaData']['url']
                #         if 'Phones' in org['properties']['CompanyMetaData'].keys():
                #             contacts = org['properties']['CompanyMetaData']['Phones'][0]['formatted']

                #         temp_dict['name'] = name
                #         temp_dict['type'] = name_of_categ
                #         if contacts is not None:
                #             temp_dict['phone'] = contacts
                #         if url is not None:    
                #             temp_dict['url'] = url

                #         print(f'name is {name}, type is {name_of_categ}')



def num2deg(xtile, ytile, zoom = 16):
  n = 2.0 ** zoom
  lon_deg = xtile / n * 360.0 - 180.0
  lat_rad = math.atan(math.sinh(math.pi * (1 - 2 * ytile / n)))
  lat_deg = math.degrees(lat_rad)
  return (lat_deg, lon_deg)


def check_same_coord_in_db(lat, lng, lat_list, lng_list):
    th = 0.015/40000*365
    for i in range(len(lat_list)):
        dist_temp = np.sqrt( (lat-lat_list[i])**2 + (lng-lng_list[i])**2 )
        if dist_temp < th:
            return True
    return False        


def has_numbers(inputString):
    return any(char.isdigit() for char in inputString)


def get_org_by_coord(lng,lat,address, api_key_org):
    r = requests.get(f'https://search-maps.yandex.ru/v1/?text={address[:-2]}&ll={lng},{lat}&spn=0.00065,0.00110&rspn=1&lang=ru_RU&apikey={api_key_org}')
    return r.text

def get_organizations(address, api_key_org):
    r = requests.get(f'https://search-maps.yandex.ru/v1/?text={address}&results=5&type=biz&lang=ru_RU&apikey={api_key_org}')
    return r.json()

def get_adress(lng, lat, api_key,d_lng = 0.000085,d_lat = 0.000110):
    r = requests.get(f'https://geocode-maps.yandex.ru/1.x/?apikey={api_key}&geocode={lng},{lat}&spn={d_lng},{d_lat}')
    return r.text
    

def dumb_coord_of_centers(df, masks_path, imgs_path, output_path, scale, area_min):
    
    masks = os.listdir(masks_path)
    print(f'found {len(masks)} masks.') 
    obj_id = 0
    scale_lat = scale * 0.000009
    scale_lng = scale * 0.000016
    for i in tqdm(range(len(masks))):
        mask = masks[i]
        # crop_names = df['crop_name'].tolist()
        # if mask_name in crop_names:
        #     print(f'{mask_name} is already in d_b')
        #     continue

        mask_name = mask.split('.')[0]
        stems = mask.split('_')
        xtile = int(stems[-2])
        ytile = int(stems[-1].split('.')[0])
        lat_deg, lon_deg = num2deg(xtile, ytile)


        mask_path = masks_path +'/'+ mask
        original = cv2.imread(imgs_path + mask_name + '.png')
        
        img_array = np.load(mask_path)*255
        img_array_converted = img_array.astype(np.uint8)

    
        contours, _ = cv2.findContours(img_array_converted, 
        cv2.RETR_TREE, cv2.CHAIN_APPROX_NONE)
        boxes = []
        contours_filtered = []
        for contour in contours:
            area = cv2.contourArea(contour)
            real_area = round(area * scale**2 ,1)

            if real_area > area_min:

                rect = cv2.minAreaRect(contour) 
                (width, height) = rect[1]
                rect_area = width*height
                box = cv2.boxPoints(rect)
                box = np.int0(box)
                boxes.append(box)
            

                if real_area > area_min*2:

                    if not np.all(np.all(box>0, axis = 1)) or np.any(np.any(box==1427, axis = 1)) :
                        real_area = real_area * 2

                
                M = cv2.moments(contour)
                contours_filtered.append(contour)
                cX = int(M["m10"] / M["m00"])
                cY = int(M["m01"] / M["m00"])
                
                obj_id+= 1
                lat = lat_deg - cY*scale_lat
                lng = lon_deg + cX*scale_lng
                original = cv2.circle(original, (cX, cY), 10, (255, 255, 255), -1)
                original = cv2.putText(original, f" obj {obj_id}, area is {real_area} sq. meters", (cX - 20, cY - 20),
                cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
                
                df = df.append({'crop_name': mask_name,'object_id':obj_id, 'lng': lng,'lat': lat, 'real_area':real_area}, ignore_index=True)
                if obj_id % 10 == 0:
                    df.to_csv(output_path + 'dumb_df_exp_filtered.csv', index=False)
    return df



if __name__ == "__main__":

    os.makedirs('./outputs', exist_ok=True)
    masks_path = 'outputs/masks/'
    imgs_path = 'outputs/visualization/'
    output_path = './outputs/'
    area_min = 1000
    scale = 0.245
    # df = pd.read_csv(output_path + 'dumb_df_exp_filtered.csv')
    df = pd.DataFrame(columns=['crop_name','object_id', 'lng','lat'])
    

    df = dumb_coord_of_centers(df, masks_path, imgs_path, output_path, scale, area_min)
    df.to_csv('./outputs/dumb_df.csv', index=False)
    print(df.head)