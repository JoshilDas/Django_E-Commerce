from django.db import models


class BaseModel(models.Model):
    """
    Abstract base model providing common timestamp fields.
    All domain models should inherit from this class.
    """

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True

class SoftDeleteModel(BaseModel):
    """
    Adds soft delete capability.
    Records are not physically removed from the database.
    """

    is_active = models.BooleanField(default=True)

    class Meta:
        abstract = True