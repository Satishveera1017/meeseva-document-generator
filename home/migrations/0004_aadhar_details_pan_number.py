import string

from django.db import migrations, models


def populate_pan_numbers(apps, schema_editor):
    Aadhar_Details = apps.get_model("home", "Aadhar_Details")
    for index, record in enumerate(Aadhar_Details.objects.order_by("number")):
        value = index % 17576
        series = ""
        for _ in range(3):
            series = string.ascii_uppercase[value % 26] + series
            value //= 26
        serial = (index % 9999) + 1
        surname_initial = (record.Last_name or "X")[0].upper()
        prefix = f"{series}P{surname_initial}{serial:04d}"
        check_digit = string.ascii_uppercase[sum(ord(character) for character in prefix) % 26]
        record.pan_number = prefix + check_digit
        record.save(update_fields=["pan_number"])


class Migration(migrations.Migration):
    dependencies = [("home", "0003_seed_indian_states")]

    operations = [
        migrations.AddField(
            model_name="aadhar_details",
            name="pan_number",
            field=models.CharField(editable=False, max_length=10, null=True, unique=True),
        ),
        migrations.RunPython(populate_pan_numbers, migrations.RunPython.noop),
    ]