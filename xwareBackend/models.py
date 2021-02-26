from django.db import models


# Create your models here.
class TimeSlot(models.Model):
    Date = models.DateField(blank=False)
    Start = models.DateTimeField(blank=False)
    End = models.DateTimeField(blank=True,null=True)
    AllowNumber = models.IntegerField(blank=False)

    def __str__(self):
        return str(self.id) + "-" +self.Date.strftime("%Y-%m-%d %w") + " " +str(self.Start.strftime("%H:%M:%S")) + "-" + (self.End).strftime("%H:%M:%S")


class user(models.Model):
    openid = models.CharField(blank=False, max_length=500)
    username = models.CharField(max_length=500)
    realName = models.CharField(max_length=100,default="")
    NO = models.CharField(max_length=500)
    phone = models.CharField(max_length=500)


class Appointment(models.Model):
    uuid = models.CharField(max_length=100)
    user = models.ForeignKey(user, on_delete=models.DO_NOTHING)
    sourseInfo = models.JSONField(null=True)
    slot = models.ForeignKey(TimeSlot, on_delete=models.CASCADE)
    problemType = models.CharField(max_length=200,default="")
    describe = models.TextField()
    applyTime = models.DateTimeField(auto_now_add=True,null=True)
    status = models.IntegerField(default=1)
    """
    0:正在预约
    1:预约成功
    2:签到成功
    3:正在维修
    4:维修完成
    5:预约失效
    6:未通过预约
    """


Owner = 5
Admin = 4
Leader = 3
Member = 2
Retire = 1


class functionary(models.Model):
    user = models.OneToOneField(user, on_delete=models.CASCADE, null=True)
    userName = models.CharField(max_length=50)
    passWord = models.CharField(max_length=500)
    realName = models.CharField(max_length=100)
    auth = models.IntegerField(default=Member)


class event(models.Model):
    appointment = models.ForeignKey(Appointment, on_delete=models.DO_NOTHING)
    handler = models.ForeignKey(functionary, on_delete=models.DO_NOTHING)
    status = models.CharField(max_length=200)
    detectProblemType = models.CharField(default="",max_length=200)
    detectInfo = models.TextField(default="")
    handleWay = models.TextField(default="")
    finalStatus = models.TextField(default="")
    result = models.CharField(max_length=200)
    handleTime = models.DateTimeField(auto_now=True)


class mainProblemType(models.Model):
    type = models.CharField(max_length=200,default="")
    message = models.TextField(default="")

    def __str__(self):
        return self.type


class subProblemType(models.Model):
    type = models.CharField(max_length=200,default="")
    mainType = models.ForeignKey(mainProblemType,on_delete=models.CASCADE)

    def __str__(self):
        return self.mainType.type + "-" + self.type
