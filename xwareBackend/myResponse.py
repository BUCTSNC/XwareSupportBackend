from rest_framework.response import Response


def Error(msg=None):
    res = {"code": 404}
    if msg:
        res['msg'] = msg
    return Response(res)


def OK(msg=None, data=None):
    res = {
        "code": 200
    }
    if msg:
        res['msg'] = msg
    if data:
        res['data'] = data
    return Response(res)


def AuthError(msg=None):
    res = {"code": 401}
    if msg:
        res['msg'] = msg
    return Response(res)


