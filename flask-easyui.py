# -*- coding: utf-8 -*-
import urllib2
import uuid
import pyamf
from pyamf import remoting
from pyamf.flex import messaging
import json
from flask import Flask, render_template, request
import time
import requests
iphost='http://47.97.100.171:8060'
app=Flask(__name__)

@app.route("/")
def index():
# 主页面
    return render_template("main.html")
    
@app.route("/smscode")
def smscode():
# tab测试界面
    return render_template("smscode.html")

@app.route('/getCode', methods=['POST'])
def getCode():
    phone = request.json['phone']
    print phone
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
    req = urllib2.Request(url,data,headers={'Cookie':'JSESSIONID=5F1A0F83802E99325C460D2AB505E91C'})
    opener = urllib2.build_opener()
    resp = remoting.decode(opener.open(req).read())
    resmsg = resp.bodies[0][1]
    print resmsg
    print len(resmsg.body.body)
    if len(resmsg.body.body)>1:
        rescode = resmsg.body.body[1][2]
        resMsg={"msg":rescode,"code":"0"}
    else:
        resMsg={"msg":"the telephone number is error","code":'-1'}
    return json.dumps(resMsg)



@app.route("/create")
def create():
    return render_template("createuser.html")


@app.route("/createuser", methods=['POST'])
def createuser():
    # 1、请求发送验证码
    phone = request.json['phone']
    print phone
    url=iphost +'/v2.0/user/cuser/smsCode'
    data = {"cs":int(time.time()),"phone":phone,"zone":"0086","type":"0","operType":"1"}
    req = requests.post(url,json=data)
    time.sleep(0.1)
    # 2、获取验证码
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
    req = urllib2.Request(url,data,headers={'Cookie':'JSESSIONID=5F1A0F83802E99325C460D2AB505E91C'})
    opener = urllib2.build_opener()
    resp = remoting.decode(opener.open(req).read())
    resmsg = resp.bodies[0][1]
    print len(resmsg.body.body)
    rescode=''
    resMsg={}
    if len(resmsg.body.body)>1:
        rescode = resmsg.body.body[1][2]
    else:
        resMsg={"msg":"the telephone number is error","code":'-1'}
    # 注册用户
    url=iphost +'/v2.0/user/cuser/register'
    data = {"password":"4CfJvm60Btlokx9zwGIhWQ==","phone":phone,"zone":"0086","againPassword":"4CfJvm60Btlokx9zwGIhWQ==","acode":rescode,"type":"0"}
    result = requests.post(url,json=data).json()
    print result
    print "注册返回状态： %s"  % result['code']
    if result['code'] == 200:
        tokenVal = result.get('data').get('accessToken').get('value')
        userid = result.get('data').get('accessToken').get('account').get('accountId')
        resMsg = {"code":'0',"msg":"用户id为："+str(userid)+",用户token为："+str(tokenVal)}
    else:
        resMsg={"msg":"register fail","code":'-1'}
    print resMsg
    return json.dumps(resMsg)

# @app.route("/createuser2auth", methods=['POST'])
# def createuser2auth(phone,password,name,idcard):
#     phone = request.json['phone']
#     password = request.json['password']
#     name = request.json['name']
#     idcard = request.json['idcard']
#     url=iphost +'/v2.0/user/cuser/login'
#     params={"userParam":phone,"password":"4CfJvm60Btlokx9zwGIhWQ=="}
#     responselogin = requests.post(url,json=params).json()
#     time.sleep(0.1)
#     tokenVal = responselogin.get('data').get('accessToken').get('value')
#     userid = responselogin.get('data').get('accessToken').get('account').get('accountId')
#     # 实名认证
#     url=iphost +'/v2.0/user/cuser/realname/auth'
#     headers={"Authorization":"Bearer " + tokenVal}
#     data = {"identityNo":idcard,"identityType":1,"accountType":1,"mobile":phone,"name":name}
#     response1 = requests.post(url,json=data,headers=headers)
#     print "实名返回状态： %s"  % response1.json()['code']
#     # 上传身份证
#     url=iphost +'/v2.0/user/cuser/info/update'
#     headers={"Authorization":"Bearer " + tokenVal}
#     data = {"certFrontPhoto":"http://img.fbh-china.com/images/1541575444375_1424.png","certBackPhoto":"http://img.fbh-china.com/images/1541575444623_4420.png","id":userid,"certHoldPhoto":"http://img.fbh-china.com/images/1541575444698_4847.png"}
#     response2 = requests.post(url,json=data,headers=headers)
#     print "上传身份证返回状态： %s"  % response2.json()['code']
#     resMsg={"msg":str(response2.json()['code']),"code":'0'}
#     return json.dumps(resMsg)

@app.route("/tab2")
def tab2():
# tab测试界面
    return render_template("tab2.html")

if __name__=="__main__":
    app.run(host = "10.0.2.153",port = 8080, debug = True)
