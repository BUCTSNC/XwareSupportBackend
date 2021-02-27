from django.shortcuts import render
from django.http import HttpResponse
import json
import XwareSupportBackend.accessTokenCenter as access
from xwareBackend import myResponse
from xwareBackend.models import *
from xwareBackend.serializer import UserSerializers, FunctionarySerializers, \
    mainProblemSerializers, timeSlotSerializers, shortAppointmentSerializers, \
    AppointmentDetailSerializers, shortEventSerializers, EventSerializers
from rest_framework.views import APIView
import requests
import uuid
import hashlib
from rest_framework.pagination import PageNumberPagination
from xwareBackend.AliyunImage import upload


class SelfdefinedPage(PageNumberPagination):
    page_size_query_param = "size"
    page_query_param = "page"


# Create your views here.
appId = access.appConfig['appId']
appSecret = access.appConfig['appSecret']


class login(APIView):
    def get(self, request):
        if "jscode" not in request.query_params:
            return myResponse.Error("无jscode")
        jscode = request.query_params['jscode']
        openId = ""
        try:
            res = requests.get("https://api.weixin.qq.com/sns/jscode2session", params={
                "appid": appId,
                "secret": appSecret,
                "js_code": jscode,
                "grant_type": "authorization_code",
            }, timeout=5)
            res = json.loads(res.text)
            openId = res['openid']
            request.session['openId'] = openId
            request.session['info'] = res
        except:
            return myResponse.Error("后端请求错误")
        return myResponse.OK("登录成功", {"userInfo": userHandle(request.session.get("openId"))})


class ProblemType(APIView):
    def get(self, request):
        problemtypes = mainProblemType.objects.all()
        ser = mainProblemSerializers(problemtypes, many=True)
        data = ser.data
        return myResponse.OK(data=data)


def userHandle(openId):
    thisUser = None
    userList = user.objects.filter(openid=openId)
    userInfo = {"isNew": False, "info": None}
    if userList.count() == 0:
        thisUser = user(
            openid=openId
        )
        thisUser.save()
        userInfo['isNew'] = True
    else:
        thisUser = userList[0]
    userInfo['info'] = UserSerializers(thisUser, many=False).data
    return userInfo


class setUserInfo(APIView):
    def post(self, request):
        data = request.data
        if not request.session.has_key("openId") or request.session.get("openId") == "":
            return myResponse.AuthError("您未登录")
        if not ("realName" in data and "phone" in data and "NO" in data):
            return myResponse.Error("请求参数过少")
        try:
            realName = request.data["realName"]
            phone = request.data["phone"]
            NO = request.data["NO"]
            thisUser = user.objects.get(openid=request.session.get("openId"))
            thisUser.realName = realName
            thisUser.phone = phone
            thisUser.NO = NO
            thisUser.save()
        except:
            return myResponse.Error("后端异常")
        return myResponse.OK("修改成功", {"userInfo": userHandle(request.session.get("openId"))})


class TimeslotList(APIView):
    def get(self, request):
        timeslots = TimeSlot.objects.all()
        return myResponse.OK(data=timeSlotSerializers(timeslots, many=True).data)


class AppointmentManager(APIView):
    def post(self, request):
        data = request.data
        if not request.session.has_key("openId") or request.session.get("openId") == "":
            return myResponse.AuthError("您未登录")
        if not ("problemType" in data and "ProblemDetail" in data and "sid" in data):
            return myResponse.Error("请求参数过少")
        try:
            sid = data['sid']
            problemType = data['problemType']
            ProblemDetail = data['ProblemDetail']
            thisUUID = uuid.uuid4()
            thisUser = user.objects.get(openid=request.session.get("openId"))
            thisSlot = TimeSlot.objects.get(id=int(sid))
            exist = Appointment.objects.filter(user=thisUser, slot__Date=thisSlot.Date, status__lte=4)
            if exist.count() != 0:
                return myResponse.AuthError("该日您已有预约")
            sourseInfo = {
                "realName": thisUser.realName,
                "phone": thisUser.phone,
                "NO": thisUser.NO,
            }
            newAppointment = Appointment(
                problemType=problemType,
                uuid=thisUUID,
                user=thisUser,
                slot=thisSlot,
                describe=ProblemDetail,
                sourseInfo=sourseInfo,
            )
            newAppointment.save()
        except:
            return myResponse.Error("后端异常")
        return myResponse.OK("提交成功", data=shortAppointmentSerializers(newAppointment).data)

    def get(self, request):
        if not request.session.has_key("openId") or request.session.get("openId") == "":
            return myResponse.AuthError("您未登录")
        try:
            aid = request.query_params['aid']
            thisAppointment = Appointment.objects.get(id=int(aid))
        except:
            return myResponse.Error("预约获取异常")
        if request.session.get("openId") != thisAppointment.user.openid:
            return myResponse.AuthError("您无权获取该预约")
        return myResponse.OK(data=AppointmentDetailSerializers(thisAppointment).data)


class myAppointment(APIView):
    def get(self, request):
        if not request.session.has_key("openId") or request.session.get("openId") == "":
            return myResponse.AuthError("您未登录")
        allApp = Appointment.objects.filter(user__openid=request.session.get("openId")).order_by("-id")
        return myResponse.OK(data=shortAppointmentSerializers(allApp, many=True).data)


class bindFunctionary(APIView):
    def post(self, request):
        if not request.session.has_key("openId") or request.session.get("openId") == "":
            return myResponse.AuthError("您未登录")
        thisUser = user.objects.get(openid=request.session.get("openId"))
        try:
            username = request.data['username']
            password = request.data['password']
            thisFunctionary = functionary.objects.get(userName=username)
            finalPassword = passwordSalt(password)
            if thisFunctionary.passWord != finalPassword:
                return myResponse.AuthError("密码错误")
            thisFunctionary.user = thisUser
            thisFunctionary.save()
        except:
            return myResponse.Error("后端异常")
        return myResponse.OK(data={"userInfo": userHandle(request.session.get("openId"))})


class startEvent(APIView):
    def get(self, request):
        if not request.session.has_key("openId") or request.session.get("openId") == "":
            return myResponse.AuthError("您未登录")
        try:
            thisFunctionary = functionary.objects.get(user__openid=request.session.get("openId"))
        except:
            return myResponse.AuthError("您不是工作人员")
        try:
            UUID = request.query_params['uuid']
            thisAppointment = Appointment.objects.get(uuid=UUID)
        except:
            return myResponse.AuthError("预约获取错误")
        try:
            thisEvent = event(appointment=thisAppointment, handler=thisFunctionary, status="正在维修")
            thisEvent.save()
            thisAppointment.status = 3
            thisAppointment.save()
        except:
            return myResponse.Error("后端异常")
        return myResponse.OK("绑定成功", data={"eid": thisEvent.id})


class myHandleEvent(APIView):
    def get(self, request):
        if not request.session.has_key("openId") or request.session.get("openId") == "":
            return myResponse.AuthError("您未登录")
        try:
            thisFunctionary = functionary.objects.get(user__openid=request.session.get("openId"))
        except:
            return myResponse.AuthError("您不是工作人员")
        allMyEvent = event.objects.filter(handler=thisFunctionary).order_by("-id")
        pg = SelfdefinedPage()
        pgr = pg.paginate_queryset(
            queryset=allMyEvent, request=request, view=self)
        return myResponse.OK(data=shortEventSerializers(pgr, many=True).data)


class Event(APIView):
    def get(self, request):
        if not request.session.has_key("openId") or request.session.get("openId") == "":
            return myResponse.AuthError("您未登录")
        try:
            eid = request.query_params['eid']
            thisEvent = event.objects.get(id=int(eid))
        except:
            return myResponse.Error("后端异常")
        if thisEvent.handler.user.openid == request.session.get("openId"):
            return myResponse.OK(data=EventSerializers(thisEvent).data)
        elif thisEvent.appointment.user.openid == request.session.get("openId"):
            return myResponse.OK(data=EventSerializers(thisEvent).data)
        else:
            return myResponse.AuthError("您无权限查看该事件")

    def post(self, request):
        if not request.session.has_key("openId") or request.session.get("openId") == "":
            return myResponse.AuthError("您未登录")
        try:
            eid = request.data['eid']
            thisEvent = event.objects.get(id=int(eid))
        except:
            return myResponse.Error("后端异常")
        if thisEvent.handler.user.openid != request.session.get("openId"):
            return myResponse.AuthError("您无权修改该事件")
        try:
            detectProblemType = request.data['detectProblemType']
            detectInfo = request.data['detectInfo']
            handleWay = request.data['handleWay']
            finalStatus = request.data['finalHandle']
            thisEvent.detectInfo = detectInfo
            thisEvent.handlerWay = handleWay
            thisEvent.finalStatus = finalStatus
            thisEvent.detectProblemType = detectProblemType
            thisEvent.save()
        except:
            return myResponse.Error("后端异常")
        return myResponse.OK(data=EventSerializers(thisEvent).data)



def passwordSalt(sourcePassword):
    salt = hashlib.md5(sourcePassword.encode("utf-8")).hexdigest()
    saltPassword = salt + sourcePassword
    finalPassword = hashlib.sha256(saltPassword.encode("utf-8")).hexdigest()
    return finalPassword


class imageUpload(APIView):
    def put(self, request):
        if not request.session.has_key("openId") or request.session.get("openId") == "":
            return myResponse.AuthError("您未登录")
        try:
            thisFunctionary = functionary.objects.get(user__openid=request.session.get("openId"))
        except:
            return myResponse.AuthError("您不是工作人员")
        try:
            img = request.FILES.get("img")
        except:
            return myResponse.Error("上传异常")

