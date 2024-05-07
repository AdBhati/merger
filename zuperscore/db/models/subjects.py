from django.db import models
from ..mixins import TimeAuditModel
from treebeard.mp_tree import MP_Node


class SubjectNode(MP_Node, TimeAuditModel):
    SUBJECT_TYPE_CHOICES = (
        ('subject', 'Subject'),
        ('topic', 'Topic'),
    )
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    props = models.JSONField(null=True)
    is_active = models.BooleanField(default=False)
    kind = models.CharField(max_length=255, choices=SUBJECT_TYPE_CHOICES)
    data = models.JSONField(null=True)
    visible = models.BooleanField(default=True)
    state = models.CharField(
        max_length=255,
        choices=(
            ("ACTIVE","ACTIVE"),
            ("ARCHIVED","ARCHIVED"),
        ), 
        default="ACTIVE",
    )

    def __str__(self):
        return self.title