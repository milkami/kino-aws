# Generated by Django 3.2.13 on 2022-08-10 07:14

import imp
from django.db import migrations
from cinemas.models import Cinemas

def change_buffer(*args):
    cinemas= Cinemas.objects.filter(chain__isnull = True).update(buffer=5)


class Migration(migrations.Migration):
    

    dependencies = [
        ('cinemas', '0009_cinemas_buffer'),
    ]

    operations = [
        migrations.RunPython(change_buffer),

    ]
