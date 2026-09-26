import secrets
import string

from django.db import models


def generate_aadhaar_number():
    return str(secrets.randbelow(900000000000) + 100000000000)


def generate_pan_number(record, offset=0):
    series_number = ((Aadhar_Details.objects.count() + offset) % 17576) + 1
    series = ""
    value = series_number - 1
    for _ in range(3):
        series = string.ascii_uppercase[value % 26] + series
        value //= 26
    serial = ((Aadhar_Details.objects.count() + offset) % 9999) + 1
    surname_initial = (record.Last_name or "X")[0].upper()
    prefix = f"{series}P{surname_initial}{serial:04d}"
    check_digit = string.ascii_uppercase[sum(ord(character) for character in prefix) % 26]
    return prefix + check_digit


class State(models.Model):
    name = models.CharField(max_length=30, unique=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name


class Aadhar_Details(models.Model):
    number = models.CharField(max_length=12, primary_key=True, default=generate_aadhaar_number, editable=False)
    pan_number = models.CharField(max_length=10, unique=True, null=True, editable=False)
    First_name = models.CharField(max_length=32)
    Middle_name = models.CharField(max_length=32, blank=True)
    Last_name = models.CharField(max_length=32)
    dob = models.DateField()
    choices = [("M", "Male"), ("F", "Female"), ("O", "Others")]
    gender = models.CharField(max_length=1, choices=choices)
    Father_name = models.CharField(max_length=50)
    Phone_number = models.PositiveBigIntegerField(unique=True)
    email = models.EmailField()
    photo = models.ImageField(upload_to="profiles", blank=True)
    address = models.TextField()
    state = models.ForeignKey(State, on_delete=models.CASCADE)
    pincode = models.IntegerField()

    def save(self, *args, **kwargs):
        while Aadhar_Details.objects.filter(number=self.number).exclude(pk=self.pk).exists():
            self.number = generate_aadhaar_number()
        if not self.pan_number:
            offset = 0
            self.pan_number = generate_pan_number(self, offset)
        else:
            offset = 0
        while Aadhar_Details.objects.filter(pan_number=self.pan_number).exclude(pk=self.pk).exists():
            offset += 1
            self.pan_number = generate_pan_number(self, offset)
        super().save(*args, **kwargs)

    @property
    def full_name(self):
        return " ".join(filter(None, [self.First_name, self.Middle_name, self.Last_name]))
