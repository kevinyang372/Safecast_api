import pandas as pd

def get_credibility_users(users, ids, results):

    json_list = []

    for t in users:
        if int(t) in set(ids):

            num_approved = 0
            num_disproved = 0

            for num in range(len(ids)):
                if int(t) == ids[num]:
                    if results[num] == 1:
                        num_approved += 1
                    else
                        num_disproved += 1
            
            json_list.append({'user': t, 'approved': str(num_approved), 'disproved': str(num_disproved)})
        else:
            json_list.append({'user': 'Not found', 'approved': 'Not found', 'disproved': 'Not found'})
    
    return json_list


def get_all_users(ids, results):

    json_list = []

    for t in set(ids):
        num_approved = 0
        num_disproved = 0
        for num in range(len(ids)):
            if ids[num] == t and results[num] == 1:
                num_approved += 1
            elif ids[num] == t and results[num] == 0:
                num_disproved += 1

        json_list.append({'user': t, 'approved': str(num_approved), 'disproved': str(num_disproved)})
       
    return json_list