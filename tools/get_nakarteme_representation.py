mport pyproj
import numpy as np
import json
import base64
import click 
_projections = {}


def zone(coordinates):
    if 56 <= coordinates[1] < 64 and 3 <= coordinates[0] < 12:
        return 32
    if 72 <= coordinates[1] < 84 and 0 <= coordinates[0] < 42:
        if coordinates[0] < 9:
            return 31
        elif coordinates[0] < 21:
            return 33
        elif coordinates[0] < 33:
            return 35
        return 37
    return int((coordinates[0] + 180) / 6) + 1


def letter(coordinates):
    return 'CDEFGHJKLMNPQRSTUVWXX'[int((coordinates[1] + 80) / 8)]


def project(coordinates):
    z = zone(coordinates)
    l = letter(coordinates)
    if z not in _projections:
        _projections[z] = pyproj.Proj(proj='utm', zone=z, ellps='WGS84')
    x, y = _projections[z](coordinates[0], coordinates[1])
    if y < 0:
        y += 10000000
    return z, l, x, y


def coord_from_file(file_path):
    with open(file_path) as file:
        lines = file.readlines()
        lines = [line.rstrip() for line in lines]

    return float(lines[4]),float(lines[5])


def unproject(z, l, x, y):
    if z not in _projections:
        _projections[z] = pyproj.Proj(proj='utm', zone=z, ellps='WGS84')
    if l < 'N':
        y -= 10000000
    lng, lat = _projections[z](x, y, inverse=True)
    return (lng, lat)


def get_coord_from_pixels(li,start_coord_x,start_coord_y):
    return start_coord_x+li[0]/5000*250 , start_coord_y-li[1]/5000*250

def generate_link(x_center, y_center, base64):
    return 'https://nakarte.me/#m=19/{}/{}&l=E&q=%D0%B7%D0%B5%D0%BB%D0%B5%D0%BD%D0%BE%D0%B3%D1%80%D0%B0%D0%B4&nktj={}'.format(center_coord_x, center_coord_y, base64)






file_path = 'Moscow_img_sec.tfw'

start_coord_x, start_coord_y = coord_from_file(file_path)
center_coord_x = start_coord_x + 125
center_coord_y = start_coord_y + 125

coord = [37.23, 55.9]
z = zone(coord)
l = letter(coord)
# point_one = [start_coord_x,start_coord_y]
# x_point_one, y_point_one = get_coord_from_pixels(point_one,start_coord_x,start_coord_y)



x_point_one = 4186059.520
y_point_one = 7504538.766


transformer = pyproj.Transformer.from_crs("epsg:3857", "epsg:4326")
result = transformer.transform(x_point_one, y_point_one)
print(result)



# roads = np.load("roads.npy", allow_pickle=True)

# # example = [{"n": "Road_26", "t": [[[[55.98888403551749, 37.2324196652384], [55.98887962558212, 37.232425477747874]],[55.98, 37.15]]]}]
# # b = [{'n': 'The_track1', 't': [[[55.993729471648096, 37.28221676320819], [55.99332992068186, 37.23221674271015]], [[55.991248342, 37.232223707315],[55.8633541248342, 37.232223707316585] ]] }]

# step = 10
# s = []
# for i,line in enumerate(roads):

#     if (len(line)-step)/step < 5:
#             continue
#     d = {}
#     a = []
#     d["n"] = "Road_{}".format(i)

#     for j in range(0,len(line)-step, step):

#         point_one = line[j]
#         point_two = line[j+step]

#         x_point_one, y_point_one = get_coord_from_pixels(point_one,start_coord_x,start_coord_y)
#         x_point_two, y_point_two = get_coord_from_pixels(point_two,start_coord_x,start_coord_y)

#         lng_one, lat_one = unproject(z, l, x_point_one, y_point_one)
#         lng_two, lat_two = unproject(z, l, x_point_two, y_point_two)
#         a.append([[round(lat_one,7),round(lng_one,7)],[round(lat_two,7),round(lng_two,7)]])

#     d["t"] = a
#     s.append(d) 

# json = json.dumps(s) 
# base64 = str(base64.b64encode(json.encode('utf-8')))[2:]
# lng_center, lat_center = unproject(z, l, center_coord_x, center_coord_y)
# print(generate_link(lng_center, lat_center, base64))


# def convert_image_to_npy():
#     pass