from django.urls import path

from . import views

urlpatterns = [
    path("", views.main, name="main"),
    path("generate/", views.registration, name="registration"),
    path("documents/", views.document_choice, name="document_choice"),
    path("verify/", views.verify, name="verify"),
    path("download/<str:number>/", views.download, name="download"),
    path("delivery/<str:number>/<str:kind>/", views.delivery_options, name="delivery_options"),
    path("delivery/<str:number>/<str:kind>/email/", views.email_document, name="email_document"),
    path("pan/verify/", views.pan_verify, {"number": None}, name="pan_verify"),
    path("pan/<str:number>/animation/", views.pan_animation, name="pan_animation"),
    path("pan/<str:number>/", views.pan_document, name="pan_document"),
    path("pan/<str:number>/download/", views.pan_download, name="pan_download"),
    path("document/<str:number>/<str:kind>/", views.document_view, name="document_view"),
    path("download/<str:number>/<str:kind>/", views.document_download, name="document_download"),
    path("qr/<str:number>/", views.qr_code, name="qr_code"),
    path("qr/<str:number>/details/", views.qr_details, name="qr_details"),
]
