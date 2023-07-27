from __future__ import unicode_literals

from django.shortcuts import render
from django.template.loader import render_to_string

from django.http import HttpResponse
from django.contrib.staticfiles.templatetags.staticfiles import static

from weasyprint import HTML


def get_certificate_context():
    return {
        'recipient': "Shantanu Tomar",
        'issue_date': "January 23, 2023",
        "certificate_id": "DEMO23423",
        "title": "Certificate Of Completion",
        "description": (
            "Recognizing your dedication, hard work, and commitment to mastering web development fundamentals."
            "We commend you for your outstanding performance in completing the course"
        ),
        "course_title": "Fundamentals Of Web Development",
        "company_logo": static("images/company_logo.png"),
        "background_image": static("images/background.png"),
        "signature_1": {
            "name": "Rakesh Asthana",
            "title": "Director"
        },
        "signature_2": {
            "name": "Abhilasha Jain",
            "title": "Manager"
        },
    }

def render_certificate(request):
    template = 'certificate.html'
    return render(request, template, get_certificate_context())


def generate_certificate_pdf(request):
    template = 'certificate.html'
    html_string = render_to_string(template, get_certificate_context())
    html = HTML(string=html_string, base_url=request.build_absolute_uri())
    pdf_file = html.write_pdf(presentational_hints=True)
    response = HttpResponse(pdf_file, content_type='application/pdf')
    return response
