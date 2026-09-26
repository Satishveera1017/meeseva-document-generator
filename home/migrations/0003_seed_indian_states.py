from django.db import migrations


INDIAN_STATES_AND_UNION_TERRITORIES = [
    "Andaman and Nicobar Islands",
    "Andhra Pradesh",
    "Arunachal Pradesh",
    "Assam",
    "Bihar",
    "Chandigarh",
    "Chhattisgarh",
    "Dadra and Nagar Haveli and Daman and Diu",
    "Delhi",
    "Goa",
    "Gujarat",
    "Haryana",
    "Himachal Pradesh",
    "Jammu and Kashmir",
    "Jharkhand",
    "Karnataka",
    "Kerala",
    "Ladakh",
    "Lakshadweep",
    "Madhya Pradesh",
    "Maharashtra",
    "Manipur",
    "Meghalaya",
    "Mizoram",
    "Nagaland",
    "Odisha",
    "Puducherry",
    "Punjab",
    "Rajasthan",
    "Sikkim",
    "Tamil Nadu",
    "Telangana",
    "Tripura",
    "Uttar Pradesh",
    "Uttarakhand",
    "West Bengal",
]


def seed_states(apps, schema_editor):
    State = apps.get_model("home", "State")
    for name in INDIAN_STATES_AND_UNION_TERRITORIES:
        State.objects.get_or_create(name=name)


def remove_states(apps, schema_editor):
    State = apps.get_model("home", "State")
    State.objects.filter(name__in=INDIAN_STATES_AND_UNION_TERRITORIES).delete()


class Migration(migrations.Migration):
    dependencies = [("home", "0002_alter_state_options")]

    operations = [migrations.RunPython(seed_states, remove_states)]
