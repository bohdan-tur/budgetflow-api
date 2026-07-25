from django.db import models
from django.conf import settings
from .choices import CategoryType


class Category(models.Model):

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="categories",
    )


    name = models.CharField(max_length=100)

    type = models.CharField(
        max_length=7,
        choices=CategoryType.choices,
        default=CategoryType.EXPENSE,
    )


    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["user", "name","type"],
                name="unique_category_name_per_user",
            )
        ]
        ordering = ["name"]

    def __str__(self):
        return self.name