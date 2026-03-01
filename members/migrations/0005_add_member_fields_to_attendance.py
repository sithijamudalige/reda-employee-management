# Generated manually on 2026-01-13 06:01

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('members', '0004_attendance'),
    ]

    operations = [
        migrations.AddField(
            model_name='attendance',
            name='member_etf_no',
            field=models.CharField(default='', max_length=50),
        ),
        migrations.AddField(
            model_name='attendance',
            name='member_fullname',
            field=models.CharField(default='', max_length=255),
        ),
        migrations.AlterField(
            model_name='attendance',
            name='member_id',
            field=models.IntegerField(default=0),
        ),
        migrations.AlterModelTable(
            name='attendance',
            table='attendance',
        ),
        migrations.AlterUniqueTogether(
            name='attendance',
            unique_together={('member_id', 'attendance_month')},
        ),
    ]
