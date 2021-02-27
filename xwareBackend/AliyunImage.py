import json
import oss2

AccessKeyID = 'LTAI4G2VUPSM4oDteMZd1mhK'
AccessKeySecret = "2Y3Ii6lXbbs5GIL9niT4UpuW6EG5Mw"
auth = oss2.Auth(AccessKeyID, AccessKeySecret)
bucket = oss2.Bucket(auth, 'https://oss-cn-beijing.aliyuncs.com', 'xwareimage')


def upload(data):
    headers = dict()
    headers["x-oss-storage-class"] = "Standard"
    headers["x-oss-object-acl"] = oss2.OBJECT_ACL_PRIVATE
    res = bucket.put_object('testImage.png', data)
    return res.status

