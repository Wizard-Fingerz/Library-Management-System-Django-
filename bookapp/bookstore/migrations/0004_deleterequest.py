# Generated by Django 4.0.3 on 2022-07-18 21:41

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('bookstore', '0003_alter_book_cover_chat'),
    ]

    operations = [
        migrations.CreateModel(
            name='DeleteRequest',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('delete_request', models.CharField(blank=True, max_length=100, null=True)),
            ],
        ),
    ]
