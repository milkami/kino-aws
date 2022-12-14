# Generated by Django 3.2.13 on 2022-09-12 09:27

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('cinemas', '0013_alter_cinemas_options'),
        ('stats', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='AppUsers',
            fields=[
                ('id', models.IntegerField(blank=True, primary_key=True, serialize=False)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
            options={
                'db_table': 'users',
                'managed': False,
            },
        ),
        migrations.CreateModel(
            name='Errors',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('error', models.IntegerField(blank=True, default=0, null=True)),
                ('alert', models.IntegerField(blank=True, default=0, null=True)),
                ('warning', models.IntegerField(blank=True, default=0, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
        ),
        migrations.CreateModel(
            name='Statistics',
            fields=[
            ],
            options={
                'verbose_name': 'Statistic',
                'verbose_name_plural': 'Statistics',
                'proxy': True,
                'indexes': [],
                'constraints': [],
            },
            bases=('cinemas.cinemas',),
        ),
    ]
