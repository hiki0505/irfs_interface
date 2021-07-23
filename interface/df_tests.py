import pandas as pd

data1 = pd.read_excel('dcorp1.xlsx', engine='openpyxl')

print(data1)

data_json = data1.to_json(orient='records')

print('*'*30)
print(data_json)
print('*'*30)

data_df = pd.read_json(data_json, orient='records')

print(data_df)