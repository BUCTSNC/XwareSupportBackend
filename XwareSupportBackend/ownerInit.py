import hashlib
from xwareBackend.models import functionary
import json


def passwordSalt(sourcePassword):
    salt = hashlib.md5(sourcePassword.encode("utf-8")).hexdigest()
    saltPassword = salt + sourcePassword
    finalPassword = hashlib.sha256(saltPassword.encode("utf-8")).hexdigest()
    return finalPassword


def init():
    setting = json.load(open("ownerSetting.json", "r", encoding="utf-8"))
    if "ownerName" in setting \
            and "ownerPassword" in setting \
            and setting['ownerName'] != '' \
            and setting['ownerPassword'] != "":
        owner = functionary.objects.filter(auth=5)
        saltPassword = passwordSalt(setting['ownerPassword'])
        if owner.count() == 0:
            functionary(
                userName=setting['ownerName'],
                passWord=saltPassword,
                auth=5
            ).save()
        elif owner.count() == 1:
            owner.update(
                userName=setting['ownerName'],
                passWord=saltPassword
            )
        elif owner.count() > 1:
            owner.delete()
            functionary(
                userName=setting['ownerName'],
                passWord=saltPassword,
                auth=5
            ).save()
    else:
        print("owner初始化失败")
