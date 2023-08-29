from django.conf.urls import url
from certificates.views import UploadCertificateTemplateView, GenerateCertificatePDFView, RenderCertificateView

urlpatterns = [
    url(r'^upload_template/$', UploadCertificateTemplateView.as_view(), name='upload_template'),
    url(r'(?P<template_id>\d+)/render/$', RenderCertificateView.as_view(), name='render'),
    url(r'(?P<template_id>\d+)/generate/$', GenerateCertificatePDFView.as_view(), name='generate'),
    url(r'', UploadCertificateTemplateView.as_view(), name='upload_template'),
]
