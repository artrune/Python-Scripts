import time
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from influxdb import InfluxDBClient

influx_host = '192.168.1.82'
router_host = '192.168.1.254'
router_username = 'TELMEX'
router_password = ''

def write_to_influx(measurement_name, data_value):
    client = InfluxDBClient(influx_host, 8086, 'root', 'root', 'measurements')
    tags = {'host': 'pi_sensor', 'region': 'mx_south'} 
    data = {'value': data_value}
    client.write_points([{"measurement": measurement_name, "tags": tags, "fields": data}])    

def login():
    driver.get("http://"+router_host+"/status-and-support.html#sub=1&subSub=gpon_status")
    print(driver.title)
    username_field = driver.find_element_by_xpath('/html/body/div[1]/section/div[2]/div[2]/div[2]/div[1]/input')
    username_field.clear()
    username_field.send_keys(router_username)
    password_field = driver.find_element_by_xpath('/html/body/div[1]/section/div[2]/div[2]/div[2]/div[2]/input')
    password_field.send_keys(router_password)
    password_field.send_keys(Keys.RETURN)
    time.sleep(2)

def get_fiber_value():
    optic_metrics_link = driver.find_element_by_xpath('/html/body/div[1]/section/div/ul/li[1]/div/ul/li[5]/a/span')
    optic_metrics_link.click()
    time.sleep(2)
    fiber_value = driver.find_element_by_xpath('/html/body/div[1]/section/article/div/div[2]/div[1]/div[2]/span').text.replace("dBm", "")
    print(fiber_value)
    return fiber_value

def logout():
    logout_button = driver.find_element_by_xpath('//*[@id="logout"]')
    logout_button.click() 

while True:
    try:
        driver = webdriver.Chrome()
        login()
        fiber_value = get_fiber_value()    
        logout()
        write_to_influx('fiber', fiber_value)
        driver.quit()
    except Exception as e:
        driver.quit()
        print(str(e))
    time.sleep(40)

    