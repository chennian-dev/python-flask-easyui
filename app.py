#coding:utf-8
import json
import urllib2
import uuid
import pyamf
from flask import Flask
from pyamf import remoting
from pyamf.flex import messaging
iphost='http://47.97.100.171:8060'
app=Flask(__name__)
@app.route('/<phone>')
def code(phone):
	url='http://116.228.64.55:9093/IMEServer/messagebroker/amf'
	msg= messaging.RemotingMessage(messageId=str(uuid.uuid1()).upper(),
		clometOd=None,
		operation='executeQuery',
		destination='QueryService',
		timeTolive=0,
		timestamp=0
	)
	class AMS_VerificationCode:
		def __init__(self):
			self.phone = phone
			self.email = None
			self._svrvals = None
	msg.body = ['DE851B3A-ACD5-484B-B166-312B7CFFEA65.754B06107DE2',[],AMS_VerificationCode(),0,7]
	msg.headers['DSEndpoint'] = 'my-amf'
	msg.headers['DSId'] = str(uuid.uuid1()).upper()
	req = remoting.Request('null', body=(msg,))
	env = remoting.Envelope(amfVersion=pyamf.AMF0)
	env.bodies = [('/1' ,req)]
	data = bytes(remoting.encode(env).read())
	req = urllib2.Request(url,data,headers={'Cookie':'JSESSIONID=E92BD1159A4E6147968C9BEF084E30D5'})
	opener = urllib2.build_opener()
	resp = remoting.decode(opener.open(req).read())
	resmsg = resp.bodies[0][1]
	print len(resmsg.body.body)
	if len(resmsg.body.body)>1:
		rescode = resmsg.body.body[1][2]
		resMsg={"code":rescode}
	else:
		resMsg={"msg":"the telephone number is error"}
	return json.dumps(resMsg)

@app.route('/favicon.ico')
def favicon():
	return None

if __name__ == '__main__':
	app.run(debug=True,host='10.0.2.153', port=80)
