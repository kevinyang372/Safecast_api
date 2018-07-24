import requests
import csv

class user:
    def __init__(self,id):
        self.id = id
        self.approved_by = []
        self.disproved_by = []
    
    def approved_num(self):
        return len(self.approved_by)
    
    def disproved_num(self):
        return len(self.disproved_by)


def start_verification():
    users = get_full_json('https://api.safecast.org/users.json?')
    users_profile = []
    for i in users:
        print(i)
        if i['measurements_count'] == 0:
            users_profile.append(user(i['id']))
            continue;
        current_user = user(i['id'])
        record = get_full_json('https://api.safecast.org/measurements.json?user_id=' + str(i['id']) + '&')
        last_checked = [0,0]
        print(record)
        
        for k in range(len(record)):
            lat = record[k]['latitude']
            lng = record[k]['longitude']
            value = record[k]['value']
            if calculate_distance_weak([lat,lng],last_checked):
                continue
            else:
                last_checked = [lat,lng]
            
            nearby_points = get_full_json('https://api.safecast.org/measurements.json?distance=500&latitude=' + str(lat) + '&longitude=' + str(lng) + '&')
            
            print(nearby_points)
            
            for point in nearby_points:
                ratio = point['value'] / value
                if ratio > 2 or ratio < 0.5:
                    current_user.disproved_by.append([point['user_id'],point['latitude'],point['longitude'],ratio])
                else:
                    current_user.approved_by.append([point['user_id'],point['latitude'],point['longitude'],ratio])
        users_profile.append(current_user)
    return users_profile

def export_to_file():
    users_profile = start_verification()
    result_csv = []
    for t in users_profile:
        for k1 in t.approved_by:
            result_csv.append([t.id, k1[0], k1[1], k1[2], k1[3], 1])
        for k2 in t.disproved_by:
            result_csv.append([t.id, k2[0], k2[1], k2[2], k2[3], 0])
    with open('/home/ec2-user/result.csv', 'w') as myfile:
        wr = csv.writer(myfile)
        wr.writerow(['id','verifiedby','lat','lng','ratio','result'])
        wr.writerows(result_csv)

def get_full_json(url):
    
    pages = 1
    cumulated_result = []
    result = requests.get(url + 'page=' + str(pages)).json()
    cumulated_result += result
    
    while result != []:
        pages += 1
        result = requests.get(url + 'page=' + str(pages)).json()
        cumulated_result += result
        
    return cumulated_result

def calculate_distance_weak(point_1, point_2):
    
    lat1 = radians(point_1[0])
    lon1 = radians(point_1[1])
    lat2 = radians(point_2[0])
    lon2 = radians(point_2[1])
    
    dlon = lon2 - lon1
    dlat = lat2 - lat1
    
    if abs(dlon) < 0.0005 and abs(dlon) < 0.0005:
        return True
    
    return False