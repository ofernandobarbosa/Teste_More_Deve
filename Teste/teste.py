import os
import json
out_path = '../out/'
list_day = []
list_file = list(os.walk('../out'))[0][2]

for i in list_file:
    with open(f'{out_path}{i}', encoding='utf-8') as file:
        json_object = json.load(file)
        list_day.append(json_object['date'])
        file.close()
print(list_day)
