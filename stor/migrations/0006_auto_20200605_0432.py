# Generated by Django 3.0.6 on 2020-06-05 11:32

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('stor', '0005_auto_20200605_0353'),
    ]

    operations = [
        migrations.RenameField(
            model_name='userprofile',
            old_name='stipe_customer_id',
            new_name='stripe_customer_id',
        ),
        migrations.AddField(
            model_name='userprofile',
            name='one_click_purchasing',
            field=models.BooleanField(default=False),
        ),
    ]
