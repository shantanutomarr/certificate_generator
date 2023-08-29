from typing import Any
from django import http
from django.shortcuts import redirect
from django.urls import reverse
from django.http import HttpResponse
from django.template import Context, Template
from django.contrib import messages
from django.views.generic import FormView
from django.conf import settings

from weasyprint import HTML

from certificates.forms import CertificateTemplateForm, CertificateContextForm
from certificates.zip_parser import TemplateZipParser
from certificates.models import CertificateTemplate


class UploadCertificateTemplateView(FormView):
    template_name = 'upload_template.html'
    form_class = CertificateTemplateForm

    def form_valid(self, form):
        template = form.save()
        template.parsed_html = TemplateZipParser(template.zip_file.path, "{}/certificates/templates/{}".format(settings.STATIC_ROOT, template.slug)).parse()
        template.save()
        messages.success(self.request, 'Template uploaded successfully.')
        return redirect(reverse("generate", kwargs={"template_id": template.id}))

    def form_invalid(self, form):
        messages.error(self.request, 'There were errors.')
        return self.render_to_response(self.get_context_data(form=form))
    
    def get_context_data(self, **kwargs):
        context = super(UploadCertificateTemplateView, self).get_context_data(**kwargs)
        context["uploaded_templates"] = CertificateTemplate.objects.all()
        return context


class RenderCertificateView(FormView):
    form_class = CertificateContextForm
    template_name = 'certificate_context_form.html'

    def dispatch(self, request, *args, **kwargs):
        self.certificate_template = CertificateTemplate.objects.get(id=self.kwargs["template_id"])
        return super(RenderCertificateView, self).dispatch(request, *args, **kwargs)
    
    def form_valid(self, form):
        certificate_context = form.cleaned_data
        html_string = Template(self.certificate_template.parsed_html).render(Context(certificate_context))
        return HttpResponse(html_string)

    def form_invalid(self, form):
        messages.error(self.request, 'There were errors.')
        return self.render_to_response(self.get_context_data(form=form))


class GenerateCertificatePDFView(FormView):
    form_class = CertificateContextForm
    template_name = 'certificate_context_form.html'

    def dispatch(self, request, *args, **kwargs):
        self.certificate_template = CertificateTemplate.objects.get(id=self.kwargs["template_id"])
        return super(GenerateCertificatePDFView, self).dispatch(request, *args, **kwargs)
    
    def form_valid(self, form):
        certificate_context = form.cleaned_data
        html_string = Template(self.certificate_template.parsed_html).render(Context(certificate_context))
        pdf_file = self._generate_pdf(html_string)
        return HttpResponse(pdf_file, content_type='application/pdf')

    def _generate_pdf(self, html_string):
        html = HTML(string=html_string, base_url=self.request.build_absolute_uri())
        pdf_file = html.write_pdf(presentational_hints=True)
        return pdf_file

    def form_invalid(self, form):
        messages.error(self.request, 'There were errors.')
        return self.render_to_response(self.get_context_data(form=form))
