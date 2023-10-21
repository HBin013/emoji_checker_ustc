"""Library URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from myLibrary import views

urlpatterns = [
    path('', views.home),
    path('admin/', admin.site.urls),

    path('login_view/', views.login_view),  # 登录
    path('register/', views.register),  # 注册
    path('logout_view/', views.logout_view),  # 退出登录

    path('user_index/', views.user_index),  # 读者首页
    path('reader_query/', views.emoji_query),  # 读者书目状态查询
    path('emoji_history/', views.emoji_history),  # 读者个人状态查询
    path('reader_reserve/', views.reader_reserve),  # 读者预约登记
    path('reader_recommend/', views.reader_recommend),  # 读者荐购

    path('admin_index/', views.admin_index),  # 管理员首页
    path('admin_query/', views.admin_query),  # 读者书目状态查询
    path('admin_borrow/', views.admin_borrow),  # 管理员借书
    path('admin_return/', views.admin_return),  # 管理员还书
    path('admin_upload/', views.admin_upload),  # 管理员入库
    path('admin_takeoff/', views.admin_takeoff),  # 管理员出库
    path('admin_pay/', views.admin_pay),  # 管理员缴扣费
    path('admin_recommend/', views.admin_recommend),  # 管理员处理荐购请求
    path('admin_recommend_operation/', views.admin_recommend_operation),

    path('admin_takeoff_query/', views.admin_takeoff_query),  # 查询可以出库的图书数量
    path('admin_pay_query/', views.admin_pay_query),  # admin_pay 附属函数 管理员查询当前读者欠费多少
    # 费用带来问题：
    # 1.读者借书时，如果余额为负数，不能借书
    # 2.读者还书时，如果超期，则需要联系管理员，进行扣费
    # path('upload_file/', views.upload_file),
    path('libadmin/book/<str:isbn>/', views.libadmin_book_detail, name='libadmin_book_detail'),
    path('reader/book/<str:isbn>/', views.reader_book_detail, name='reader_book_detail'),
]

# 使用了 <str:isbn> 作为 URL 路径参数，这样可以将请求 URL 中的 ISBN 号提取出来，并将其作为参数传递给视图函数 views.book_detail。使用 name='book_detail' 给该路由命名，以便在视图函数中使用 {% url 'book_detail' isbn %} 的方式生成书籍详细信息的 URL。
# 在视图函数 views.book_detail(位于views.py里) 中，可以根据 ISBN 号查询书籍详细信息，并返回书籍详细信息的 HTML 页面。
'''
符号表：
    1.读者id reader_id
    2.管理员id admin_id
    3.书目id book_id
    4.书目名称 book_name
    5.书目作者 author
    6.出库 admin_takeoff
    7.入库 admin_upload
    8.管理员查询 admin_query
    9.出版社 publisher
    10.出版时间 publish_date
'''
