import uvicorn
from fastapi import FastAPI
from pydantic import BaseModel
import datetime
import time
import tinytuya
import json

app = FastAPI()

with open("/home/bob/deviceapi/devices.json") as fh:
	app.data = json.load(fh)

@app.get("/devicelist")
def devicelist():
	res = []
	for i in app.data:
		v = { 'id' : i['id'], 'name' : i['name'] }
		res.append(v)
#	res = ""
#	for i in app.data:
#		res.append
	return res

@app.get("/switch/{devname}/{newstate}")
def switch(devname: str, newstate: str):
	retname = 'unknown'
	retstate = 'unknown'
	retresult='fail'
	for i in app.data:
		if devname.casefold() == i['name'].casefold():
			retname=i['name']
			d=tinytuya.OutletDevice(dev_id=i['id'],address=i['ip'],local_key=i['key'], version=i['version'])
			if newstate.lower() == "on":
				d.turn_on()
				retstate=newstate
				retresult='On'
			if newstate.lower() == "off":
				d.turn_off()
				retstate=newstate
				retresult='Off'
	t = time.time()
	td = time.strftime('%Y%m%d',time.localtime(t))
	tt = time.strftime('%H%M%S',time.localtime(t))
	logfile = time.strftime('/home/bob/log/switch-summary-%Y%m.log',time.localtime(t))
	ls = "{ 'date' : '"+td+"', 'time' : '"+tt+"', 'Device' : '"+devname+"', 'result' : "+retresult+" }"
	with open(logfile, "a") as fh:
		fh.write(ls+"\n")
	fh.close()

	return { 'name' : retname, 'state' : retstate, 'result' : retresult}

@app.get("/dimmer/{devname}/{dimval}")
def dimmer(devname: str, dimval: str):
	result ='unknown'
	dv = int(dimval)
	for i in app.data:
		if devname.casefold() == i['name'].casefold():
			retname=i['name']
			d=tinytuya.OutletDevice(dev_id=i['id'],address=i['ip'],local_key=i['key'], version=i['version'])
			d.set_dimmer(dv)
			result = "dimmer set to "+str(dv)
	return { 'name' : retname, 'result' : result}


@app.get("/timer/{devname}/{timeval}")
def timer(devname: str, timeval: str):
	result= 'unknown'
	tv = int(timeval)
	for i in app.data:
		if devname.casefold() == i['name'].casefold():
			retname=i['name']
			d=tinytuya.OutletDevice(dev_id=i['id'],address=i['ip'],local_key=i['key'], version=i['version'])
			d.set_timer(tv)
			result = "timer set to "+str(tv)
	return { 'name' : retname, 'result' : result}

@app.get("/info/{id}")
def info(id: str):
	res = {}
	for i in app.data:
		if id.casefold() == i['name'].casefold():
			res = i
	return res 

@app.get("/status/{id}")
def status(id: str):
	res = { 'name' : id, 'status' : 'unknown'}
	for i in app.data:
		if id.casefold() == i['name'].casefold():
			d=tinytuya.OutletDevice(dev_id=i['id'],address=i['ip'],local_key=i['key'], version=i['version'])
			res = { 'name' : id, 'status' : d.status()}
#	return json.dumps(res) 
	return res 


if __name__ == "__main__":
    uvicorn.run("devices:app", port=8080, host='0.0.0.0', reload=True)
