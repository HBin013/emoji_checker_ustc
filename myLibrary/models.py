from django.db import models


# DAO类的集合

# 用户
class User(models.Model):
    uid = models.AutoField(primary_key=True)
    uname = models.CharField(max_length=15)
    mailAddr = models.CharField(max_length=30, null=True, blank=True)
    tel = models.CharField(max_length=20, null=True, blank=True)
    role = models.IntegerField(choices=(
        (0, 'visitor'),
        (1, 'admin'),
        (2, 'teacher'),
        (3, 'student')
    ))
    pwd = models.CharField(max_length=128)


class Course(models.Model):
    cid = models.IntegerField(primary_key=True)
    cname = models.CharField(max_length=15)
    tid = models.ForeignKey(User, on_delete=models.CASCADE)
    beginTime = models.DateTimeField()
    endTime = models.DateTimeField()


class Emoji(models.Model):
    eid = models.AutoField(primary_key=True)
    ename = models.CharField(max_length=15)
    timeStamp = models.DateTimeField()
    uid = models.ForeignKey(User, on_delete=models.CASCADE)
    # cid = models.ForeignKey(Course, on_delete=models.CASCADE)


# class Sc(models.Model):
#     uid = models.ForeignKey(User, on_delete=models.CASCADE, primary_key=True)
#     cid = models.ForeignKey(Course, on_delete=models.CASCADE, primary_key=True)
