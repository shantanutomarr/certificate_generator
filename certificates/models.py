from django.db import models
from django.template.defaultfilters import slugify


class CertificateTemplate(models.Model):
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=255, unique=True, blank=True)
    zip_file = models.FileField(upload_to='certificate_templates/')
    parsed_html = models.TextField(null=True, blank=True)

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super(CertificateTemplate, self).save(*args, **kwargs)
