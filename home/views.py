import base64
import html
import mimetypes
from io import BytesIO
from pathlib import Path

import qrcode
from django.conf import settings
from django.http import Http404, HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils.safestring import mark_safe
from django.core.mail import EmailMessage
from .forms import RegistrationForm
from .models import Aadhar_Details


def main(request):
    return render(request, "main.html")


def registration(request):
    form = RegistrationForm(request.POST or None, request.FILES or None)
    if request.method == "POST" and form.is_valid():
        form.save()
        return redirect("main")
    return render(request, "registration.html", {"form": form})


def document_choice(request):
    return render(request, "document_choice.html")


def verify(request):
    error = None
    if request.method == "POST":
        record = Aadhar_Details.objects.filter(
            Phone_number=request.POST.get("mobile", "").strip(),
            Father_name__iexact=request.POST.get("father_name", "").strip(),
            Last_name__iexact=request.POST.get("last_name", "").strip(),
        ).first()
        if record:
            return redirect("download", number=record.number)
        error = "The three details did not match a registered record."
    return render(request, "verify.html", {"error": error})


def download(request, number):
    record = get_object_or_404(Aadhar_Details, number=number)
    return render(request, "download.html", {"record": record})


def delivery_options(request, number, kind):
    if kind not in {"masked", "unmasked", "pan"}:
        raise Http404
    record = get_object_or_404(Aadhar_Details, number=number)
    return render(request, "delivery_options.html", {
        "record": record,
        "kind": kind,
    })


def email_document(request, number, kind):
    if kind not in {"masked", "unmasked", "pan"}:
        raise Http404
    if request.method != "POST":
        return redirect("delivery_options", number=number, kind=kind)

    record = get_object_or_404(Aadhar_Details, number=number)
    if not record.email:
        return render(request, "delivery_options.html", {
            "record": record,
            "kind": kind,
            "error": "This record does not have an email address.",
        })

    if kind == "pan":
        document = _pan_svg(record).encode("utf-8")
        filename = f"pan-{record.pan_number}.svg"
        document_name = "PAN"
    else:
        document = _document_svg(record, kind == "masked").encode("utf-8")
        filename = f"aadhaar-{kind}-{record.number}.svg"
        document_name = f"{kind.title()} Aadhaar"

    message = EmailMessage(
        subject=f"Your {document_name} document",
        body=f"Please find your {document_name} document attached.",
        from_email=getattr(settings, "DEFAULT_FROM_EMAIL", settings.EMAIL_HOST_USER),
        to=[record.email],
    )
    message.attach(filename, document, "image/svg+xml")
    message.send()
    return render(request, "delivery_options.html", {
        "record": record,
        "kind": kind,
        "sent": True,
    })


def pan_verify(request, number):
    record = get_object_or_404(Aadhar_Details, number=number) if number else None
    error = None
    if request.method == "POST":
        submitted_number = request.POST.get("aadhaar_number", "").strip()
        submitted_dob = request.POST.get("dob", "").strip()
        record = Aadhar_Details.objects.filter(number=submitted_number).first()
        if record and submitted_dob == record.dob.isoformat():
            return redirect("pan_animation", number=record.number)
        error = "The Aadhaar number and date of birth did not match."
    return render(request, "pan_verify.html", {"record": record, "error": error})


def pan_document(request, number):
    record = get_object_or_404(Aadhar_Details, number=number)
    return render(request, "pan_document.html", {
        "record": record,
        "svg": mark_safe(_pan_svg(record)),
    })


def pan_animation(request, number):
    record = get_object_or_404(Aadhar_Details, number=number)
    return render(request, "pan_animation.html", {"record": record})


def document_view(request, number, kind):
    if kind not in {"masked", "unmasked"}:
        raise Http404
    record = get_object_or_404(Aadhar_Details, number=number)
    return render(request, "document.html", {
        "record": record,
        "kind": kind,
        "display_number": "X" * 8 + record.number[-4:] if kind == "masked" else record.number,
        "gender_display": record.get_gender_display().upper(),
    })


def qr_code(request, number):
    get_object_or_404(Aadhar_Details, number=number)
    qr = qrcode.make(request.build_absolute_uri(f"/qr/{number}/details/"))
    output = BytesIO()
    qr.save(output, format="PNG")
    return HttpResponse(output.getvalue(), content_type="image/png")


def qr_details(request, number):
    record = get_object_or_404(Aadhar_Details, number=number)
    return render(request, "qr_details.html", {"record": record})


def _document_svg(record, masked):
    name = html.escape(record.full_name)
    father_name = html.escape(record.Father_name)
    address = html.escape(record.address)
    state = html.escape(record.state.name)
    gender = html.escape(record.get_gender_display().upper())
    date_of_birth = record.dob.strftime("%Y-%m-%d")

    def inline_asset(filename, mime_type):
        asset_path = Path(settings.BASE_DIR) / "home" / "static" / filename
        if not asset_path.exists():
            return ""
        return f"data:{mime_type};base64,{base64.b64encode(asset_path.read_bytes()).decode()}"

    aadhaar_logo = inline_asset("aadhaar-logo.png", "image/png")
    government_strip = inline_asset("government-strip.png", "image/png")
    emblem = inline_asset("emblem.png", "image/png")
    qr = qrcode.make(f"Aadhaar number: {record.number}; Name: {record.full_name}")
    qr_output = BytesIO()
    qr.save(qr_output, format="PNG")
    qr_data = base64.b64encode(qr_output.getvalue()).decode()

    photo_data = ""
    photo_type = "image/jpeg"
    if record.photo:
        try:
            photo_type = mimetypes.guess_type(record.photo.name)[0] or "image/jpeg"
            photo_data = base64.b64encode(record.photo.read()).decode()
        finally:
            record.photo.close()
    photo = (
        f"<image href='data:{photo_type};base64,{photo_data}' x='10' y='80' "
        "width='150' height='120' preserveAspectRatio='xMidYMin slice'/>"
        if photo_data
        else "<rect x='10' y='80' width='150' height='120' fill='#dbe4e8'/><text x='42' y='145' font-size='17' font-family='Arial'>No photo</text>"
    )
    emblem_image = f"<image href='{emblem}' x='52' y='4' width='38' height='64' preserveAspectRatio='xMidYMid meet'/>" if emblem else ""
    logo_image = f"<image href='{aadhaar_logo}' x='52' y='4' width='54' height='62' preserveAspectRatio='xMidYMid meet'/>" if aadhaar_logo else ""
    government_image = f"<image href='{government_strip}' x='150' y='7' width='300' height='52' preserveAspectRatio='xMidYMid meet'/>" if government_strip else ""
    government_fallback = "<text x='225' y='28' font-size='13' font-family='Noto Sans Devanagari, Arial' text-anchor='middle'>भारत सरकार</text><text x='225' y='47' font-size='12' font-family='Arial' text-anchor='middle'>GOVERNMENT OF INDIA</text>"
    footer = "<text x='280' y='292' font-size='16' fill='#c8524b' font-family='Noto Sans Telugu, Nirmala UI, Arial' text-anchor='middle'>నా ఆధార్, నా గుర్తింపు</text>"
    display_number = "X" * 8 + record.number[-4:] if masked else record.number
    number_text = f"{display_number[:4]} {display_number[4:8]} {display_number[8:]}"
    mini_front = f"""
            <g>
                <rect width='600' height='300' fill='white' stroke='#111' stroke-width='2'/>
                    {emblem_image}{government_image or government_fallback}
                {photo}
                    <text x='200' y='96' font-size='17' font-family='Noto Sans Telugu, Nirmala UI, Arial'>పేరు: {name}</text>
                    <text x='200' y='118' font-size='17' font-family='Arial'>Name: {name}</text>
                    <text x='200' y='140' font-size='17' font-family='Noto Sans Telugu, Nirmala UI, Arial'>పుట్టిన తేదీ/DOB: {date_of_birth}</text>
                    <text x='200' y='162' font-size='17' font-family='Noto Sans Telugu, Nirmala UI, Arial'>పురుషుడు/{gender}</text>
                    <image href='data:image/png;base64,{qr_data}' x='500' y='174' width='82' height='82'/>
                    <text x='200' y='248' font-size='27' font-family='Georgia, serif'>{number_text}</text>
                    <line x1='0' y1='261' x2='600' y2='261' stroke='red' stroke-width='2'/>
                    {footer}
            </g>"""
    mini_back = f"""
      <g>
        <rect width='600' height='300' fill='white' stroke='#111' stroke-width='2'/>
            {logo_image}{government_image or government_fallback}
            <text x='18' y='129' font-size='16' font-family='Noto Sans Telugu, Nirmala UI, Arial' font-weight='bold'>చిరునామా: {father_name}</text>
            <text x='18' y='151' font-size='14' font-family='Arial'>Address: {address[:42]}</text>
            <text x='18' y='173' font-size='14' font-family='Arial'>{state} - {record.pincode}</text>
            <image href='data:image/png;base64,{qr_data}' x='426' y='75' width='132' height='132'/>
            <text x='200' y='248' font-size='27' font-family='Georgia, serif'>{number_text}</text>
        <line x1='0' y1='268' x2='600' y2='268' stroke='red' stroke-width='2'/>
            <text x='92' y='281' font-size='12' font-family='Arial' text-anchor='middle'>☎</text><text x='92' y='294' font-size='12' font-family='Arial' text-anchor='middle'>1947</text>
            <text x='300' y='281' font-size='12' font-family='Arial' text-anchor='middle'>✉</text><text x='300' y='294' font-size='12' font-family='Arial' text-anchor='middle'>help@uidai.gov.in</text>
            <text x='508' y='281' font-size='12' font-family='Arial' text-anchor='middle'>◉</text><text x='508' y='294' font-size='12' font-family='Arial' text-anchor='middle'>www.uidai.gov.in</text>
      </g>"""

    width, height = 600, 620
    details = f"<g>{mini_front}</g><g transform='translate(0 320)'>{mini_back}</g>"
    return f"<svg xmlns='http://www.w3.org/2000/svg' width='{width}' height='{height}' viewBox='0 0 {width} {height}'>{details}</svg>"


def _pan_svg(record):
    name = html.escape(record.full_name)
    father_name = html.escape(record.Father_name)
    address = html.escape(record.address)
    pan = html.escape(record.pan_number)
    photo_data = ""
    photo_type = "image/jpeg"
    if record.photo:
        try:
            photo_type = mimetypes.guess_type(record.photo.name)[0] or "image/jpeg"
            photo_data = base64.b64encode(record.photo.read()).decode()
        finally:
            record.photo.close()
    photo = (
        f"<image href='data:{photo_type};base64,{photo_data}' x='390' y='90' width='120' height='145' preserveAspectRatio='xMidYMid slice'/>"
        if photo_data
        else "<rect x='390' y='90' width='120' height='145' fill='white'/><text x='412' y='170' font-size='14'>Photo</text>"
    )
    qr = qrcode.make(f"PAN: {record.pan_number}; Name: {record.full_name}")
    qr_output = BytesIO()
    qr.save(qr_output, format="PNG")
    qr_data = base64.b64encode(qr_output.getvalue()).decode()
    gandhi_path = Path(settings.BASE_DIR) / "home" / "static" / "gandhi.jpg"
    gandhi_data = base64.b64encode(gandhi_path.read_bytes()).decode() if gandhi_path.exists() else ""
    gandhi_image = (
        f"<image href='data:image/jpeg;base64,{gandhi_data}' x='160' y='25' width='280' height='310' "
        "preserveAspectRatio='xMidYMid meet' opacity='0.13'/>"
        if gandhi_data
        else ""
    )
    front = f"""
            <g>
                <rect width='600' height='360' rx='12' fill='#4aaed4' stroke='#000000' stroke-width='4'/>
                {gandhi_image}
                <text x='24' y='40' font-size='22' font-family='Arial'>आयकर विभाग</text>
                <text x='24' y='65' font-size='14' font-family='Arial'>INCOME TAX DEPARTMENT</text>
                <text x='425' y='40' font-size='22' font-family='Arial'>भारत सरकार</text>
                <text x='425' y='65' font-size='14' font-family='Arial'>GOVT. OF INDIA</text>
                <text x='24' y='130' font-size='18' font-family='Arial'>Name: {name}</text>
                <text x='24' y='164' font-size='18' font-family='Arial'>Father: {father_name}</text>
                <text x='24' y='198' font-size='18' font-family='Arial'>DOB: {record.dob}</text>
                <text x='24' y='255' font-size='28' font-family='Arial' font-weight='bold' letter-spacing='3'>{pan}</text>
                {photo}
                <image href='data:image/png;base64,{qr_data}' x='525' y='90' width='55' height='55'/>
            </g>"""
    back = f"""
            <g transform='translate(0 380)'>
                <rect width='600' height='360' rx='12' fill='#4aaed4' stroke='#000000' stroke-width='4'/>
                {gandhi_image}
                <text x='24' y='50' font-size='18' font-family='Arial'>Permanent Account Number Card</text>
                <text x='24' y='102' font-size='17' font-family='Arial'>Address:</text>
                <text x='24' y='135' font-size='16' font-family='Arial'>{address[:52]}</text>
                <text x='24' y='168' font-size='16' font-family='Arial'>{html.escape(record.state.name)} - {record.pincode}</text>
                <text x='24' y='245' font-size='18' font-family='Arial'>PAN: {pan}</text>
                <text x='24' y='285' font-size='14' font-family='Arial'>If found, please return to the Income Tax Department.</text>
            </g>"""
    return f"<svg xmlns='http://www.w3.org/2000/svg' width='600' height='740' viewBox='0 0 600 740'>{front}{back}</svg>"


def document_download(request, number, kind):
    if kind not in {"masked", "unmasked"}:
        raise Http404
    record = get_object_or_404(Aadhar_Details, number=number)
    svg = _document_svg(record, kind == "masked").encode("utf-8")
    response = HttpResponse(svg, content_type="image/svg+xml; charset=utf-8")
    response["Content-Disposition"] = f'attachment; filename="aadhaar-{kind}-{number}.svg"'
    response["Content-Length"] = str(len(svg))
    return response


def pan_download(request, number):
    record = get_object_or_404(Aadhar_Details, number=number)
    svg = _pan_svg(record).encode("utf-8")
    response = HttpResponse(svg, content_type="image/svg+xml; charset=utf-8")
    response["Content-Disposition"] = f'attachment; filename="pan-{record.pan_number}.svg"'
    response["Content-Length"] = str(len(svg))
    return response
