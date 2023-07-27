from django.conf.urls import url
from certificates.views import generate_certificate_pdf, render_certificate

urlpatterns = [
    url('render/', render_certificate, name='render'),
    url('generate/', generate_certificate_pdf, name='generate'),
]
