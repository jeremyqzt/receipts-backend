# Generated by Django 3.2 on 2022-05-13 20:00

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('uploader', '0009_auto_20220513_2000'),
    ]

    operations = [
        migrations.DeleteModel(
            name='ReceiptExpenseCategory',
        ),
        migrations.AddField(
            model_name='receipt',
            name='category',
            field=models.IntegerField(choices=[(1, 'Uncategorized'), (2, 'Prepay'), (3, 'Advertising'), (4, 'Tax Fee Due'), (5, 'Insurance'), (6, 'Interest'), (7, 'Maint'), (8, 'Meals'), (9, 'Office'), (10, 'Salary'), (11, 'Startup'), (12, 'Car')], default=1),
        ),
    ]
