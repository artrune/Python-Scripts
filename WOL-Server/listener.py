import os
import traceback
import flask
from flask import request

app=flask.Flask(__name__)
app.config["DEBUG"]=True

#change macaddress to the computer mac address
#change wlan0 to eth0 if using ethernet
@app.route('/wake',methods=['GET'])
def wake():
    try:
        os.system("sudo etherwake -i wlan0 macaddress")
        return "Wake signal sent"
    except Exception as ex:
        return str(traceback.format_exc())

app.run(debug=True, port='43594',host='0.0.0.0')