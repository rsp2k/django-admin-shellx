# Generated by Django 4.2.10 on 2024-02-21 16:53

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("django_web_repl", "0003_terminalcommand_prompt"),
    ]

    operations = [
        migrations.AlterField(
            model_name="terminalcommand",
            name="command",
            field=models.CharField(max_length=100),
        ),
        migrations.AddConstraint(
            model_name="terminalcommand",
            constraint=models.UniqueConstraint(
                fields=("command", "prompt"), name="unique_command_prompt"
            ),
        ),
    ]
