from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('system', '0052_adv_syslog_transport'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='Advanced',
            name='adv_legacy_ui',
        )
    ]
