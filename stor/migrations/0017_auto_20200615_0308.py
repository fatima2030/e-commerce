# Generated by Django 3.0.6 on 2020-06-15 10:08

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('stor', '0016_auto_20200614_1940'),
    ]

    operations = [
        migrations.AddField(
            model_name='category',
            name='tag',
            field=models.CharField(default='tag', max_length=17),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='category',
            name='parent',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='chiled', to='stor.Category'),
        ),
        migrations.AlterField(
            model_name='item',
            name='categories',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='stor.Category'),
        ),
    ]