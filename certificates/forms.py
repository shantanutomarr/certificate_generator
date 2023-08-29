from django import forms

from certificates.models import CertificateTemplate

class CertificateTemplateForm(forms.ModelForm):
    class Meta:
        model = CertificateTemplate
        fields = ['name', 'zip_file']


class CertificateContextForm(forms.Form):
    recepient_name = forms.CharField(max_length=30, initial="Shantanu Tomar")
    title = forms.CharField(max_length=50, initial="Certificate of Completion")
    description = forms.CharField(
        max_length=170,
        initial=(
            "Recognizing your dedication, hard work, and commitment to mastering web development fundamentals. "
            "We commend you for your outstanding performance in completing the course"
        ),
        widget=forms.widgets.Textarea,
    )
    course_title = forms.CharField(max_length=50, initial="Fundamentals Of Web Development")

    class Meta:
        fields = ['recepient_name', 'title', "description", "course_title"]
