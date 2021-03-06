# Generated by Django 3.2.9 on 2022-01-30 14:56

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0012_profile_welcome_email'),
    ]

    operations = [
        migrations.AlterField(
            model_name='userkyc',
            name='photo',
            field=models.FileField(default='default_photo.jpg', upload_to='gameon/kyc/front_path/'),
        ),
        migrations.AlterField(
            model_name='userkyc',
            name='photo_2',
            field=models.FileField(default='default_photo.jpg', upload_to='gameon/kyc/front_back/'),
        ),
        migrations.AlterField(
            model_name='userkyc',
            name='status',
            field=models.CharField(choices=[('not_submitted', 'Not Submitted'), ('submitted', 'Submitted'), ('pending', 'Pending'), ('rejected', 'Rejected'), ('approved', 'Approved')], default='not_submitted', max_length=100),
        ),
    ]
