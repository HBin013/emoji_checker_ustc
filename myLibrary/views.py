import csv

from django.shortcuts import render, redirect
from django.http import HttpResponseRedirect, response, HttpResponse, JsonResponse
from django.contrib.auth.hashers import make_password, check_password  # 用户密码管理
from django.utils import timezone  # django带时区管理的时间类
from datetime import datetime
from django.shortcuts import get_object_or_404, render
from django.db import connection
from django.db.models import Count  # 计数函数
from django.views.decorators.csrf import csrf_exempt

from .models import *  # 引入数据库
import re
from decimal import Decimal
from django.db.models import Q


# 检查日期格式是否符合要求
def is_valid_date(date_string, format='%Y-%m-%d'):
    try:
        datetime.strptime(date_string, format)
        return True
    except ValueError:
        return False


def home(request):
    return render(request, 'home.html')


def login_view(request):  # 用户登录
    """
        登录
    """
    context = dict()
    if request.method == 'POST':
        context["username"] = username = request.POST.get("username")
        password = request.POST.get("password")
        if not username:
            context["msg"] = "请输入用户名"
            return render(request, 'home.html', context=context)
        if not password:
            context["msg"] = "不可输入空密码"
            return render(request, 'home.html', context=context)
        result = User.objects.filter(uname=username)
        if result.exists() and check_password(password, result[0].pwd):  # 登录成功
            request.session['login_type'] = result[0].role
            request.session['id'] = result[0].uid
            request.session['name'] = result[0].uname
            if result[0].role == 1:
                return redirect('admin_index')
            else:
                return redirect('user_index')
        elif not result.exists():
            context["msg"] = "用户不存在"
            return render(request, 'home.html', context=context)
        else:
            context["msg"] = "密码错误"
            return render(request, 'home.html', context=context)
    else:
        return render(request, 'home.html')


def register(request):  # 新用户注册账户
    """
        注册账号
    """
    context = dict()
    if request.method == 'GET':
        return render(request, 'register.html', context=context)
    elif request.method == 'POST':
        context["name"] = name = request.POST.get("name")  # 姓名
        context["phone_num"] = phone_num = request.POST.get("phone_num")  # 电话
        context["mail"] = mail = request.POST.get("mail")  # 邮箱
        context["role"] = role = request.POST.get("role")  # 身份
        pw = request.POST.get("pw")  # 密码
        pw_confirm = request.POST.get("pw_confirm")  # 密码确认
        context["msg"] = "未知错误，请重试"
        if not (name and phone_num and mail and pw and pw_confirm and role):
            context['msg'] = "姓名、电话、身份、邮箱和密码均不可为空"
            return render(request, 'register.html', context=context)
        if len(phone_num) != 11 or not phone_num.isdecimal():
            context["msg"] = "电话输入有误，请检查"
            return render(request, 'register.html', context=context)
        if pw != pw_confirm:
            context["msg"] = "两次密码输入不一致，请检查"
            return render(request, 'register.html', context=context)
        if len(pw) < 8 or len(pw) > 20:
            context["msg"] = "密码长度8-20位"
            return render(request, 'register.html', context=context)
        if '@' not in mail:
            context["msg"] = "邮箱格式错误，缺少@"
            return render(request, 'register.html', context=context)
        result = User.objects.filter(uname=name)
        if result.exists():
            context["msg"] = "用户名已经注册"
            return render(request, 'register.html', context=context)
        item = User(
            uname=name,
            mailAddr=mail,
            tel=phone_num,
            role=role,
            pwd=make_password(pw)
        )
        item.save()
        result = User.objects.get(uname=name)
        context["msg"] = "注册成功，系统自动为您分配账号，id为:" + str(result.uid)
        return render(request, 'home.html', context=context)
    else:
        return render(request, 'register.html', context=context)


def logout_view(request):  # 退出登录
    if request.session.get('login_type', None):
        request.session.flush()
    return HttpResponseRedirect("/")


def modifyPwd(request):  # 修改密码
    """
        修改密码
    """
    context = dict()
    uname = request.session.get("name")
    # tel = request.session.get("phone_num")
    # mailAddr = request.session.get("mailAddr")
    # role = request.session.get("role")
    context["name"] = uname
    # context["phone_num"] = tel
    # context["mail"] = mailAddr
    # context["role"] = role
    if request.method == 'GET':
        return render(request, 'modifyPwd.html', context=context)
    elif request.method == 'POST':
        pw_old = request.POST.get("pw_old")  # 旧密码
        pw = request.POST.get("pw")  # 密码
        pw_confirm = request.POST.get("pw_confirm")  # 密码确认
        context["msg"] = "未知错误，请重试"
        result = User.objects.filter(uname=uname)
        if not (pw_old and pw and pw_confirm):
            context['msg'] = "旧密码、新密码和确认密码均不可为空"
            return render(request, 'modifyPwd.html', context=context)
        if not check_password(pw_old, result[0].pwd):
            context['msg'] = "旧密码错误"
            return render(request, 'modifyPwd.html', context=context)
        if pw != pw_confirm:
            context["msg"] = "两次密码输入不一致，请检查"
            return render(request, 'modifyPwd.html', context=context)
        if len(pw) < 8 or len(pw) > 20:
            context["msg"] = "密码长度8-20位"
            return render(request, 'modifyPwd.html', context=context)
        result = User.objects.filter(uname=uname)
        if result[0].pwd == pw:
            context["msg"] = "新密码与旧密码相同"
            return render(request, 'modifyPwd.html', context=context)
        new_password = make_password(pw)
        user = User.objects.get(uname=uname)
        user.pwd = new_password
        user.save()
        request.session.flush()  # 修改密码后自动退出
        context["msg"] = "修改成功，请重新登录"
        return render(request, 'home.html', context=context)
        # return render(request, 'home.html', context=context)
    else:
        return render(request, 'modifyPwd.html', context=context)


"""
登录后的session:
request.session['login_type']: role
request.session['id']: uid
request.session['name']: uname
"""


def send_emoji(request):
    """
        发送emoji
    """
    context = dict()
    if request.method == 'GET':
        return render(request, 'send_emoji.html', context=context)
    elif request.method == 'POST':
        context["name"] = name = request.session.get("name")  # 姓名
        # context["phone_num"] = phone_num = request.POST.get("phone_num")  # 电话
        # context["mail"] = mail = request.POST.get("mail")  # 邮箱
        # context["role"] = role = request.POST.get("role")  # 身份
        ename = request.POST.get("ename")  # emoji名称
        context["msg"] = "未知错误，请重试"
        if not (ename):
            context['msg'] = "请选择emoji"
            return render(request, 'send_emoji.html', context=context)
        uid = User.objects.filter(uname=name)[0]
        emoji = Emoji(
            ename=ename,
            timeStamp=timezone.now(),
            uid=uid
        )
        emoji.save()
        context["msg"] = "发送成功"
        return render(request, 'send_emoji.html', context=context)
    else:
        return render(request, 'send_emoji.html', context=context)


# =====================emoji相关功能======================


def user_index(request):  # 用户首页
    temp = request.session.get('login_type', None)
    if temp != 0 and temp != 2 and temp != 3:
        return HttpResponseRedirect("/")
    context = dict()
    context['name'] = request.session.get('name')
    context['id'] = request.session.get('id')
    return render(request, 'user_index.html', context=context)


# 查询历史emoji
def emoji_history(request):
    """
        查询并返回符合条件的emoji
        给的emoji条件越多，则符合条件的emoji会越少
    """
    temp = request.session.get('login_type', None)
    if temp != 0 and temp != 2 and temp != 3:
        return HttpResponseRedirect("/")
    context = dict()
    context['name'] = uname = request.session.get('name', None)
    context['msg'] = "未知错误，请重试"
    uid = User.objects.filter(uname=uname)[0]
    result = Emoji.objects.all()
    # if ename:
    #     result = result.filter(ename__contains=ename)
    if uname:
        result = result.filter(uid=uid)
    # if cid:
    #     result = result.filter(cid=cid)
    emoji_history = []
    for elem in result:
        emoji_history.append(
            {
                'eid': elem.eid,
                'ename': elem.ename,
                'timeStamp': elem.timeStamp,
                'uid': elem.uid
                # 'cid': elem.cid
            }
        )
    context['msg'] = ''
    context['emoji_history'] = emoji_history
    return render(request, 'emoji_history.html', context=context)


# # =====================管理员======================
#
#
def admin_index(request):  # 管理员首页
    """
    """
    if request.session.get('login_type', None) != 1:
        return HttpResponseRedirect("/")
    context = dict()
    context['name'] = request.session.get('name')
    if request.method == 'GET':
        return render(request, 'admin_index.html', context=context)
    else:
        return render(request, 'admin_index.html', context=context)


def admin_takeoff(request):
    return None


def admin_query(request):
    """
    查看用户数据
    """
    if request.session.get('login_type', None) != 1:
        return HttpResponseRedirect("/")
    context = dict()
    context['name'] = request.session.get('name', None)
    context['msg'] = "未知错误，请重试"
    result = User.objects.all()

    user_list = []
    for elem in result:
        user_list.append(
            {
                'uid': elem.uid,
                'uname': elem.uname,
                'mailAddr': elem.mailAddr,
                'tel': elem.tel,
                'role': elem.role
            }
        )
    context['msg'] = ''
    context['user_list'] = user_list
    return render(request, 'admin_query.html', context=context)


def emoji_query(request):
    """
        查看emoji数据
    """
    if request.session.get('login_type', None) != 1:
        return HttpResponseRedirect("/")
    context = dict()
    context['name'] = request.session.get('name', None)
    context['msg'] = "未知错误，请重试"
    result = Emoji.objects.all()
    emoji_list = []
    for elem in result:
        emoji_list.append(
            {
                'eid': elem.eid,
                'ename': elem.ename,
                'timeStamp': elem.timeStamp,
                'uid': elem.uid.uid,
                'stu_name': elem.uid.uname
            }
        )
    context['msg'] = ''
    context['emoji_list'] = emoji_list
    return render(request, 'emoji_query.html', context=context)


def emoji_export(request):
    """
    导出emoji数据
    """
    # global char
    if request.session.get('login_type', None) != 1:
        return HttpResponseRedirect("/")
    context = dict()
    context['name'] = request.session.get('name', None)
    context['msg'] = "未知错误，请重试"
    result = Emoji.objects.all()
    emoji_list = []
    emoji_list.append(["emoji_id", "emoji名称", "发送时间", "用户id", "用户名"])
    for elem in result:
        # if elem.ename == "laugh":
        #     char = '😄'
        # elif elem.ename == "forced_smile":
        #     char = '😅'
        # elif elem.ename == "light_up_with_pleasure":
        #     char = '🥰'
        # elif elem.ename == "think":
        #     char = '🤔'
        # elif elem.ename == "indifference":
        #     char = '😐'
        # elif elem.ename == "sleepy":
        #     char = '😪'
        # elif elem.ename == "slightly_dissatisfied":
        #     char = '🙁'
        # elif elem.ename == "painful":
        #     char = '😣'
        # emoji不能正确编码/解码
        emoji_list.append([elem.eid, elem.ename, elem.timeStamp, elem.uid.uid, elem.uid.uname])
    context['msg'] = ''
    response = HttpResponse(content_type='text/csv; charset=gbk')
    response['Content-Disposition'] = 'attachment; filename="emoji_data.csv"'

    for row in emoji_list:
        encoded_row = [cell.encode('gbk') if isinstance(cell, str) else cell for cell in row]
    writer = csv.writer(response)
    for row in emoji_list:
        writer.writerow(row)

    return response


def emoji_statistic(request):
    """
            统计emoji数据
    """
    if request.session.get('login_type', None) != 1:
        return HttpResponseRedirect("/")
    context = dict()
    context['name'] = request.session.get('name', None)
    if request.method == 'GET':
        return render(request, 'emoji_statistic.html', context=context)
    context['msg'] = "未知错误，请重试"
    context['beginTime'] = beginTime = request.POST.get("beginTime")
    context['endTime'] = endTime = request.POST.get("endTime")
    if beginTime and endTime:
        if beginTime > endTime:
            context['msg'] = "开始时间不可晚于结束时间"
            return render(request, 'emoji_statistic.html', context=context)
        emoji_map = ["laugh", "forced_smile", "light_up_with_pleasure", "think", "indifference", "sleepy",
                     "slightly_dissatisfied", "painful"]
        emoji_count = {}
        emoji_num = []
        for emoji_name in emoji_map:
            count = Emoji.objects.filter(timeStamp__range=(beginTime, endTime), ename=emoji_name).count()
            emoji_count[emoji_name] = count
            emoji_num.append(count)
        context['msg'] = ''
        context['emoji_num'] = emoji_num
        context['emoji_count'] = emoji_count
        context['emoji_map'] = emoji_map
        result = Emoji.objects.all()
        emoji_list = []
        for elem in result:
            emoji_list.append(
                {
                    'eid': elem.eid,
                    'ename': elem.ename,
                    'timeStamp': elem.timeStamp,
                    'uid': elem.uid.uid,
                    'stu_name': elem.uid.uname
                }
            )
        context['emoji_list'] = emoji_list

    else:
        context['msg'] = "请选择开始时间和结束时间"
    return render(request, 'emoji_statistic.html', context=context)


def emoji_chart(request):
    """
        统计emoji数据
    """
    if request.session.get('login_type', None) != 1:
        return HttpResponseRedirect("/")
    context = dict()
    context['name'] = request.session.get('name', None)
    if request.method == 'GET':
        return render(request, 'emoji_statistic.html', context=context)
    context['msg'] = "未知错误，请重试"
    context['beginTime'] = beginTime = request.POST.get("beginTime")
    context['endTime'] = endTime = request.POST.get("endTime")
    if beginTime and endTime:
        if beginTime > endTime:
            context['msg'] = "开始时间不可晚于结束时间"
            return render(request, 'emoji_statistic.html', context=context)
        emoji_map = ["laugh", "forced_smile", "light_up_with_pleasure", "think", "indifference", "sleepy",
                     "slightly_dissatisfied", "painful"]
        emoji_count = []
        for i in range(len(emoji_map)):
            count = Emoji.objects.filter(timeStamp__range=(beginTime, endTime), ename=emoji_map[i]).count()
            emoji_count.append(count)
        context['msg'] = ''
        context['emoji_count'] = emoji_count
        context['emoji_map'] = emoji_map
        return JsonResponse({'emoji_chart_data': emoji_count})
    else:
        context['msg'] = "请选择开始时间和结束时间"
        return render(request, 'emoji_statistic.html', context=context)


# const data = {
#     lineChartData: {
#         labels: ["Label 1", "Label 2", "Label 3"],
#         datasets: [
#             {
#                 label: "Dataset 1",
#                 data: [10, 20, 30],
#             },
#         ],
#     },
#     pieChartData: {
#         labels: ["Category 1", "Category 2", "Category 3"],
#         datasets: [
#             {
#                 data: [40, 30, 30],
#                 backgroundColor: ["red", "green", "blue"],
#             },
#         ],
#     },
# };
def add_user(request):
    """
            添加用户
    """
    context = dict()
    if request.method == 'GET':
        return render(request, 'add_user.html', context=context)
    elif request.method == 'POST':
        context["name"] = name = request.POST.get("name")  # 姓名
        context["phone_num"] = phone_num = request.POST.get("phone_num")  # 电话
        context["mail"] = mail = request.POST.get("mail")  # 邮箱
        context["role"] = role = request.POST.get("role")  # 身份
        pw = request.POST.get("pw")  # 密码
        pw_confirm = request.POST.get("pw_confirm")  # 密码确认
        context["msg"] = "未知错误，请重试"
        if not (name and phone_num and mail and pw and pw_confirm and role):
            context['msg'] = "姓名、电话、身份、邮箱和密码均不可为空"
            return render(request, 'add_user.html', context=context)
        if len(phone_num) != 11 or not phone_num.isdecimal():
            context["msg"] = "电话输入有误，请检查"
            return render(request, 'add_user.html', context=context)
        if pw != pw_confirm:
            context["msg"] = "两次密码输入不一致，请检查"
            return render(request, 'add_user.html', context=context)
        if len(pw) < 8 or len(pw) > 20:
            context["msg"] = "密码长度8-20位"
            return render(request, 'add_user.html', context=context)
        if '@' not in mail:
            context["msg"] = "邮箱格式错误，缺少@"
            return render(request, 'add_user.html', context=context)
        result = User.objects.filter(uname=name)
        if result.exists():
            context["msg"] = "用户名已经存在"
            return render(request, 'add_user.html', context=context)
        item = User(
            uname=name,
            mailAddr=mail,
            tel=phone_num,
            role=role,
            pwd=make_password(pw)
        )
        item.save()
        result = User.objects.get(uname=name)
        context["msg"] = "添加成功，系统自动分配账号，id为:" + str(result.uid)
        return admin_query(request)
    else:
        return render(request, 'add_user.html', context=context)


def add(request):
    if request.session.get('login_type', None) != 1:
        return HttpResponseRedirect("/")
    context = dict()
    context['name'] = request.session.get('name')
    return render(request, 'add_user.html', context=context)


def modify_user(request):
    """
        修改用户信息
    """
    context = dict()
    if request.method == 'GET':
        return render(request, 'modify_user.html', context=context)
    elif request.method == 'POST':
        context["name"] = name = request.POST.get("name")  # 姓名
        context["phone_num"] = phone_num = request.POST.get("phone_num")  # 电话
        context["mail"] = mail = request.POST.get("mail")  # 邮箱
        context["role"] = role = request.POST.get("role")  # 身份
        context["self_flag"] = self_flag = request.POST.get("self_flag") # 是否是自己
        context["uid"] = request.POST.get("uid")
        pw = request.POST.get("pw")  # 密码
        pw_confirm = request.POST.get("pw_confirm")  # 密码确认
        context["msg"] = "未知错误，请重试"
        if not (name and phone_num and mail and pw and pw_confirm and role):
            context['msg'] = "姓名、电话、身份、邮箱和密码均不可为空"
            return render(request, 'modify_user.html', context=context)
        if len(phone_num) != 11 or not phone_num.isdecimal():
            context["msg"] = "电话输入有误，请检查"
            return render(request, 'modify_user.html', context=context)
        if pw != pw_confirm:
            context["msg"] = "两次密码输入不一致，请检查"
            return render(request, 'modify_user.html', context=context)
        if len(pw) < 8 or len(pw) > 20:
            context["msg"] = "密码长度8-20位"
            return render(request, 'modify_user.html', context=context)
        if '@' not in mail:
            context["msg"] = "邮箱格式错误，缺少@"
            return render(request, 'modify_user.html', context=context)
        result = User.objects.filter(uname=name)
        # if result.exists():
        #     context["msg"] = "用户名已经存在"
        #     return render(request, 'modify_user.html', context=context)
        uid = request.POST.get('uid')
        user = User.objects.get(uid=uid)
        user.uname = name
        user.mailAddr = mail
        user.tel = phone_num
        user.role = role
        user.pwd = make_password(pw)
        user.save()
        context["msg"] = "修改成功"
        return admin_query(request)
    else:
        return render(request, 'modify_user.html', context=context)


def modify(request):
    if request.session.get('login_type', None) != 1:
        return HttpResponseRedirect("/")
    context = dict()
    context['name'] = name = request.session.get('name')
    context['uid'] = request.POST.get("modify_uid")
    selected_name = request.POST.get("selected_name")
    selected_role = request.POST.get("selected_role")
    if selected_name == name and selected_role == 1 :
        context['self_flag'] = 1
    else:
        context['self_flag'] = 0
    return render(request, 'modify_user.html', context=context)


def delete_user(request):
    if request.session.get('login_type', None) != 1:
        return HttpResponseRedirect("/")
    context = dict()
    context['name'] = name = request.session.get('name')
    context['uid'] = uid = request.POST.get("delete_uid")
    delete_name = request.POST.get("delete_name")
    delete_role = request.POST.get("delete_role")
    if delete_name == name:
        context['msg'] = "不可以删除自己"
        return admin_query(request)
    else:
        user = User.objects.get(uid=uid)
        user.delete()
    return admin_query(request)

def user_emoji(request):
    if request.session.get('login_type', None) != 1:
        return HttpResponseRedirect("/")
    context = dict()
    context['name'] = name = request.session.get('name')
    context['uid'] = uid = request.POST.get("user_uid")
    user_name = request.POST.get("user_name")
    result = Emoji.objects.all()
    # if ename:
    #     result = result.filter(ename__contains=ename)
    if user_name:
        result = result.filter(uid=uid)
    # if cid:
    #     result = result.filter(cid=cid)
    emoji_history = []
    for elem in result:
        emoji_history.append(
            {
                'eid': elem.eid,
                'ename': elem.ename,
                'timeStamp': elem.timeStamp,
                'uid': elem.uid
                # 'cid': elem.cid
            }
        )
    context['msg'] = ''
    context['emoji_history'] = emoji_history
    return render(request, 'user_emoji.html', context=context)