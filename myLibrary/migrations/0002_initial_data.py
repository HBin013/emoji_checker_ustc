from django.contrib.auth.hashers import make_password
from django.db import migrations


def insert_initial_data(apps, schema_editor):
    User = apps.get_model('myLibrary', 'User')
    # data = User.objects.get(uname="admin")
    # data.delete()
    User.objects.create(uname="admin", mailAddr="hb2002@mail.ustc.edu.cn",
                        tel="13695517640", role=1, pwd=make_password("12345678"))


class Migration(migrations.Migration):
    dependencies = [
        ('myLibrary', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(insert_initial_data),
    ]
