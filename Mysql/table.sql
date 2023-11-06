create database if not exists db;
use db;
drop table if exists sc;
drop table if exists emoji;
drop table if exists course;
drop table if exists user;
create table user(
    uid int not null auto_increment,
    uname varchar(15) not null,
    mailAddr varchar(30),
    tel varchar(20),
    role int not null check ( role in (0,1,2,3) ), # 游客、管理员、教师、学生
#     stat int not null check ( stat in (0,1,2) ), # 离线、在线、停用
    pwd varchar(128) not null,
#     path varchar(100),# emoji数据的文件存放路径
#     layer int not null ,# 权力等级，可能不需要这个属性，暂时先留着
    constraint PK_user primary key user(uid)
);

# 不区分不同的课程，只区分每一堂课
create table course(
    cid int not null ,
    cname varchar(15) not null ,
    tid int ,# 教师id
    beginTime datetime not null ,
    endTime datetime not null ,
    constraint PK_course primary key course(cid),
    constraint FK_course_user foreign key(tid) references user(uid) on delete cascade on update cascade
);
# 需要另外建立ename和具体哪个emoji的映射
create table emoji(
    eid int not null auto_increment,
    ename varchar(128) not null,
    timeStamp datetime not null,
    uid int not null ,
#     cid int not null ,
    constraint PK_emoji primary key emoji(eid),
    constraint FK_emoji_user foreign key(uid) references user(uid) on delete cascade on update cascade
#     constraint FK_emoji_course foreign key(cid) references course(cid) on delete cascade on update cascade
);
# 用来控制课堂参与
create table sc(
    uid int not null ,
    cid int not null,
    constraint PK_sc primary key sc(uid,cid),
    constraint FK_sc_user foreign key(uid) references user(uid) on delete cascade on update cascade ,
    constraint FK_sc_course foreign key(cid) references course(cid) on delete cascade on update cascade
);

insert into user values (0,'admin','hb2002@mail.ustc.edu.cn','13695517640',1,'12345678');