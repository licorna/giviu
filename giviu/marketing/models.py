from __future__ import unicode_literals
from django.db import models


class EmailTemplate(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=30)
    html_template = models.CharField(max_length=40)
    text_template = models.CharField(max_length=40)
    subject = models.CharField(max_length=64)
