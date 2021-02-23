from django.shortcuts import render
from django.http import HttpResponse
import json
# Create your views here.


def hello(request):
    res = {"code":200,"msg":"hello"}
    return HttpResponse(json.dumps(res),content_type="text/json")