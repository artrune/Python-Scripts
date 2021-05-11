
api_key = ''
secret = ''
org_id = ''

connect = 'postgres://postgres:pa$$@192.168.1.114:5432/nh_soc'

from datetime import datetime, timezone
from typing import List
from api_client import private_api
import json
import psycopg2
import traceback
import time

api_client = private_api('https://api2.nicehash.com',org_id,api_key, secret)

def get_rig_data():
    response = api_client.request('GET','/main/api/v2/mining/rigs2','',None)
    if response.ok:
        data = response.json()
        total_rigs = data['totalRigs']
        miners_on = data['minerStatuses']['MINING'] if 'MINING' in data['minerStatuses'] else 0
        miners_off = data['minerStatuses']['OFFLINE'] if 'OFFLINE' in data['minerStatuses'] else 0
        total_profitabiliy = data['totalProfitability']
        unpaid_amount = data['unpaidAmount']
        global_data = GlobalData(total_rigs, miners_on, miners_off, total_profitabiliy, unpaid_amount)
        for rig_data in data['miningRigs']:
            name = rig_data['name']
            id = rig_data['rigId']
            rig = RigData(name, id)
            global_data.add_rig(rig)
            for device in rig_data['devices']:
                if device['deviceType']['enumName'] == 'NVIDIA':
                    name = device['name']
                    id = device['id']
                    core_temp = device['temperature'] % 65536
                    vram_temp = device['temperature'] / 65536
                    consumption = device['powerUsage']
                    hash_rate = float(device['speeds'][0]['speed'])
                    rig.hash_rate = global_data.hash_rate + hash_rate
                    rig.energy_consumpton = global_data.consumption + consumption
                    global_data.hash_rate = global_data.hash_rate + hash_rate
                    global_data.consumption = global_data.consumption + consumption
                    device = DeviceData(name, id, core_temp, vram_temp, consumption, hash_rate)
                    rig.add_device_data(device)
        return global_data
    return None


class DeviceData:
    def __init__(self, name, id, core_temp, vram_temp, energy_consumption, hash_rate):
        self.name = name
        self.id = id
        self.core_temp = core_temp
        self.vram_temp = vram_temp
        self.energy_consumpton = energy_consumption
        self.hash_rate = hash_rate

class RigData:
    def __init__(self, name, id):
        self.name = name
        self.id = id
        self.device_data = list() 
        self.hash_rate = 0
        self.energy_consumpton = 0

    def get_devices_data(self) -> List[DeviceData]:
        return self.device_data
    
    def add_device_data(self, device:DeviceData):
        self.device_data.append(device)

class GlobalData:

    def __init__(self, rigs_count, miners_on, miners_off, total_profitability, unpaid_amount):
        self.rigs_count = rigs_count
        self.miners_on = miners_on
        self.miners_off = miners_off
        self.total_profitability = total_profitability
        self.unpaid_amount = unpaid_amount
        self.rigs = list()
        self.consumption = 0
        self.hash_rate = 0

    def get_rigs(self) -> List[RigData]:
        return self.rigs
    
    def add_rig(self, rig:RigData):
        self.rigs.append(rig)

    def toJson(self):
        return json.dumps(self, default=lambda o: o.__dict__)


#
while 1:
    try:
        timestamp = datetime.now(timezone.utc).isoformat()
        data=get_rig_data()
        if data is not None:
            with psycopg2.connect(connect) as connection:
                cursor = connection.cursor()
                cursor.execute(f"insert into public.global_data values ('{data.rigs_count}', '{data.miners_on}', '{data.miners_off}', '{data.total_profitability}', '{data.unpaid_amount}', '{timestamp}')")
                for rig in data.get_rigs():
                    cursor.execute(f"insert into public.rig values('{rig.name}', '{rig.id}') ON CONFLICT (id) DO NOTHING;")
                    cursor.execute(f"insert into public.rig_data values('{timestamp}', '{rig.id}', '{rig.hash_rate}', '{rig.energy_consumpton}')")
                    connection.commit()
                    for device in rig.get_devices_data():
                        cursor.execute(f"insert into public.device values('{rig.id}', '{device.id}', '{device.name}') ON CONFLICT (rig_id, id) DO NOTHING;")
                        cursor.execute(f"insert into public.device_data values('{device.id}', '{rig.id}', '{timestamp}', '{device.core_temp}', '{device.vram_temp}', '{device.energy_consumpton}', '{device.hash_rate}')")
                connection.commit()
                cursor.close()
            print("populated")
            time.sleep(60)
    except Exception as ex:
        print(str(ex) + traceback.format_exc())