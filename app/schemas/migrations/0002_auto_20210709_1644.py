# Generated by Django 3.2.5 on 2021-07-09 16:44

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('schemas', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='dataschemas',
            name='id',
            field=models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID'),
        ),
        migrations.AlterField(
            model_name='schemacolumn',
            name='id',
            field=models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID'),
        ),
    ]
