import pandas as pd
from datetime import datetime
from time import sleep
from random import randint

from sfc_traffic_repository import SfcTrafficRepository

df = pd.read_csv('cluster_1.csv')
df = df[['date','mean']]

sfc_traffic_reposityory = SfcTrafficRepository()


sfc_id = 'my-sfc'

# minute = datetime.utcnow()#.replace(second=0, microsecond=0)
# data = {"traffic": randint(0,100)}

physical_links = [(0, 1), (1, 10)]

for i, row in df.iterrows():
    # print(row['date'])
    # print(row['mean'])
    traffic = {'date': row['date'], 'traffic': row['mean']}
    sfc_traffic_reposityory.insert_measurement(sfc_id, traffic, physical_links)

    # sleep(2)

    if i > 30:
        break

# data = sfc_traffic_reposityory.get_sfc_traffic_by_sfc_id(sfc_id)

# if len(data)>0:
#     traffic_sfc = data[0]['d']
#     print(traffic_sfc)
# else:
#     print('There is no data about the selected SFC')

# for x in data:
#     print(x)


# sfc_traffic_reposityory.delete_sfc_traffic(sfc_id)