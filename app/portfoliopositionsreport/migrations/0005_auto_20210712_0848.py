# Generated by Django 3.2.5 on 2021-07-12 08:48

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('portfoliopositionsreport', '0004_auto_20210712_0828'),
    ]

    operations = [
        migrations.AlterField(
            model_name='portfoliorow',
            name='file_1',
            field=models.ImageField(null=True, upload_to='media'),
        ),
        migrations.AlterField(
            model_name='portfoliorow',
            name='file_2',
            field=models.ImageField(null=True, upload_to='media'),
        ),
    ]