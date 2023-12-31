# Generated by Django 4.2.6 on 2023-11-02 17:28

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='User',
            fields=[
                ('uid', models.AutoField(primary_key=True, serialize=False)),
                ('uname', models.CharField(max_length=15)),
                ('mailAddr', models.CharField(blank=True, max_length=30, null=True)),
                ('tel', models.CharField(blank=True, max_length=20, null=True)),
                ('role', models.IntegerField(choices=[(0, 'visitor'), (1, 'admin'), (2, 'teacher'), (3, 'student')])),
                ('pwd', models.CharField(max_length=128)),
            ],
        ),
        migrations.CreateModel(
            name='Emoji',
            fields=[
                ('eid', models.AutoField(primary_key=True, serialize=False)),
                ('ename', models.CharField(max_length=128)),
                ('timeStamp', models.DateTimeField()),
                ('uid', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='myLibrary.user')),
            ],
        ),
        migrations.CreateModel(
            name='Course',
            fields=[
                ('cid', models.IntegerField(primary_key=True, serialize=False)),
                ('cname', models.CharField(max_length=15)),
                ('beginTime', models.DateTimeField()),
                ('endTime', models.DateTimeField()),
                ('tid', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='myLibrary.user')),
            ],
        ),
    ]
