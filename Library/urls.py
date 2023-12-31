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

    path('login_view/', views.login_view, name='login_view'),  # 登录
    path('register/', views.register, name='register'),  # 注册
    path('logout_view/', views.logout_view, name='logout_view'),  # 退出登录
    path('modifyPwd/', views.modifyPwd, name='modifyPwd'),  # 修改密码

    path('user_index/', views.user_index, name='user_index'),  # 用户首页
    path('emoji_history/', views.emoji_history, name='emoji_history'),  # 查看历史emoji

    path('admin_index/', views.admin_index, name='admin_index'),  # 管理员首页
    path('admin_query/', views.admin_query, name='admin_query'),  # 查看用户数据
    path('admin_query/add_user/', views.add_user, name='add_user'),  # 添加用户数据
    path('admin_query/add/', views.add, name='add'), # 添加用户数据页面跳转
    path('admin_query/modify_user/', views.modify_user, name='modify_user'),  # 修改用户数据
    path('admin_query/modify/', views.modify, name='modify'), # 添加用户数据页面跳转
    path('admin_query/delete_user/', views.delete_user, name='delete_user'), # 删除用户
    path('admin_query/user_emoji/', views.user_emoji, name='user_emoji'), # 查看用户历史emoji
    path('emoji_query/', views.emoji_query, name='emoji_query'),  # 查看emoji数据
    path('emoji_export/', views.emoji_export, name='emoji_export'),  # 导出emoji数据
    path('emoji_statistic/', views.emoji_statistic, name='emoji_statistic'),  # 统计emoji数据
    path('emoji_statistic/chart_data/', views.emoji_chart, name='emoji_chart'),  # 统计emoji数据
    path('send_emoji/', views.send_emoji, name='send_emoji')  # 发送emoji

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
