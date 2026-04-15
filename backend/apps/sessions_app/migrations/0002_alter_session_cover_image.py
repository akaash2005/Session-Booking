# Generated migration to add image upload support with MinIO

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('sessions_app', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='session',
            name='cover_image',
            field=models.ImageField(blank=True, null=True, upload_to='sessions/'),
        ),
    ]
