import pandas as pd

def get_credibility_users(users):

    data = pd.read_csv('result.csv')
    json_list = []

    for t in users:
        if int(t) in data['id'].tolist():
            k = data.loc[data['id'] == int(t)]
            if 1 in k['result'].tolist():
                num_approved = k['result'].value_counts()[1]
            else:
                num_approved = 0
            
            if 0 in k['result'].tolist():
                num_disproved = k['result'].value_counts()[0]
            else:
                num_disproved = 0
            
            json_list.append({'user': t, 'approved': str(num_approved), 'disproved': str(num_disproved)})
        else:
            json_list.append({'user': 'Not found', 'approved': 'Not found', 'disproved': 'Not found'})
    
    return json_list


def get_all_users():

    data = pd.read_csv('/Users/kevin/desktop/Github/Safecast_api/result.csv')
    json_list = []

    for t in data['id'].value_counts().index:
        k = data.loc[data['id'] == t]
        if 1 in k['result'].tolist():
            num_approved = k['result'].value_counts()[1]
        else:
            num_approved = 0

        if 0 in k['result'].tolist():
            num_disproved = k['result'].value_counts()[0]
        else:
            num_disproved = 0

        json_list.append({'user': t, 'approved': str(num_approved), 'disproved': str(num_disproved)})
       
    return json_list