import pandas as pd

with open('temp.json', encoding='utf-8-sig') as f_input:
   json = pd.read_json(f_input)

list = (([date, value]) for date, value in json['values'])

df = pd.DataFrame(list, columns=["time","temp"])
df.to_csv("temp.csv", index=False)
