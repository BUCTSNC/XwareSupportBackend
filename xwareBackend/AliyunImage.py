import json
import oss2

AccessKeyID = ''
AccessKeySecret = ""

auth = oss2.Auth(AccessKeyID, AccessKeySecret)
bucket = oss2.Bucket(auth, 'https://oss-cn-beijing.aliyuncs.com', 'xwareimage')


def upload(data,name):
    headers = dict()
    headers["x-oss-storage-class"] = "Standard"
    headers["x-oss-object-acl"] = oss2.OBJECT_ACL_PRIVATE
    res = bucket.put_object(name, data)
    return res.status

