# Generated by Django 3.2.21 on 2023-09-09 16:09

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('safety', '0008_rename_permissiongroup_objectgroup'),
    ]

    operations = [
        migrations.CreateModel(
            name='FakePost',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=100)),
                ('content', models.TextField()),
            ],
        ),
    ]