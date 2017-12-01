from django.db import models


class Document(models.Model):
    nit = models.CharField(max_length=15, default='No detect')
    file = models.FileField(upload_to='input')
    uploaded_at = models.DateTimeField(auto_now_add=True)
