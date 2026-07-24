from django.db import models
from django.utils.translation import gettext_lazy as _


class Currency(models.TextChoices):
    UAH = "UAH", _("Ukrainian Hryvnia")
    USD = "USD", _("US Dollar")
    EUR = "EUR", _("Euro")