import numpy as np
import os
import cv2
import pyproj
import numpy as np
import pandas as pd
import requests
from xml.dom import minidom
from xml.dom.minidom import parseString
import imageio


masks_path = 'tomsk_masks/'
imgs_path = 'tomsk_dataset_add/'
output_path = 'outputs/masks_viz/'
output_path_new = 'output/viz_new/'
# imgs_path = 'tomsk_dataset/'
# masks_path = 'outputs/masks/'
# output_path = 'outputs/masks_viz/'
area_min = 1000
scale  = 0.1*2
scale_area = 0.112*2

# df = pd.DataFrame(columns=['crop_name','object_id', 'lng','lat','real_area','address','organizations'])
df = pd.read_csv(output_path + 'dumb_df_exp_filtered.csv')

api_key = '428f4bec-2cf2-4d88-84b3-636539b76bea'
api_key_ft = '6af69ba7-1b6c-4358-9f79-9c9cbc207f38'
api_key_sec = '002fa019-bd47-481e-abce-6025ab30a425'
api_key_org = '819baf3e-84e3-4156-894a-91235ea1191f'
api_key_org_sec = '614ec352-af37-490c-aa9e-f7109b0a9b79'
api_key_org_ft = '5e2b05de-c9a8-47c3-89d1-9635d212f027'
api_key_third = '2cf3c1e3-a1fa-4bb8-b35e-d31b5fac7ab6'
api_key_org_third = 'e75d7b73-904e-4afc-aa74-73023586bc71'


def check_same_coord_in_db(lat, lng, lat_list, lng_list):
    th = 0.015/40000*365
    for i in range(len(lat_list)):
        dist_temp = np.sqrt( (lat-lat_list[i])**2 + (lng-lng_list[i])**2 )
        if dist_temp < th:
            return True
    return False        


def resize(images_dir):
    names  = os.listdir(images_dir)
    img_names = [name for name in names if name[-4:]=='.tif']
    for name in img_names:
        img_path = images_dir + '/' + name
        new_path = 'test_resized/' + name
        img = cv2.imread(img_path)
        w, h = img.shape[0],img.shape[1]
        cropSize = int(w/2), int(h/2)
        img = Image.open(img_path)
        img.thumbnail(cropSize, Image.ANTIALIAS)
        img.save(new_path)


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
    



def dumb_coord_of_centers(df, masks_path, imgs_path, output_path_new,scale,scale_area,area_min,api_key,api_key_org):

    transformer = pyproj.Transformer.from_crs(crs_from="epsg:3857", crs_to="epsg:4326")
    masks = os.listdir(masks_path) 
    obj_id = df.shape[0]
    print('obj_id=',obj_id)
    for mask in masks:

        mask_name = mask.split('.')[0]
        crop_names = df['crop_name'].tolist()
        if mask_name in crop_names:
            print(f'{mask_name} is already in d_b')
            continue

        coeff = 2
        mask_path = masks_path +'/'+ mask
        original = cv2.imread('images/' + mask_name + '.png')

        coeff_area = 1
        if mask_name[:4] == 'tile':
            coeff = 1.25
            coeff_area = 1.65*1.65

        with open(imgs_path + mask_name + '.txt', 'r') as f:
            coord = f.readlines()
        
        
        # try:
        #     img_array = imageio.imread(mask_path)
        # except:
        #     print('error')
        #     continue

        img_array = np.load(mask_path)*255
        img_array = img_array[:,:,0]
        img_array_converted = img_array.astype(np.uint8)

        
        kernel = np.ones((15,15), np.uint8)
        opening = cv2.morphologyEx(img_array_converted, cv2.MORPH_OPEN, kernel)
        closing = cv2.morphologyEx(opening, cv2.MORPH_CLOSE, kernel)
        img_array_converted = closing
        contours, _ = cv2.findContours(img_array_converted, 
        cv2.RETR_TREE, cv2.CHAIN_APPROX_NONE)


        contours_filtered = []
        print(len(contours))
        
        for contour in contours:

            area = cv2.contourArea(contour)
            real_area = round(area * scale_area**2 *1/coeff_area,1)

            if real_area > area_min:
                M = cv2.moments(contour)
                contours_filtered.append(contour)
                cX = int(M["m10"] / M["m00"])
                cY = int(M["m01"] / M["m00"])
                
                obj_id+=1
                obj_x_coord = float(coord[0]) + cX*scale*coeff
                obj_y_coord = float(coord[1]) - cY*scale*coeff
                lng, lat = transformer.transform(obj_x_coord, obj_y_coord)

                # print(f'{lng} {lat} for object {count}, {obj[1]*scale}, {obj[2]*scale}')
                # original = cv2.circle(original, (cX, cY), 10, (255, 255, 255), -1)
                # original = cv2.putText(original, f" obj {obj_id}, area is {real_area} sq. meters", (cX - 20, cY - 20),
                # cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)

                # lat_list = df['lat'].tolist()
                # lng_list = df['lng'].tolist()
                # if check_same_coord_in_db(lat, lng, lat_list, lng_list):
                #     continue

                request = get_adress(lat, lng, api_key)
                # print(request)
                xmldoc = parseString(request)
                adresses = xmldoc.getElementsByTagName("text")
                address = adresses[0].firstChild.nodeValue
                print(address)
                organizations_list = []

                if not has_numbers(address):
                    obj_x_coord = float(coord[0]) + cX*scale*2
                    obj_y_coord = float(coord[1]) - cY*scale*2
                    lng, lat = transformer.transform(obj_x_coord, obj_y_coord)
                    request = get_adress(lat, lng, api_key)
                    xmldoc = parseString(request)
                    adresses = xmldoc.getElementsByTagName("text")
                    address = adresses[0].firstChild.nodeValue

                if has_numbers(address):
                    organizations = get_organizations(address, api_key_org)
                    if 'features' in organizations.keys():
                        org_list = organizations['features']
                    else:
                        continue    

                    for org in org_list:
                        temp_dict = {}
                        url, contacts = None, None
                        name = org['properties']['name']
                        name_of_categ = org['properties']['CompanyMetaData']['Categories'][0]['name']
                        if 'url' in org['properties']['CompanyMetaData'].keys():
                            url = org['properties']['CompanyMetaData']['url']
                        if 'Phones' in org['properties']['CompanyMetaData'].keys():
                            contacts = org['properties']['CompanyMetaData']['Phones'][0]['formatted']

                        temp_dict['name'] = name
                        temp_dict['type'] = name_of_categ
                        if contacts is not None:
                            temp_dict['phone'] = contacts
                        if url is not None:    
                            temp_dict['url'] = url 

                        organizations_list.append(temp_dict)
                        print(f'name is {name}, type is {name_of_categ}')
                
                df = df.append({'crop_name': mask_name,'object_id':obj_id, 'lng': lng,'lat': lat, 'real_area':real_area,'address':address, 'organizations': organizations_list}, ignore_index=True)
                # if obj_id % 5 == 0:
                df.to_csv(output_path + 'dumb_df_exp_filtered.csv', index=False)

        print(f"Number of filtered contours = {len(contours_filtered)} for mask {mask_name}")
        # mask_with_contours = cv2.drawContours(original, contours_filtered, -1, (0, 255, 0), 7)
        # cv2.imwrite(output_path_new + mask_name + '.png', img_array)
        # cv2.imwrite(output_path_new + mask_name + '_contour.png', mask_with_contours)
    return df


if __name__=="__main__":
    dumb_coord_of_centers(df, masks_path, imgs_path, output_path_new,scale,scale_area,area_min,api_key_ft,api_key_org_ft)