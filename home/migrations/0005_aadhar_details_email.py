from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [("home", "0004_aadhar_details_pan_number")]

    operations = [
        migrations.AddField(
            model_name="aadhar_details",
            name="email",
            field=models.EmailField(default="", max_length=254),
            preserve_default=False,
        ),
    ]