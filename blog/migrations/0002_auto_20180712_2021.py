# Generated by Django 2.0.6 on 2018-07-12 12:21

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('blog', '0001_initial'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='article2tag',
            unique_together=set(),
        ),
        migrations.AlterUniqueTogether(
            name='articleupdown',
            unique_together=set(),
        ),
    ]