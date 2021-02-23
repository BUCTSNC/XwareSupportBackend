from django.db import models


# Create your models here.
class TimeSlot(models.Model):
    Date = models.DateField(blank=False)
    Start = models.DateTimeField(blank=False)
    Slot = models.DurationField(blank=False)
    AllowNumber = models.IntegerField(blank=False)

    def __str__(self):
        return str(self.id)+":"+str(self.Start)+"-"+(self.Start+self.Slot)


class user(models.Model):
    openid = models.CharField(blank=False,max_length=500)
    username = models.CharField(max_length=500)
    stuNO = models.CharField(max_length=500)
    phone = models.CharField(max_length=500)


class Appointment(models.Model):
    uuid = models.CharField(max_length=100)
    user = models.ForeignKey(user,on_delete=models.DO_NOTHING)
    slot = models.ForeignKey(TimeSlot,on_delete=models.CASCADE)
    type = models.CharField(max_length=200)
    describe = models.TextField()


class functionary(models.Model):
    Owner = 5
    Admin = 4
    Leader = 3
    Member = 2
    Retire = 1
    user = models.OneToOneField(user,on_delete=models.CASCADE)
    userName = models.CharField(max_length=50)
    passWord = models.CharField(max_length=500)
    realName = models.CharField(max_length=100)
    auth = models.IntegerField(default=Member)


class event(models.Model):
    appointment = models.ForeignKey(Appointment,on_delete=models.DO_NOTHING)
    handler = models.ForeignKey(functionary,on_delete=models.DO_NOTHING)
    status = models.CharField(max_length=200)
    result = models.CharField(max_length=200)
    handleTime = models.DateTimeField()
