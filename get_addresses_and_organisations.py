import pandas as pd
import numpy as np

import requests
from pandas import ExcelWriter
from xml.dom import minidom
from xml.dom.minidom import parseString
import geopy.distance

def has_numbers(inputString):
    return any(char.isdigit() for char in inputString)

def get_address(lng, lat, api_key,d_lng = 0.000085,d_lat = 0.000110):
    r = requests.get(f'https://geocode-maps.yandex.ru/1.x/?apikey={api_key}&geocode={lng},{lat}&spn={d_lng},{d_lat}')
    return r.text


def assign_close_cities(df_exp, cities):
    for iteration, row in df_exp.iterrows():
        lng = row['lng']
        lat = row['lat']
        point = (lat,lng)
        dist_min = 1000000
        closest_city = None
        for city in cities.keys():
            dist_temp = geopy.distance.geodesic(point, cities[city]).km
            if dist_temp < dist_min and dist_temp < 30:
                dist_min = dist_temp
                closest_city = city
        df_exp.at[iteration,'Город'] = closest_city
    return df_exp

def add_link(df_exp):
    df_exp['Объект на карте'] = None
    for iteration,row in df_exp.iterrows():
        lng = row['lng'] 
        lat = row['lat']
        url_alt = f"https://yandex.ru/maps/?whatshere[point]={lng},{lat}&whatshere[zoom]=17"
        url = f"https://yandex.ru/maps/?ll={lng},{lat}&pt={lng},{lat}&z=18&l=sat"
        hyper_url = f'=HYPERLINK("{url}", "Ссылка")'
    #     df_exp.at[iteration,'address'] = row['address'][7:]
        df_exp.at[iteration,'Объект на карте'] = hyper_url
    return df_exp  

def make_url(lat_list, lng_list, area_list):
    count = 0
    center_lat = 55.209123
    center_lng = 87.646385
    points_str = 'pt='
    for lat,lng,area in zip(lat_list, lng_list, area_list):
        
        if area<5000:
            continue
        lat = round(lat,4)
        lng = round(lng,4)
        temp_point = f'~{lng},{lat}'
        if count == 0:
            temp_point = f'{lng},{lat}'
        points_str += temp_point
        count+=1
    alt_url = f'https://yandex.ru/maps/67/tomsk/?l=sat&ll={center_lng},{center_lat}&{points_str}&z=7&l=map'
    url = f'https://yandex.ru/maps/?ll={tomsk_lng},{tomsk_lat}&{points_str}'
    return url, alt_url

def has_numbers(inputString):
    return any(char.isdigit() for char in inputString)

def correct_df(df):
    print(df.shape)
    df = df.drop_duplicates(['lng','lat'], keep= 'last')
    # df = df.drop_duplicates(['address'], keep= 'last')
    # df = df.drop_duplicates(['organizations'], keep= 'last')
    area_list = df['real_area'].tolist()
    crop_names = df['crop_name'].tolist()
    print(df.shape)
#     for i in range(len(crop_names)):
#         if crop_names[i][:4]=='tile':
#                 area_list[i] = area_list[i]/1.65/1.65
#     df['real_area'] = area_list

    return df

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


def main(cities, df_path, api_keys, api_keys_org):
    
    df = pd.read_csv(df_path)
    df = df[df['real_area']>1000]
    df = correct_df(df)
    df.reset_index(inplace = True)
    df_exp = df
    df_exp['Город'] = None
    df_exp['address'] = None
    df_exp = assign_close_cities(df_exp, cities)
    df_exp = add_link(df_exp)
    df_exp.sort_values(by=['real_area'],ascending=False, inplace = True)
    df_exp.reset_index(inplace = True,drop = True)
    df_exp.head()

    j = 0
    cnt = 0
    api_key = api_keys[j]
    for it, row in df_exp.iterrows():
        lat = row['lat']
        lng = row['lng']
        request = get_address(lng, lat, api_key)
        xmldoc = parseString(request)
        adresses = xmldoc.getElementsByTagName("text")
        if adresses == []:
            j+=1
            api_key = api_keys[j]

        address = adresses[0].firstChild.nodeValue
        df_exp.at[it,'address'] = address
        cnt+=1
        if cnt%10 == 0:
            print(f'Address {address} is added')

    df_exp.drop(['index','crop_name','object_id'],axis=1, inplace=True)
    df_exp.sort_values(by=['real_area'],ascending=False, inplace = True)
    df_exp.rename(columns={'address':'Адрес','real_area': 'Площадь, м.кв.','lng':'Долгота','lat':'Широта'}, inplace=True)
    df_exp.reset_index(inplace = True,drop = True)

    writer = ExcelWriter('Result.xlsx')
    df_exp.to_excel(writer,'Sheet5')
    writer.save()


if __name__=="__main__":
    df_path = 'outputs/dumb_df.csv'
    api_key = '428f4bec-2cf2-4d88-84b3-636539b76bea'
    api_key_ft = '6af69ba7-1b6c-4358-9f79-9c9cbc207f38'
    api_key_sec = '002fa019-bd47-481e-abce-6025ab30a425'
    api_key_org = '819baf3e-84e3-4156-894a-91235ea1191f'
    api_key_org_sec = '614ec352-af37-490c-aa9e-f7109b0a9b79'
    api_key_org_ft = '5e2b05de-c9a8-47c3-89d1-9635d212f027'
    api_key_third = '2cf3c1e3-a1fa-4bb8-b35e-d31b5fac7ab6'
    api_key_org_third = 'e75d7b73-904e-4afc-aa74-73023586bc71'
    
    api_keys = [api_key,api_key_sec,api_key_third,api_key_ft]
    api_org_keys = [api_key_org,api_key_org_sec,api_key_org_third,api_key_org_ft]

    cit = pd.read_csv('city.csv')
    city = cit[['city','geo_lat','geo_lon','population']]
    # city = city[city['geo_lat'] > 50]
    # city = city[city['geo_lat'] < 60]
    # city = city[city['geo_lon'] > 75]
    # city = city[city['geo_lon'] < 95]
    city = city[city['population'] > 10000]
    cities = {}
    for it, row in city.iterrows():
        cities[city['city'][it]] = (city['geo_lat'][it], city['geo_lon'][it])

    main(cities, df_path, api_keys, api_org_keys)