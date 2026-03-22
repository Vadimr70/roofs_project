import pandas as pd
import numpy as np

tomsk_lng = '84.969883'
tomsk_lat = '56.475882'

lng_int2  = 84.973885
lat_int2 = 56.523383

lng_int = 85.104103
lat_int = 56.519434


def find_closest_point(lat_list,lng_list,lat_point,lng_point,list_of_names):
    dist_min = 100
    dist_second = 0
    cnt = 0
    cnt_min = 0
    name = ''
    for crop_name,lat,lng in zip(list_of_names, lat_list, lng_list):
        dist_temp = np.sqrt( (lat_point-lat)**2 + (lng_point-lng)**2 )
        cnt+=1
        if dist_temp < dist_min:
            cnt_min = cnt
            dist_second = dist_min
            name_second = name
            dist_min = dist_temp
            name = crop_name
    return cnt_min, dist_min,name, dist_second, name_second        



def correct_df(df):
    print(df.shape)
    df = df.drop_duplicates(['lng','lat'], keep= 'last')
    # df = df.drop_duplicates(['address'], keep= 'last')
    # df = df.drop_duplicates(['organizations'], keep= 'last')
    area_list = df['real_area'].tolist()
    crop_names = df['crop_name'].tolist()
    print(df.shape)
    for i in range(len(crop_names)):
        if crop_names[i][:4]=='tile':
                area_list[i] = area_list[i]/1.65/1.65
    df['real_area'] = area_list            
    return df



def has_numbers(inputString):
    return any(char.isdigit() for char in inputString)



def make_url(lat_list, lng_list, addresses, area_list):
    count = 0
    points_str = 'pt='
    for lat,lng,address,area in zip(lat_list, lng_list, addresses, area_list):
        
        if area<2500:
            continue
        lat = round(lat,4)
        lng = round(lng,4)
        temp_point = f'~{lng},{lat}'
        if count == 0:
            temp_point = f'{lng},{lat}'
        points_str += temp_point
        count+=1

    url  = f'https://yandex.ru/maps/?ll={tomsk_lng},{tomsk_lat}&{points_str}&z=12&l=sat'
    return url



output_path = 'outputs/masks_viz/'

df = pd.read_csv('outputs/masks_viz/dumb_df_exp_filtered.csv')
df = correct_df(df)

print(df[df['crop_name']=='big_15_31'].shape)
# df.to_csv(output_path + 'dumb_df_exp_filtered.csv', index=False)

lat_list = df['lng'].tolist()
lng_list = df['lat'].tolist()
addresses = df['address'].tolist()
area_list = df['real_area'].tolist()
list_of_names = df['crop_name'].tolist()
url = make_url(lat_list, lng_list, addresses, area_list)
print(url)

# 85.023749%2C56.504062
lat_point = 56.504062
lng_point = 85.023749
cnt_min, dist_min, name ,d_sec,name_sec= find_closest_point(lat_list,lng_list,lat_point,lng_point,list_of_names)
print(cnt_min)
print(dist_min)
print(name)
print(d_sec)
print(name_sec)