from rest_framework.serializers import ModelSerializer, Serializer
from rest_framework import serializers
from xwareBackend.models import *
import json


class UserSerializers(ModelSerializer):
    class Meta:
        model = user
        fields = "__all__"

    functionaryInfo = serializers.SerializerMethodField()

    def get_functionaryInfo(self, data):
        if functionary.objects.filter(user_id=data.id).count() == 0:
            return False
        else:
            return FunctionarySerializers(functionary.objects.filter(user_id=data.id)[0], many=False).data


class FunctionarySerializers(ModelSerializer):
    class Meta:
        model = functionary
        exclude = ['user', "passWord"]


class mainProblemSerializers(ModelSerializer):
    class Meta:
        model = mainProblemType
        fields = ['id', 'type', 'subs', "message"]

    subs = serializers.SerializerMethodField()

    def get_subs(self, data):
        ret = []
        allsub = subProblemType.objects.filter(mainType_id=data.id)
        for sub in allsub:
            ret.append(sub.type)
        return ret


class subProblemSerializers(ModelSerializer):
    class Meta:
        model = subProblemType
        fields = ['type']


class timeSlotSerializers(ModelSerializer):
    class Meta:
        model = TimeSlot
        fields = ["id", 'date', 'slot']

    date = serializers.SerializerMethodField()
    slot = serializers.SerializerMethodField()

    def get_date(self, data):
        return data.Date.strftime("%Y-%m-%d") + " " + "({})".format(numberToWeekDay(data.Date.strftime("%w")))

    def get_slot(self, data):
        return str(data.Start.strftime("%H:%M:%S")) + "-" + data.End.strftime("%H:%M:%S")


class shortAppointmentSerializers(ModelSerializer):
    class Meta:
        model = Appointment
        fields = ['id', 'problemType', 'status', "date", "slot", "applyTime"]

    date = serializers.SerializerMethodField()
    slot = serializers.SerializerMethodField()
    applyTime = serializers.SerializerMethodField()

    def get_date(self, data):
        time = TimeSlot.objects.filter(id=data.slot.id)
        return time[0].Date.strftime("%Y-%m-%d") + " " + "({})".format(numberToWeekDay(time[0].Date.strftime("%w")))

    def get_slot(self, data):
        time = TimeSlot.objects.filter(id=data.slot.id)
        return str(time[0].Start.strftime("%H:%M:%S")) + "-" + time[0].End.strftime("%H:%M:%S")

    def get_applyTime(self, data):
        return data.applyTime.strftime("%Y-%m-%d %H:%M:%S")


class AppointmentDetailSerializers(ModelSerializer):
    class Meta:
        model = Appointment
        fields = ['uuid', 'describe', "meta", "user"]

    meta = serializers.SerializerMethodField()
    user = serializers.SerializerMethodField()

    def get_meta(self, data):
        return shortAppointmentSerializers(data).data

    def get_user(self, data):
        return data.sourseInfo


class shortEventSerializers(ModelSerializer):
    class Meta:
        model = event
        fields = ['id', 'status', 'appointment', 'user', "uuid", "handletime"]

    appointment = serializers.SerializerMethodField()
    user = serializers.SerializerMethodField()
    uuid = serializers.SerializerMethodField()
    handletime = serializers.SerializerMethodField()

    def get_appointment(self, data):
        return shortAppointmentSerializers(data.appointment).data

    def get_user(self, data):
        return data.appointment.sourseInfo

    def get_uuid(self, data):
        return data.appointment.uuid

    def get_handletime(self, data):
        return data.handleTime.strftime("%Y-%m-%d %H:%M:%S")


class EventSerializers(ModelSerializer):
    class Meta:
        model = event
        exclude = ['appointment', 'handler']

    Appointment = serializers.SerializerMethodField()
    Handler = serializers.SerializerMethodField()
    attachImage = serializers.SerializerMethodField()

    def get_Appointment(self, data):
        return AppointmentDetailSerializers(data.appointment).data

    def get_Handler(self, data):
        return FunctionarySerializers(data.handler).data

    def get_attachImage(self, data):
        return imageSerializers(eventImage.objects.filter(event_id=data.id,type="attach"),many=True).data
class imageSerializers(ModelSerializer):
    class Meta:
        model = eventImage
        fields = "__all__"

def numberToWeekDay(num):
    dic = {
        "1": "星期一",
        "2": "星期二",
        "3": "星期三",
        "4": "星期四",
        "5": "星期五",
        "6": "星期六",
        "7": "星期日",
    }
    return dic[num]
