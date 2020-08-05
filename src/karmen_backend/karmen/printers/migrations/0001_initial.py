# Generated by Django 3.0.8 on 2020-07-31 11:56

from django.db import migrations, models
import django.db.models.deletion
import karmen.models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Printer',
            fields=[
                ('id', karmen.models.IdField(serialize=False)),
                ('name', models.CharField(help_text='Printer will be presented by this name.', max_length=255, verbose_name='Name')),
                ('token', models.CharField(help_text='Printer most either associated with a pill device or issued by a key manager', max_length=255, verbose_name='Device token')),
                ('api_key', models.CharField(blank=True, help_text='API key used to access the printer', max_length=255, verbose_name='API key')),
                ('created_on', models.DateTimeField(auto_now_add=True)),
                ('last_updated_on', models.DateTimeField(auto_now=True)),
            ],
        ),
        migrations.CreateModel(
            name='PrinterInGroup',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
            ],
        ),
        migrations.CreateModel(
            name='UserOnPrinter',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('role', models.CharField(choices=[('admin', 'admin'), ('user', 'user')], default='user', max_length=20, verbose_name='User role')),
                ('printer', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='printers.Printer')),
            ],
        ),
    ]