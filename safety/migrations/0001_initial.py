# Generated by Django 4.2 on 2023-04-16 19:49

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        ('contenttypes', '0002_remove_content_type_name'),
        ('auth', '0012_alter_user_first_name_max_length'),
    ]

    operations = [
        migrations.CreateModel(
            name='ObjectPermission',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('to_id', models.CharField(max_length=255, verbose_name='Target ID')),
                ('object_id', models.CharField(max_length=255, verbose_name='Object ID')),
                ('object_ct',
                 models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='contenttypes.contenttype',
                                   verbose_name='Content Type')),
                ('permission', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='auth.permission',
                                                 verbose_name='Permission')),
                ('to_ct', models.ForeignKey(limit_choices_to={'model__in': ('user', 'group')},
                                            on_delete=django.db.models.deletion.CASCADE, to='contenttypes.contenttype',
                                            verbose_name='Content Type')),
            ],
            options={
                'verbose_name': 'User object permission',
                'verbose_name_plural': 'User object permissions',
                'unique_together': {('to_ct', 'permission', 'object_ct', 'object_id')},
            },
        ),
    ]
