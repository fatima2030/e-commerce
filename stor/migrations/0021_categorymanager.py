# Generated by Django 3.0.6 on 2020-06-15 14:34

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('stor', '0020_auto_20200615_0648'),
    ]

    operations = [
        migrations.CreateModel(
            name='CategoryManager',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
            ],
        ),
    ]
