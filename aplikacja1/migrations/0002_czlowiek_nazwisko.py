# Generated by Django 5.1.2 on 2024-10-18 10:15

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('aplikacja1', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='czlowiek',
            name='nazwisko',
            field=models.CharField(default='', max_length=40, verbose_name='Nazwisko'),
        ),
    ]
