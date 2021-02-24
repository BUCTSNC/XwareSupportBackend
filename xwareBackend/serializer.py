from rest_framework.serializers import ModelSerializer, Serializer
from rest_framework import serializers
from xwareBackend.models import *


class UserSerializers(ModelSerializer):
    class Meta:
        model = user
        fields = "__all__"

    functionaryInfo = serializers.SerializerMethodField

    def get_functionaryInfo(self, data):
        if functionary.objects.filter(user_id=data.id).count() == 0:
            return False
        else:
            return FunctionarySerializers(functionary.objects.filter(user_id=data.id)[0], many=False).data


class FunctionarySerializers(ModelSerializer):
    class Meta:
        model = functionary
        exclude = ['user', "passWord"]
