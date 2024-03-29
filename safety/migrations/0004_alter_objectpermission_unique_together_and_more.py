# Generated by Django 4.2 on 2023-04-16 21:49

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('auth', '0012_alter_user_first_name_max_length'),
        ('contenttypes', '0002_remove_content_type_name'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('safety', '0003_alter_objectpermission_options'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='objectpermission',
            unique_together=set(),
        ),
        migrations.AlterField(
            model_name='objectpermission',
            name='object_ct',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='object_of',
                                    to='contenttypes.contenttype', verbose_name='Target Content Type'),
        ),
        migrations.AlterField(
            model_name='objectpermission',
            name='object_id',
            field=models.IntegerField(verbose_name='Object ID'),
        ),
        migrations.AlterField(
            model_name='objectpermission',
            name='to_ct',
            field=models.ForeignKey(limit_choices_to={'model__in': ('user', 'group')},
                                    on_delete=django.db.models.deletion.CASCADE, related_name='entity_of',
                                    to='contenttypes.contenttype', verbose_name='Content Type'),
        ),
        migrations.AlterUniqueTogether(
            name='objectpermission',
            unique_together={('to_ct', 'permission', 'object_ct', 'object_id')},
        ),
        migrations.CreateModel(
            name='PermissionGroup',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255, verbose_name='Name')),
                ('target_id', models.IntegerField(verbose_name='Target ID')),
                ('permissions', models.ManyToManyField(to='auth.permission', verbose_name='Permissions')),
                ('target_ct',
                 models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='contenttypes.contenttype',
                                   verbose_name='Target Content Type')),
                ('users', models.ManyToManyField(to=settings.AUTH_USER_MODEL, verbose_name='Users')),
            ],
            options={
                'verbose_name': 'Permission Group',
                'verbose_name_plural': 'Permission Groups',
            },
        ),
    ]
