import os
import six
import chardet
import cssutils
import uuid
import zipfile
from bs4 import BeautifulSoup
from django.conf import settings
from django.contrib.staticfiles.templatetags.staticfiles import static


class TemplateZipParser(object):
    """Parses template from a ZIP file and returns a single standalone HTML string."""

    def __init__(self, zip_path, destination_folder):
        self.zip_path = zip_path
        self.folder = destination_folder

    def parse(self):
        self.unzip_to_folder()
        soup = self.get_template_soup()
        soup = self.convert_relative_file_paths_to_absolute(soup)
        soup = self.upload_embedded_files(soup)
        return str(soup)
    
    def unzip_to_folder(self):
        with zipfile.ZipFile(self.zip_path, 'r') as zip_ref:
            zip_ref.extractall(self.folder)

    def get_template_soup(self):
        html_file, self.folder = self.get_html_file_from_folder()
        html_file_content = self.read_and_encode_html(html_file)
        return BeautifulSoup(html_file_content, "html.parser")

    def get_html_file_from_folder(self):
        for root, dirs, files in os.walk(self.folder):
            for filename in files:
                if filename.endswith(".htm") or filename.endswith(".html"):
                    new_folder = os.path.dirname(os.path.join(root, filename)) + "/"
                    return os.path.join(root, filename), new_folder

    def read_and_encode_html(self, html_file):
        html_file_content = open(html_file, "rb").read()
        encoding = chardet.detect(html_file_content)["encoding"]
        if encoding != "utf-8":
            return html_file_content.decode("Windows-1252").encode("utf-8")
        return six.text_type(html_file_content, errors="ignore")

    def convert_relative_file_paths_to_absolute(self, soup):
        relative_path_processor = RelativeToAbsolutePathConverter(soup, self.folder)
        return relative_path_processor.run()

    def upload_embedded_files(self, soup):
        return EmbeddedFileUploader(soup).run()


class RelativeToAbsolutePathConverter(object):
    """Converts local relative paths to local absolute paths in HTML."""

    def __init__(self, soup, directory=""):
        self.soup = soup
        self.directory = directory

    def run(self):
        self.clean()
        return self.soup

    def clean(self):
        self.update_element_attribute("img", "src")
        self.update_element_attribute("link", "href")
        self.update_css()

    def update_element_attribute(self, tag, attr):
        for element in self.soup.findAll(tag):
            attribute_value = element.get(attr)
            if self.is_relative_url(attribute_value):
                element[attr] = self.create_absolute_path(attribute_value)

    def update_css(self):
        for style in self.soup.findAll("style"):
            sheet = cssutils.parseString(style.string)
            for rule in sheet:
                if rule.type == rule.FONT_FACE_RULE:
                    self.process_font_face_rule(rule)

            style.string = sheet.cssText

    def process_font_face_rule(self, rule):
        src_value = rule.style.getPropertyValue('src')
        if "url(" in src_value:
            src_value = src_value.lstrip("url(").rstrip(")")
            if self.is_relative_url(src_value):
                new_src_value = "url('{}')".format(self.create_absolute_path(src_value))
                rule.style.setProperty("src", new_src_value)

    def is_relative_url(self, url):
        return url and not (url.startswith("http") or url.startswith("data:"))

    def create_absolute_path(self, relative_path):
        return "{}{}".format(self.directory, relative_path)


class EmbeddedFileUploader(object):
    """Uploads embedded local files to cloud storage and replaces source URLs in HTML."""

    def __init__(self, soup):
        self.soup = soup

    def run(self):
        destination = "{}/certificates".format(settings.STATIC_ROOT)
        self.process_elements("img", "src", destination)
        self.process_elements("link", "href", destination)
        self.process_css(destination)
        return self.soup

    def process_elements(self, tag, attr, destination):
        for element in self.soup.findAll(tag):
            if element.get(attr):
                element[attr] = self.upload_file(element[attr], destination)

    def process_css(self, destination):
        for style in self.soup.findAll("style"):
            sheet = cssutils.parseString(style.string)
            for rule in sheet:
                if rule.type == rule.FONT_FACE_RULE:
                    self.process_font_face_rule(rule, destination)

            style.string = sheet.cssText

    def process_font_face_rule(self, rule, destination):
        src_value = rule.style.getPropertyValue('src')
        if "url(" in src_value:
            src_value = src_value.lstrip("url(").rstrip(")")
            new_src_value = "url('{}')".format(self.upload_file(src_value, destination))
            rule.style.setProperty("src", new_src_value)

    def upload_file(self, source, destination):
        if source and "http" not in source:
            return FileUploader(source, destination).process()
        return source


class FileUploader(object):
    """Uploads files to a destination folder."""

    def __init__(self, source, destination):
        self.source = source
        self.destination = destination
        self.file_name = "{}.{}".format(uuid.uuid4().hex, self.extension)

    def process(self):
        self.source = self.clean_source()
        self.upload()
        return static("certificates/{}".format(self.file_name))

    def clean_source(self):
        return self.source

    @property
    def extension(self):
        return self.source.split(".")[-1].lower()

    def upload(self):
        file_stream = open(self.source, "rb")
        chunk_size = 52428800  # 50MB
        image = self.open()
        chunk = file_stream.read(chunk_size)
        while len(chunk) > 0:
            image.write(chunk)
            chunk = file_stream.read(chunk_size)
        image.close()

    @property
    def upload_path(self):
        return u"{}/{}".format(self.destination, self.file_name)

    def open(self):
        return open(self.upload_path, "w")
