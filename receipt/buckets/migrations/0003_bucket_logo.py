# Generated by Django 3.2 on 2022-02-03 02:16

from django.db import migrations
import thumbnails.fields


class Migration(migrations.Migration):

    dependencies = [
        ('buckets', '0002_alter_bucket_create_date'),
    ]

    operations = [
        migrations.AddField(
            model_name='bucket',
            name='logo',
            field=thumbnails.fields.ImageField(default=None, null=True, upload_to='logos/'),
        ),
    ]
