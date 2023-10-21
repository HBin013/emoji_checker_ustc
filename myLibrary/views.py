from django.shortcuts import render, redirect
from django.http import HttpResponseRedirect
from django.contrib.auth.hashers import make_password, check_password  # 用户密码管理
from django.utils import timezone  # django带时区管理的时间类
from datetime import datetime
from django.shortcuts import get_object_or_404, render
from django.db import connection
from django.db.models import Count  # 计数函数
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
        if result.exists() and check_password(password, result[0].pwd): # 登录成功
            request.session['login_type'] = result[0].role
            request.session['id'] = result[0].uid
            request.session['name'] = result[0].uname
            if result[0].role == 1:
                return redirect('admin_index')
            else:
                return redirect('user_index')
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
        context["msg"] = "注册成功，系统自动为您分配账号，id为：" + str(result.reader_id)
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
        pw = request.POST.get("pw")  # 密码
        pw_confirm = request.POST.get("pw_confirm")  # 密码确认
        context["msg"] = "未知错误，请重试"
        if not (pw and pw_confirm):
            context['msg'] = "密码和确认密码均不可为空"
            return render(request, 'modifyPwd.html', context=context)
        if pw != pw_confirm:
            context["msg"] = "两次密码输入不一致，请检查"
            return render(request, 'modifyPwd.html', context=context)
        if len(pw) < 8 or len(pw) > 20:
            context["msg"] = "密码长度8-20位"
            return render(request, 'modifyPwd.html', context=context)
        result = User.objects.filter(uname=uname)
        if result[0].pwd == pw:
            context["msg"] = "新密码与旧密码啊相同"
            return render(request, 'modifyPwd.html', context=context)
        User.objects.filter(uname=uname).update(pwd=pw)
        context["msg"] = "修改成功"
        logout_view(request) # 修改密码后自动退出
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
        context["name"] = name = request.POST.get("name")  # 姓名
        # context["phone_num"] = phone_num = request.POST.get("phone_num")  # 电话
        # context["mail"] = mail = request.POST.get("mail")  # 邮箱
        # context["role"] = role = request.POST.get("role")  # 身份
        ename = request.POST.get("ename")  # emoji名称
        context["msg"] = "未知错误，请重试"
        if not (ename):
            context['msg'] = "请选择emoji"
            return render(request, 'send_emoji.html', context=context)
        uid = User.objects.filter(uname=name)[0].uid
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
    if temp != '0' and temp != '2' and temp != '3':
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
    if temp != '0' and temp != '2' and temp != '3':
        return HttpResponseRedirect("/")
    context = dict()
    context['name'] = uname = request.session.get('name', None)
    if request.method == 'GET':
        return render(request, 'emoji_history.html', context=context)
    else:
        # context['ename'] = ename = request.POST.get('ename')  # emoji名称
        # context['cid'] = cid = request.POST.get('cid')  # 课程
        context['msg'] = "未知错误，请重试"
        result = Emoji.objects.all()
        # if ename:
        #     result = result.filter(ename__contains=ename)
        if uname:
            result = result.filter(uname=uname)
        # if cid:
        #     result = result.filter(cid=cid)
        emoji_history = []
        for elem in result:
            emoji_history.append(
                {
                    'eid': elem.eid,
                    'ename': elem.ename,
                    'timeStamp': elem.timeStamp,
                    'uid': elem.uid,
                    'cid': elem.cid
                }
            )
        context['msg'] = ''
        context['emoji_history'] = emoji_history
        return render(request, 'emoji_history.html', context=context)


# 读者预约登记



def reader_recommend(request):
    """
        读者荐购
        只需要填写ISBN即可
        对于某一个ISBN号只可以申请荐购一次
    """
    if request.session.get('login_type', None) != 'identity_reader':
        return HttpResponseRedirect("/")
    context = dict()
    context['name'] = request.session.get('name')
    if request.method == 'GET':
        return render(request, 'reader_recommend.html', context=context)
    else:
        context['isbn'] = isbn = request.POST.get('isbn')  # ISBN
        context['upload_num'] = upload_num = request.POST.get('upload_num')  # 入库数量
        if not isbn or not upload_num:
            context['msg'] = "请填写ISBN号、入库数量"
            return render(request, 'reader_recommend.html', context=context)
        result = recommend_table.objects.filter(isbn=isbn, reader_id_id=request.session.get('id'))
        if (result):
            context['msg'] = "该读者对该isbn号的图书已经有过荐购请求，请勿重复请求"
            return render(request, 'reader_recommend.html', context=context)

            #result = recommend_table.objects.filter(isbn=isbn)
        else:
            result = book_table.objects.filter(isbn=isbn)
            if(result):
                context['msg'] = "该isbn号的图书已经有馆藏，不可荐购"
                return render(request, 'reader_recommend.html', context=context)
            else:
                result = recommend_table.objects.filter(isbn=isbn)
                if (result):
                    context['msg'] = "其他人已经荐购过该书，不可重复荐购"
                    return render(request, 'reader_recommend.html', context=context)
        # 其他人荐购过的isbn号不可荐购

        ##添加荐购信息
        item = recommend_table(
            isbn=isbn,
            book_num=upload_num,
            reader_id_id=request.session.get('id'),
            status='未处理'
        )
        item.save()
        context['msg'] = "成功荐购"
        return render(request, 'reader_recommend.html', context=context)


# =====================管理员======================


def admin_index(request):  # 管理员首页
    """
        显示当前日期的预约信息，以便处理读者借阅
        清除过期的预约信息 预约借书过期则此前预约无效，从预约表中删去 因为借书时只有当天的预约信息有效
        显示逾期归还信息
        显示待处理荐购信息
    """
    if request.session.get('login_type', None) != 'identity_admin':
        return HttpResponseRedirect("/")
    context = dict()
    context['name'] = request.session.get('name')
    if request.method == 'GET':
        return render(request, 'admin_index.html', context=context)
    else:

        today = timezone.now().date()
        reservations = reservation_table.objects.filter(take_date=today)
        context['existing_reservation'] = reservations
        # 处理过期预约信息
        result = reservation_table.objects.extra(where=["""datediff(curdate(), take_date) > 2"""])
        context['msg1'] = "清理" + str(len(result)) + "份过期预约信息。"
        for elem in result:#book_table中对应书本的状态改成未借出
            result_book = book_table.objects.get(book_id=elem.book_id_id)
            result_book.status = '未借出'
            result_book.save()
        result.delete()
        # 查询未归还图书记录
        result = borrow_table.objects.filter(return_date=None).extra(where=["""datediff(curdate(), due_date) = 0"""])
        context['msg2'] = "提示：当前有" + str(len(result)) + "份逾期归还图书。"
        # 查询未处理荐购记录
        unhandled_records = recommend_table.objects.filter(status='未处理')
        context['msg3'] = "提示：当前有" + str(len(unhandled_records)) + "份未处理荐购记录。"
        return render(request, 'admin_index.html', context=context)


def admin_query(request):  # 管理员书目状态查询
    """
        查询book_table返回书目状态
    """
    if request.session.get('login_type', None) != 'identity_admin':
        return HttpResponseRedirect("/")
    context = dict()
    context['name'] = request.session.get('name', None)
    if request.method == 'GET':
        return render(request, 'emoji_query.html', context=context)
    else:
        context['book_name'] = book_name = request.POST.get('book_name')  # 书名
        context['author'] = author = request.POST.get('author')  # 作者
        context['isbn'] = isbn = request.POST.get('isbn')  # ISBN
        context['publisher'] = publisher = request.POST.get('publisher')  # 出版社
        context['msg'] = "未知错误，请重试"
        result = booklist_table.objects.all()
        if book_name:
            result = result.filter(book_name__contains=book_name)
        if author:
            result = result.filter(author__contains=author)
        if isbn:
            result = result.filter(isbn__startswith=isbn)
        if publisher:
            result = result.filter(publisher__contains=publisher)
        book_message = []
        for elem in result:
            book_message.append(
                {
                    'ISBN': elem.isbn,
                    'book_name': elem.book_name,
                    'author': elem.author,
                    'publisher': elem.publisher,
                    'publish_date': elem.publish_date,
                    'num_inlib': len(book_table.objects.filter(isbn=elem.isbn)),
                    'num_forbid_borrow': len(book_table.objects.filter(isbn=elem.isbn, status='不外借')),
                    'num_not_borrow': len(book_table.objects.filter(isbn=elem.isbn, status='未借出')),
                    'num_have_borrow': len(book_table.objects.filter(isbn=elem.isbn, status='已借出')),
                    'num_have_reserve': len(book_table.objects.filter(isbn=elem.isbn, status='已预约')),
                    'image': elem.image
                }
            )
        context['msg'] = ''
        context['book_status'] = book_message
        return render(request, 'emoji_query.html', context=context)


# def send_emoji(request):  # 管理员借书
#     """
#         分为两种情况
#         1.来借阅之前预约过的图书，注意curdate()必须和之前预约的取书日期一致才可以借书
#         2.未预约直接借书，只可以借阅状态为未借出的书籍 如果此时这个书籍有当天有预约：
#             那么该书籍对于没有预约的人群来说：可借阅数量 =书库藏中可借阅数量-预约数量，如果可借阅数量为0，则无法为没有借阅的人群借书
#     """
#     if request.session.get('login_type', None) != 'identity_admin':
#         return HttpResponseRedirect("/")
#     context = dict()
#     context['name'] = request.session.get('name')
#     if request.method == 'GET':
#         return render(request, 'send_emoji.html', context=context)
#     else:
#         context['reader_id'] = reader_id = request.POST.get('reader_id')
#         context['isbn'] = isbn = request.POST.get('isbn')
#         context['msg'] = "未知错误，请重试"
#         if not reader_id or not isbn:
#             context['msg'] = "请填写完整的读者id和ISBN号"
#             return render(request, 'send_emoji.html', context=context)
#         if not reader_id.isdecimal():
#             context['msg'] = "读者id不存在！"
#             return render(request, 'send_emoji.html', context=context)
#         result = reader_table.objects.filter(reader_id=reader_id)
#         if not result.exists():
#             context['msg'] = "读者id不存在！"
#             return render(request, 'send_emoji.html', context=context)
#         result = booklist_table.objects.filter(isbn=isbn)
#         if not result.exists():
#             context['msg'] = "ISBN号填写错误，不存在该类书籍！"
#             return render(request, 'send_emoji.html', context=context)
#         result = borrow_table.objects.filter(reader_id_id=reader_id, return_date=None)
#         if len(result) >= 10:
#             context['msg'] = "该读者借阅书籍数已经达到上限！"
#             return render(request, 'send_emoji.html', context=context)
#         # 查询预约表，为读者处理预约表
#         reservation_book = reservation_table.objects.filter \
#             (reader_id_id=reader_id, take_date=timezone.now().date(), reservation_status='未处理')
#         result = None
#         for elem in reservation_book:
#             book_id = elem.book_id.book_id
#             book = book_table.objects.filter(book_id=book_id)
#             book_isbn = book[0].isbn_id
#             if (book_isbn == isbn):
#                 result = elem
#         if result:  # 借书有过预约，且预约成功（修改预约、添加借书信息、修改图书状态）
#             book_id = result.book_id_id
#             book = book_table.objects.filter(book_id=book_id)
#             book = book[0]  ##之前已经预约的图书
#             book.status = '已借出'
#             book.save()  # 修改图书状态
#             item = borrow_table(
#                 reader_id_id=reader_id,
#                 book_id=book,
#                 borrowing_time=timezone.now(),
#                 due_date=timezone.now() + timezone.timedelta(days=60)
#             )
#             item.save()  # 添加借书信息
#             result.reservation_status = '已处理'
#             result.save()  # 修改预约信息
#             context['msg'] = "借阅成功（已预约）！（图书id：" + str(item.book_id.book_id) + "）"
#             return render(request, 'send_emoji.html', context=context)
#         else:  # 未预约直接借书（添加借书信息、修改图书状态）
#             # 注意：此时读者不可以借阅id号在预约表中的图书，即状态为已预约的图书
#             result = book_table.objects.filter(isbn_id=isbn, status='未借出')
#             if not result.exists():
#                 context['msg'] = "该图书已全部被借出或预约，无法借阅！"
#                 return render(request, 'send_emoji.html', context=context)
#             result = result[0]
#             result.status = '已借出'
#             result.save()  # 修改图书状态
#             item = borrow_table(
#                 reader_id_id=reader_id,
#                 book_id=result,
#                 borrowing_time=timezone.now(),
#                 due_date=timezone.now() + timezone.timedelta(days=60)
#             )
#             item.save()  # 添加借书信息
#             context['msg'] = "借阅成功（未预约）！（图书id：" + str(result.book_id) + "）"
#             return render(request, 'send_emoji.html', context=context)


def admin_return(request):  # 管理员还书
    """
            分为两种情况
            1.逾期归还，则此时读者违约费用对应增多
            2.未按期归还
            无论怎样都需要更新book的状态
    """
    if request.session.get('login_type', None) != 'identity_admin':
        return HttpResponseRedirect("/")
    context = dict()
    context['name'] = request.session.get('name')
    if request.method == 'GET':
        return render(request, 'admin_return.html', context=context)
    else:
        context['reader_id'] = reader_id = request.POST.get('reader_id')
        context['book_id'] = book_id = request.POST.get('book_id')
        context['msg'] = "未知错误，请重试"
        if not reader_id or not book_id:
            context['msg'] = "请填写完整的读者id和ISBN号"
            return render(request, 'admin_return.html', context=context)
        if not reader_id.isdecimal() or not book_id.isdecimal():
            context['msg'] = "读者id和图书id必须是数字！"
            return render(request, 'admin_return.html', context=context)
        result = reader_table.objects.filter(reader_id=reader_id)
        if not result.exists():
            context['msg'] = "读者id不存在！"
            return render(request, 'admin_return.html', context=context)
        result = book_table.objects.filter(book_id=book_id)
        if not result.exists():
            context['msg'] = "不存在该图书id！"
            return render(request, 'admin_return.html', context=context)
        result = borrow_table.objects.filter(reader_id_id=reader_id, book_id_id=book_id, return_date=None)  # 未归还的借书记录
        if not result.exists():
            context['msg'] = "该读者未借阅该图书！"
            return render(request, 'admin_return.html', context=context)
        return_book = result[0]

        if timezone.now() - return_book.due_date > timezone.timedelta(days=0):  # 逾期未还
            reader = reader_table.objects.get(reader_id=reader_id)
            time_diff_day = (timezone.now() - return_book.due_date).days
            reader.arrears = reader.arrears + Decimal(time_diff_day * 0.1 ) # 逾期一天缴纳1元
            reader.admin_return_save()
            context['msg'] = "图书逾期归还，应该缴纳费用" + str((timezone.now() - return_book.due_date).days * 0.1) + "元"
        else:  # 期限内归还
            context['msg'] = "图书期限内归还"
        # 修改图书表状态
        book = book_table.objects.get(book_id=book_id)
        book.status = '未借出'
        book.save()
        # result.return_date = timezone.now()  # 归还此书
        # result.save()
        return_book.return_date = timezone.now()  # 归还此书
        return_book.save()
        return render(request, 'admin_return.html', context=context)


def admin_upload(request):  # 管理员入库
    """
        旧书入库时，对应信息要和之前的信息保持一致
        新书入库时，必须填写book_name等信息
    """
    if request.session.get('login_type', None) != 'identity_admin':
        return HttpResponseRedirect("/")
    context = dict()
    context['name'] = request.session.get('name')
    if request.method == 'GET':
        return render(request, 'admin_upload.html', context=context)
    else:
        context['isbn'] = isbn = request.POST.get('isbn')  # ISBN
        context['upload_num'] = upload_num = request.POST.get('upload_num')  # 入库数量
        context['upload_place'] = upload_place = request.POST.get('upload_place')  # 入库后状态（流通室、阅览室）
        context['book_name'] = book_name = request.POST.get('book_name')  # 书名（新书录入）
        context['author'] = author = request.POST.get('author')  # 作者（新书录入）
        context['publisher'] = publisher = request.POST.get('publisher')  # 出版社（新书录入）
        context['publish_date'] = publish_date = request.POST.get('publish_date')  # 出版年月（新书录入）
        context['image_file'] = image_file = request.FILES.get('image_file')
        context['pdf_file'] = pdf_file = request.FILES.get('pdf_file')  # 图书pdf
        context['vedio_file'] = vedio_file = request.FILES.get('vedio_file')  # 图书视频

        context['msg'] = "未知错误，请重试"
        if (publish_date):
            if (not is_valid_date(publish_date)):
                context['msg'] = "请检查日期格式是否符合要求"
                return render(request, 'admin_upload.html', context=context)
        if not isbn or not upload_num or not upload_place:
            context['msg'] = "请填写ISBN号、入库数量和入库后状态"
            return render(request, 'admin_upload.html', context=context)
        if upload_place != '流通室' and upload_place != '阅览室':
            context['msg'] = "入库后状态必须为流通室或阅览室"
            return render(request, 'admin_upload.html', context=context)
        result = booklist_table.objects.filter(isbn=isbn)
        if result.exists():  # 旧书录入
            if book_name:
                result = result.filter(book_name__contains=book_name)
                if not result.exists():
                    context['msg'] = "检测到旧书录入，且书名信息不匹配，请检查"
                    return render(request, 'admin_upload.html', context=context)
            if author:
                result = result.filter(author__contains=author)
                if not result.exists():
                    context['msg'] = "检测到旧书录入，且作者信息不匹配，请检查"
                    return render(request, 'admin_upload.html', context=context)
            if publisher:
                result = result.filter(publisher__contains=publisher)
                if not result.exists():
                    context['msg'] = "检测到旧书录入，且出版社信息不匹配，请检查"
                    return render(request, 'admin_upload.html', context=context)
            if publish_date:
                result = result.filter(publish_date=publish_date)
                if not result.exists():
                    context['msg'] = "检测到旧书录入，且出版年月不匹配，请检查"
                    return render(request, 'admin_upload.html', context=context)
            if upload_place == '流通室':
                for _ in range(int(upload_num)):
                    item = book_table(
                        isbn_id=isbn,
                        storage_location='图书流通室',
                        status='未借出',
                        operator_id=request.session.get('id')
                    )
                    item.save()
            else:  # 阅览室不外借
                for _ in range(int(upload_num)):
                    item = book_table(
                        isbn_id=result[0].isbn,
                        storage_location='图书阅览室',
                        status='不外借',
                        operator_id=request.session.get('id')
                    )
                    item.save()
            data = booklist_table.objects.get(isbn=isbn)
            data.operator_id = request.session.get('id')
            if (image_file):
                data.image = image_file
            if (vedio_file):
                data.vedio = vedio_file
            if (pdf_file):
                data.pdf = pdf_file
            data.save()
            context['msg'] = "旧书入库成功！"
        else:  # 新书录入
            if not (book_name and author and publisher and publish_date):
                context['msg'] = "检测到新书录入，请完整填写信息"
                return render(request, 'admin_upload.html', context=context)
            item = booklist_table(
                isbn=isbn,
                book_name=book_name,
                author=author,
                publisher=publisher,
                publish_date=publish_date,
                operator_id=request.session.get('id'),
                image=image_file,
                vedio=vedio_file,
                pdf=pdf_file,
            )
            item.save()
            if upload_place == '流通室':
                for _ in range(int(upload_num)):
                    item = book_table(
                        isbn_id=isbn,
                        storage_location='图书流通室',
                        status='未借出',
                        operator_id=request.session.get('id')
                    )
                    item.save()
            else:  # 阅览室不外借
                for _ in range(int(upload_num)):
                    item = book_table(
                        isbn_id=isbn,
                        storage_location='图书阅览室',
                        status='不外借',
                        operator_id=request.session.get('id')
                    )
                    item.save()
            context['msg'] = "新书入库成功！"
        return render(request, 'admin_upload.html', context=context)


def admin_takeoff(request):  # 管理员出库
    """
        从book_table中删除掉对应数量的book
        状态为未借出(流通室）  不外借（阅览室），另外两种状态的book不可出库 状态和出库地点一一对应，不匹配的图书不可以出库
        使用了触发器 delete_book_trigger ：当所有的书都出库时，从booklist中删除掉对应的项
        使用了过程 get_book_cantakeoff ：查询对于的可出库图书

    """
    if request.session.get('login_type', None) != 'identity_admin':
        return HttpResponseRedirect("/")
    context = dict()
    context['name'] = request.session.get('name')
    if request.method == 'GET':
        return render(request, 'admin_takeoff.html', context=context)
    else:
        context['isbn'] = isbn = request.POST.get('isbn')  # ISBN
        context['takeoff_num'] = takeoff_num = request.POST.get('takeoff_num')  # 出库数量
        context['takeoff_place'] = takeoff_place = request.POST.get('takeoff_place')  # 出库优先（未借出、不外借）
        context['msg'] = "未知错误，请重试"
        if not isbn or not takeoff_num or not takeoff_place:
            context['msg'] = "请填写ISBN号、入出库数量和优先出库位置"
            return render(request, 'admin_takeoff.html', context=context)
        if takeoff_place != '图书流通室' and takeoff_place != '图书阅览室':
            context['msg'] = "优先出库位置必须为流通室或阅览室"
            return render(request, 'admin_takeoff.html', context=context)
        result = booklist_table.objects.filter(isbn=isbn)
        if not result.exists():
            context['msg'] = "ISBN录入有误，请检查"
            return render(request, 'admin_takeoff.html', context=context)

        ##查询当前isbn 、take_place对应的可出库图书,返回列表
        ##状态为未借出(流通室）  不外借（阅览室），另外两种状态的book不可出库
        if (isbn and takeoff_place):
            book_can_takeoff = book_table.objects.raw('CALL get_book_cantakeoff(%s, %s)', [isbn, takeoff_place])
            takeoff_num = int(takeoff_num)
            if len(book_can_takeoff) < takeoff_num:
                context['msg'] = "出库数量超过可出库图书总数！请检查"
                return render(request, 'admin_takeoff.html', context=context)
            book_id = ''
            book_takeoff = []
            for elem in book_can_takeoff:
                if takeoff_num > 0:
                    book_id += str(elem.book_id) + ','
                    book_takeoff.append(elem)
                    takeoff_num -= 1
                else:
                    break
            for elem in book_takeoff:
                elem.delete()
            context['msg'] = "出库成功！"
            context['book_id'] = book_id
            book_remain = book_table.objects.raw('CALL get_book_cantakeoff(%s, %s)', [isbn, takeoff_place])
            context['book_num'] = len(book_remain)
            return render(request, 'admin_takeoff.html', context=context)


def admin_takeoff_query(request):
    """
        admin_takeoff 附属函数 查询当前图书可以出库的数量
        使用了过程 get_book_cantakeoff ：查询对于的可出库图书
    """

    if request.session.get('login_type', None) != 'identity_admin':
        return HttpResponseRedirect("/")
    context = dict()
    context['name'] = request.session.get('name')
    context['isbn'] = isbn = request.POST.get('isbn')  # ISBN
    context['takeoff_place'] = takeoff_place = request.POST.get('takeoff_place')  # 出库地址
    if request.method == 'GET':
        return render(request, 'admin_takeoff.html', context=context)
    else:
        if not isbn or not takeoff_place:
            context['msg'] = "请填写ISBN号、出库位置"
            return render(request, 'admin_takeoff.html', context=context)
        if takeoff_place != '图书流通室' and takeoff_place != '图书阅览室':
            context['msg'] = "出库位置必须为流通室或阅览室"
            return render(request, 'admin_takeoff.html', context=context)
        result = booklist_table.objects.filter(isbn=isbn)
        if not result.exists():
            context['msg'] = "ISBN录入有误，请检查"
            return render(request, 'admin_takeoff.html', context=context)
        book_remain = book_table.objects.raw('CALL get_book_cantakeoff(%s, %s)', [isbn, takeoff_place])
        context['book_num'] = len(book_remain)
        return render(request, 'admin_takeoff.html', context=context)


def admin_pay(request):
    """
        管理员替读者还款
        使用了过程 update_reader_arrears_fn: 该过程用到了事务，使得还款超过界限时回退
    """
    if request.session.get('login_type', None) != 'identity_admin':
        return HttpResponseRedirect("/")
    context = dict()
    context['name'] = request.session.get('name')
    if request.method == 'GET':
        return render(request, 'admin_pay.html', context=context)
    else:
        context['reader_id'] = reader_id = request.POST.get('reader_id')
        context['money_num'] = money_num = request.POST.get('money_num')
        if not reader_id or not money_num:
            context['msg'] = "请填写完整的读者id和款数"
            return render(request, 'admin_pay.html', context=context)
        # if not reader_id.isdigit() or not money_num.isdigit():
        if not reader_id.isdigit() or not re.match(r'^\d+(\.\d+)?$', money_num):
            context['msg'] = "读者id和款数必须是数字！"
            return render(request, 'admin_pay.html', context=context)
        reader = reader_table.objects.filter(reader_id=reader_id)
        if not reader:
            context['msg'] = "读者id不存在！"
            return render(request, 'admin_pay.html', context=context)
        pay_num = float(money_num)
        with connection.cursor() as cursor:
            cursor.execute('CALL update_reader_arrears_fn(' + str(reader_id) + ',' + str(pay_num) + ')')
            row = cursor.fetchone()
            cursor.close()
            result = row[0]
            if (result >= 0):
                context['msg'] = "为读者还款" + str(pay_num) + "元成功！"
                context['reader_arrears'] = result
            else:
                context['msg'] = "还款失败，当前欠费小于还款数，你可以调整还款数之后重新还款！"
                context['reader_arrears'] = reader[0].arrears
            return render(request, 'admin_pay.html', context=context)

"""
def admin_pay_query(request):
    
     ### admin_pay 附属函数 管理员查询读者欠费多少
    
    if request.session.get('login_type', None) != 'identity_admin':
        return HttpResponseRedirect("/")
    context = dict()
    context['name'] = request.session.get('name')
    context['reader_id'] = reader_id = request.POST.get('reader_id')
    if request.method == 'GET':
        return render(request, 'admin_pay.html', context=context)
    else:

        reader = reader_table.objects.filter(reader_id=reader_id)
        if not reader:
            context['msg'] = "读者id不存在！"
            return render(request, 'admin_pay.html', context=context)
        context['reader_arrears'] = reader[0].arrears
        return render(request, 'admin_pay.html', context=context)
"""
def admin_pay_query(request):
    """
        admin_pay 附属函数 管理员查询读者欠费多少
    """
    if request.session.get('login_type', None) != 'identity_admin':
        return HttpResponseRedirect("/")
    context = dict()
    context['name'] = request.session.get('name')
    context['reader_id'] = reader_id = request.POST.get('reader_id')
    if request.method == 'GET':
        return render(request, 'admin_pay.html', context=context)
    else:
        #reader = reader_table.objects.all()
        if reader_id:
            reader = reader_table.objects.filter(reader_id=reader_id)
        else :
            context['msg'] = "请填写读者id"
            return render(request, 'admin_pay.html', context=context)
        if not reader:
            context['msg'] = "读者id不存在！"
            return render(request, 'admin_pay.html', context=context)
        reader_ID=reader[0].reader_id
        print(reader_ID)
        with connection.cursor() as cursor:
            cursor.execute("SELECT get_arrears_by_id(%s)", [reader_ID])
            arrears_value = cursor.fetchone()[0]
            print(arrears_value)
            #context['reader_arrears'] = arrears_value
            context['msg'] = "读者id为"+str(reader_ID)+"的欠费为"+str(arrears_value)+"元"
            return render(request, 'admin_pay.html', context=context)
def admin_recommend_operation(request):
    if request.session.get('login_type', None) != 'identity_admin':
        return HttpResponseRedirect("/")

    if request.method == 'GET':
        context = {'name': request.session.get('name')}
        return render(request, 'admin_recommend.html', context=context)
    else:
        #items = recommend_table.objects.filter(status='未处理').order_by('book_num')
        items = recommend_table.objects.filter(Q(status='未处理') | Q(status='同意，在途')).order_by('book_num')
        operations = []
        for item in items:
            operation = request.POST.get('admin_operation_' + str(item.reader_id_id)+'_'+str(item.isbn))

            if operation == '请选择操作...':
                items = recommend_table.objects.filter(Q(status='未处理') | Q(status='同意，在途')).order_by('book_num')
                context = {
                    'name': request.session.get('name'),
                    'msg': "有未进行操作的荐购，请检查后重新处理",
                    'items': items,
                }
                return render(request, 'admin_recommend.html', context=context)

            operations.append((item.reader_id_id, item.isbn, operation))
        for reader_id, isbn, operation in operations:
            item = recommend_table.objects.get(reader_id_id=reader_id, isbn=isbn)
            if operation == 'approve':
                item.status = '同意，在途'
                item.admin_operation = operation
                item.save()
            elif operation == 'reject':
                item.status = '拒绝'
                item.admin_operation = operation
                item.save()
            elif operation == 'finish':
                item.status = '已上架'
                item.admin_operation = operation
                item.save()
        items = recommend_table.objects.filter(Q(status='未处理') | Q(status='同意，在途')).order_by('book_num')
        context = {'msg': "处理荐购成功",
                   items: items,
                   'name': request.session.get('name'),
                   }
        return render(request, 'admin_recommend.html', context=context)

"""
def admin_recommend_operation(request):
    # 处理当前推荐表中 购买数量最小的那一份荐购，即处理次序的优先级由荐购数量来定义
    # 管理员选择同意荐购
    if request.session.get('login_type', None) != 'identity_admin':
        return HttpResponseRedirect("/")
    context = dict()
    context['name'] = request.session.get('name')
    if request.method == 'GET':
        return render(request, 'admin_recommend.html', context=context)
    else:

        items = recommend_table.objects.filter(status='未处理').order_by('book_num')
        for item in items:

            if item:
                reader_id_id = item.reader_id_id
                isbn = item.isbn
                book_num = item.book_num
                operation = request.POST.get('admin_operation')
                if (operation == '请选择操作...'):
                    context = {'msg': "请选择对当前荐购的操作", 'reader_id_id': reader_id_id, 'ISBN': isbn,
                           'book_num': book_num, 'recommend_book_status': 10}
                    return render(request, 'admin_recommend.html', context=context)

                item.status = '已处理'
                item.admin_operation = operation
                item.save()

        items = recommend_table.objects.filter(status='未处理').order_by('book_num')
        for item in items:
            if item:
                reader_id_id = item.reader_id_id
                ISBN = item.isbn
                book_num = item.book_num
                # 将元素的值添加到上下文中
                context = {'msg': "处理荐购成功", 'reader_id_id': reader_id_id, 'ISBN': ISBN,
                       'book_num': book_num, 'recommend_book_status': 10}
            else:
                context = {'msg': "处理荐购成功", 'recommend_book_status': 0}
        return render(request, 'admin_recommend.html', context=context)

    if request.session.get('login_type', None) != 'identity_admin':
        return HttpResponseRedirect("/")
    context = dict()
    context['name'] = request.session.get('name', None)
    if request.method == 'GET':
        return render(request, 'admin_recommend.html', context=context)
    else:
        
        context['reader_id_id'] = book_name = request.POST.get('book_name')  # 书名
        context['author'] = author = request.POST.get('author')  # 作者
        context['isbn'] = isbn = request.POST.get('isbn')  # ISBN
        context['publisher'] = publisher = request.POST.get('publisher')  # 出版社
        context['msg'] = "未知错误，请重试"
        
        result = recommend_table.objects.filter(status='未处理').order_by('isbn')

        book_message = []
        for elem in result:
            book_message.append(
                {
                    'ISBN': elem.isbn,
                    'book_num': elem.book_num,
                    'author': elem.author,
                    'publisher': elem.publisher,
                    'publish_date': elem.publish_date,
                    'num_inlib': len(book_table.objects.filter(isbn=elem.isbn)),
                    'num_forbid_borrow': len(book_table.objects.filter(isbn=elem.isbn, status='不外借')),
                    'num_not_borrow': len(book_table.objects.filter(isbn=elem.isbn, status='未借出')),
                    'num_have_borrow': len(book_table.objects.filter(isbn=elem.isbn, status='已借出')),
                    'num_have_reserve': len(book_table.objects.filter(isbn=elem.isbn, status='已预约')),
                    'image': elem.image
                }
            )
        context['msg'] = ''
        context['book_status'] = book_message
        return render(request, 'emoji_query.html', context=context)
    """


def admin_recommend(request):
    """
    查询所有未处理的荐购
    """
    if request.session.get('login_type', None) != 'identity_admin':
        return HttpResponseRedirect("/")

    context = {
        'name': request.session.get('name')
    }

    items = recommend_table.objects.filter(Q(status='未处理') | Q(status='同意，在途'))

    if not items:
        context['recommend_book_status'] = 0
    else:
        context['items'] = items

    return render(request, 'admin_recommend.html', context=context)

def reader_book_detail(request, isbn):
    book = get_object_or_404(booklist_table, isbn=isbn)
    return render(request, 'reader_book_info.html', {'book': book})


def libadmin_book_detail(request, isbn):
    book = get_object_or_404(booklist_table, isbn=isbn)
    return render(request, 'emoji_statistic.html', {'book': book})
