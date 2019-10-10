from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('storage', '0022_auto_20190809_1137'),
    ]

    operations = [
        migrations.CreateModel(
            name='Dataset',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(unique=True, max_length=255)),
                ('encryption_key', models.TextField(null=True, default=None)),
            ],
        ),
    ]
