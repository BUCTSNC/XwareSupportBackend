import json

from django.shortcuts import render
from xwareBackend.models import *
from xwareBackend.views import passwordSalt
from rest_framework.views import APIView
from xwareBackend import myResponse
from xwareBackend import serializer as f_serializer
from functools import wraps
import datetime, time


def login_decorate(func):
    @wraps(func)
    def wrapper(self, request):
        if not request.session.has_key('username') or request.session.get('username') == "":
            return myResponse.AuthError("您未登录")
        return func(self, request)

    return wrapper


def manage_decorate(power=2):
    def decorator(func):
        @login_decorate
        def wrapper(self, request):
            if (not request.session.has_key("auth")) or request.session.get("auth") < power:
                return myResponse.AuthError("权限不足")
            return func(self, request)

        return wrapper

    return decorator


# Create your views here.
class login(APIView):
    def post(self, request):
        data = json.loads(request.body)
        if "username" not in data or "password" not in data:
            return myResponse.Error("数据不全")
        username = data['username']
        password = passwordSalt(data['password'])
        userList = functionary.objects.filter(userName=username)
        if userList.count() == 0:
            return myResponse.AuthError("无此用户")
        thisuser = userList[0]
        if thisuser.passWord != password:
            return myResponse.AuthError("密码错误")
        request.session['auth'] = thisuser.auth
        request.session['username'] = thisuser.userName
        return myResponse.OK("登录成功", f_serializer.FunctionarySerializers(thisuser).data)


class logout(APIView):
    @login_decorate
    def get(self, request):
        request.session.flush()
        return myResponse.OK("退出成功")


class checkLogin(APIView):
    @login_decorate
    def get(self, request):
        username = request.session.get("username")
        userList = functionary.objects.filter(userName=username)
        if userList.count() == 0:
            return myResponse.Error("无此用户")
        thisuser = userList[0]
        return myResponse.OK("已登录", f_serializer.FunctionarySerializers(thisuser).data)


class User(APIView):
    @login_decorate
    def get(self, request):
        userList = functionary.objects.filter(auth__lt=request.session.get("auth"))
        return myResponse.OK(data=f_serializer.FunctionarySerializers(userList, many=True).data)

    @login_decorate
    def post(self, request):
        if request.session.get("auth") < 4:
            return myResponse.AuthError("您无此权限")
        js_body = json.loads(request.body)
        try:
            username = js_body['username']
            password = js_body['password']
            realName = js_body['realName']
            auth = js_body['auth']
        except:
            return myResponse.Error("字段不全")
        if functionary.objects.filter(userName=username).count() != 0:
            return myResponse.Error("已存在用户名")
        if request.session.get("auth") <= int(auth):
            return myResponse.AuthError("权限不足")
        newFunctionary = functionary(
            userName=username,
            passWord=passwordSalt(password),
            auth=int(auth),
            realName=realName,
        )
        newFunctionary.save()
        return myResponse.OK(data=f_serializer.FunctionarySerializers(newFunctionary).data)

    @login_decorate
    def put(self, request):
        try:
            fid = request.query_params['fid']
            thisFunctionary = functionary.objects.get(id=fid)
        except:
            return myResponse.Error("后端错误")
        if thisFunctionary.userName != request.session.get("username") and request.session.get(
                "auth") <= thisFunctionary.auth:
            return myResponse.AuthError("您无此权限")
        js_body = json.loads(request.body)
        try:
            realName = js_body['realName']
            if request.session.get("auth") >= 4 and int(js_body['auth']) < request.session.get("auth"):
                auth = js_body['auth']
            else:
                auth = thisFunctionary.auth
        except:
            return myResponse.Error("字段不足")
        thisFunctionary.auth = auth
        thisFunctionary.realName = realName
        thisFunctionary.save()
        return myResponse.OK(data=f_serializer.FunctionarySerializers(thisFunctionary).data)


class changePassword(APIView):
    @login_decorate
    def post(self, request):
        try:
            fid = request.query_params['fid']
            thisFunctionary = functionary.objects.get(id=fid)
        except:
            return myResponse.Error("后端错误")
        if thisFunctionary.userName != request.session.get("username") and request.session.get(
                "auth") <= thisFunctionary.auth:
            return myResponse.AuthError("您无此权限")
        js_body = json.loads(request.body)
        try:
            old = js_body['old']
            newPassword = js_body['new']
        except:
            return myResponse.Error("字段错误")
        if request.session.get("auth") >= 4:
            thisFunctionary.passWord = passwordSalt(newPassword)
        else:
            if thisFunctionary.passWord == passwordSalt(old):
                thisFunctionary.passWord = passwordSalt(newPassword)
            else:
                return myResponse.Error("旧密码错误")
        thisFunctionary.save()
        return myResponse.OK("修改成功")


class timeSlop(APIView):
    @login_decorate
    def get(self, request):
        allTime = TimeSlot.objects.all().order_by("-id")
        return myResponse.OK(data=f_serializer.timeSlotSerializers(allTime, many=True).data)

    @manage_decorate(3)
    def post(self, request):
        try:
            js_body = json.loads(request.body)
            date = datetime.datetime.strptime(js_body['date'], "%Y-%m-%d")
            starttime = datetime.datetime.strptime(js_body['start'], "%Y-%m-%d %H:%M:%S")
            endtime = datetime.datetime.strptime(js_body['end'], "%Y-%m-%d %H:%M:%S")
            number = int(js_body['number'])
        except:
            return myResponse.Error("后端异常")
        newTimeSlop = TimeSlot(
            Date=date,
            Start=starttime,
            End=endtime,
            AllowNumber=number
        )
        newTimeSlop.save()
        return myResponse.OK(data=f_serializer.timeSlotSerializers(newTimeSlop).data)

    @manage_decorate(3)
    def put(self, request):
        try:
            tid = int(request.query_params['tid'])
            js_body = json.loads(request.body)
            date = datetime.datetime.strptime(js_body['date'], "%Y-%m-%d")
            starttime = datetime.datetime.strptime(js_body['start'], "%Y-%m-%d %H:%M:%S")
            endtime = datetime.datetime.strptime(js_body['end'], "%Y-%m-%d %H:%M:%S")
            number = int(js_body['number'])
        except:
            return myResponse.Error("后端异常")
        try:
            thisTimeSlop = TimeSlot.objects.get(id=tid)
        except:
            return myResponse.Error("无法取得此时间段")
        thisTimeSlop.Date = date
        thisTimeSlop.Start = starttime
        thisTimeSlop.End = endtime
        thisTimeSlop.AllowNumber = number
        thisTimeSlop.save()
        return myResponse.OK(data=f_serializer.timeSlotSerializers(thisTimeSlop).data)


class AP(APIView):
    @manage_decorate(2)
    def get(self, request):
        try:
            tids = request.query_params['tids'].split(",")
            inttids = []
            for tid in tids:
                inttids.append(int(tid))
        except:
            return myResponse.Error("无法取得时间段")
        allAppointment = Appointment.objects.filter(slot_id__in=tids)
        return myResponse.OK(msg="获取成功", data=f_serializer.AppointmentDetailSerializers(allAppointment, many=True).data)

    @manage_decorate(3)
    def put(self, request):
        try:
            uuid = request.query_params['uuid']
            status = 2
        except:
            return myResponse.Error("字段不足")
        Appointment.objects.filter(uuid=uuid).update(status=status)
        return myResponse.OK("操作成功")


class myHandle(APIView):
    @login_decorate
    def get(self, request):
        allevent = event.objects.filter(handler__userName=request.session.get("username"))
        return myResponse.OK(data=f_serializer.shortEventSerializers(allevent, many=True).data)


class handleDetail(APIView):
    @login_decorate
    def get(self, request):
        try:
            eid = int(request.query_params['eid'])
            thisEvent = event.objects.get(id=eid)
        except:
            return myResponse.Error("后端异常")
        return myResponse.OK(data=f_serializer.EventSerializers(thisEvent).data)
