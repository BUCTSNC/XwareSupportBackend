from django.shortcuts import render
from django.http import HttpResponse
import json
import XwareSupportBackend.accessTokenCenter as access
from xwareBackend import myResponse
from xwareBackend.models import *
from xwareBackend.serializer import UserSerializers, FunctionarySerializers
from rest_framework.views import APIView
import requests
# Create your views here.
appId = access.appConfig['appId']
appSecret = access.appConfig['appSecret']


def hello(request):
    res = {"code": 200, "msg": "hello"}
    return HttpResponse(json.dumps(res), content_type="text/json")


class login(APIView):
    def get(self,request):
        if "jscode" not in request.query_params:
            return myResponse.Error("无jscode")
        jscode = request.query_params['request.query_params']
        openId = ""
        try:
            res = requests.get("https://api.weixin.qq.com/sns/jscode2session",params={
                "appid":appId,
                "secret":appSecret,
                "js_code":jscode,
                "grant_type":"authorization_code",
            },timeout=5)
            res = json.loads(res.text)
            openId = res['openid']
            request.session['openId'] = openId
            request.session['info'] = res
        except:
            return myResponse.Error("后端请求错误")
        return myResponse.OK("登录成功", {"userInfo": userHandle(request.session.get("openId"))})


def userHandle(openId):
    thisUser = None
    userList = user.objects.filter(openid=openId)
    userInfo = {"isNew":False,"info":None}
    if userList.count() == 0:
        thisUser = user(
            openId=openId
        )
        thisUser.save()
        userInfo['isnew'] = True
    else:
        thisUser = userList[0]
    userInfo['info'] = UserSerializers(thisUser, many=False).data
    return userInfo
