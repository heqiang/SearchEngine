# Generated by Django 2.2.1 on 2019-10-22 15:27

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('user', '0006_auto_20191022_1507'),
    ]

    operations = [
        migrations.AlterField(
            model_name='collect',
            name='collecttitle',
            field=models.CharField(max_length=255),
        ),
    ]