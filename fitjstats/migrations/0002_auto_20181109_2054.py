# Generated by Django 2.1.2 on 2018-11-09 20:54

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('fitjstats', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='comment',
            name='created',
            field=models.DateTimeField(default=django.utils.timezone.now),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='post',
            name='num_female',
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name='post',
            name='num_male',
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name='post',
            name='num_rx',
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name='post',
            name='num_scale',
            field=models.IntegerField(default=0),
        ),
        migrations.AlterField(
            model_name='comment',
            name='comment_text',
            field=models.TextField(default=''),
        ),
        migrations.AlterField(
            model_name='comment',
            name='gender',
            field=models.CharField(choices=[(None, 'n/a'), ('m', 'male'), ('f', 'female'), ('o', 'other')], max_length=3, null=True),
        ),
        migrations.AlterField(
            model_name='comment',
            name='scale',
            field=models.CharField(choices=[(None, 'n/a'), ('RX', 'rx'), ('SC', 'scale')], max_length=2, null=True),
        ),
        migrations.AlterField(
            model_name='commenter',
            name='created',
            field=models.DateTimeField(),
        ),
    ]
