import pandas as pd

with open('humidity.json', encoding='utf-8-sig') as f_input:
   json = pd.read_json(f_input)

list = (([date, value]) for date, value in json['values'])

df = pd.DataFrame(list, columns=["time","humidity"])
df.to_csv("humidity.csv", index=False)
