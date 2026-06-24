from django.db import models

# Create your models here.
class SearchHistory(models.Model):
    email = models.EmailField(max_length=254, null=False, blank=False)
    search_information = models.JSONField()
    created_at = models.DateTimeField(auto_now_add=True)