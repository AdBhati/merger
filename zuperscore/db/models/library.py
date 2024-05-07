import os
from django.db import models

from zuperscore.db.models.base import User
from ..mixins import TimeAuditModel


def get_file_upload_path(instance, filename):
    return os.path.join(f"{instance.context}", filename)

class ActiveManager(models.Manager):

    def get_queryset(self, *args, **kwargs):
        return super().get_queryset(*args, **kwargs).filter(
            is_active=True
        )


class FileAsset(TimeAuditModel):
    asset = models.FileField(upload_to=get_file_upload_path)
    attributes = models.JSONField(blank=True, default=dict)
    context = models.CharField(max_length=255, choices=(
        ("library", "Library"), 
        ("exams", "Exams"), 
        ("subjects", "Subjects"),
        ("users", "users"),
        ("sessions", "sessions")

    ), 
    default="library")

    class Meta:
        """Meta definition for FileAsset."""

        verbose_name = "File Asset"
        verbose_name_plural = "File Assets"
        db_table = "library_assets"


class Exam(TimeAuditModel):
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)

    def __str__(self):
        return self.name

    class Meta:
        """Meta definition for Exam."""

        verbose_name = "Exam"
        verbose_name_plural = "Exams"
        db_table = "exams"


class Subject(TimeAuditModel):
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    mega_domain = models.BooleanField(default=False)
    exam = models.ForeignKey(Exam, on_delete=models.CASCADE, related_name="subjects")
    

    def __str__(self):
        return self.name

    class Meta:
        """Meta definition for Subject."""

        verbose_name = "Subject"
        verbose_name_plural = "Subjects"
        db_table = "subjects"


class MegaDomain(TimeAuditModel):
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    sequence = models.IntegerField(default=0)
    is_active = models.BooleanField(default=True)
    subject = models.ForeignKey(
        Subject,
        on_delete=models.CASCADE,
        related_name="mega_domains",
        null=True,
        blank=True,
    )

    def __str__(self):
        return self.name

    class Meta:
        """Meta definition for Mega Domain."""

        verbose_name = "MegaDomain"
        verbose_name_plural = "MegaDomains"
        db_table = "mega_domains"


class SessionPlan(TimeAuditModel):
    name = models.CharField(max_length=255)
    description = models.TextField(null=True, blank=True)
    is_active = models.BooleanField(default=True)
    sequence = models.IntegerField(default=0)
    subject = models.ForeignKey(
        Subject, on_delete=models.CASCADE, related_name="session_plan", null=True,
        blank=True,
    )
    mega_domain = models.ForeignKey(
        MegaDomain, on_delete=models.CASCADE, related_name="session_plan", null=True,
        blank=True,
    )
    

    def __str__(self):
        return self.name


    class Meta:
        """Meta definition for SessionPlan."""

        verbose_name = "SessionPlan"
        verbose_name_plural = "SessionPlans"
        db_table = "session_plan"


class Module(TimeAuditModel):
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    sequence = models.IntegerField(default=0)
    is_active = models.BooleanField(default=True)
    session_plan = models.ForeignKey(
        SessionPlan,
        on_delete=models.CASCADE,
        related_name="modules",
        null=True,
        blank=True,
    )
    mega_domain = models.ForeignKey(
        MegaDomain,
        on_delete=models.CASCADE,
        related_name="modules",
        null=True,
        blank=True,
    )

    def __str__(self):
        return self.name

    class Meta:
        """Meta definition for Module."""

        verbose_name = "Module"
        verbose_name_plural = "Modules"
        db_table = "modules"


class Domain(TimeAuditModel):
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    sequence = models.IntegerField(default=0)
    is_active = models.BooleanField(default=True)
    subject = models.ForeignKey(
        Subject, on_delete=models.CASCADE, related_name="domains",null=True, blank=True
    )
    module = models.ForeignKey(
        Module, on_delete=models.CASCADE, related_name="domains", null=True, blank=True
    )
    mega_domain = models.ForeignKey(
        MegaDomain, on_delete=models.CASCADE, related_name="domains", null=True
    )

    def __str__(self):
        return self.name

    class Meta:
        """Meta definition for Domain."""

        verbose_name = "Domain"
        verbose_name_plural = "Domains"
        db_table = "domains"


class Topic(TimeAuditModel):
    objects = ActiveManager()
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    sequence = models.IntegerField(default=0)
    is_active = models.BooleanField(default=True)
    domain = models.ForeignKey(Domain, on_delete=models.CASCADE, related_name="topics", null=True, blank=True)

    def __str__(self):
        return self.name

    class Meta:
        """Meta definition for Topic."""

        verbose_name = "Topic"
        verbose_name_plural = "Topics"
        db_table = "topics"


class SubTopic(TimeAuditModel):
    objects = ActiveManager()
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    sequence = models.IntegerField(default=0)
    is_active = models.BooleanField(default=True)
    practice_sheet = models.URLField(blank=True, null=True)
    topic = models.ForeignKey(Topic, on_delete=models.CASCADE, related_name="subtopics", null=True, blank=True)


    def __str__(self):
        return self.name

    class Meta:
        """Meta definition for SubTopic."""

        verbose_name = "SubTopic"
        verbose_name_plural = "SubTopics"
        db_table = "subtopics"


class Molecule(TimeAuditModel):

    # objects = ActiveManager()
    title = models.CharField(max_length=100,null=True)
    subject = models.ForeignKey(Subject,on_delete=models.CASCADE,related_name="subject_id")
    mega_domain = models.ForeignKey(MegaDomain,on_delete=models.CASCADE,related_name="mega_domain_id")
    domain = models.ForeignKey(Domain,on_delete=models.CASCADE,related_name="domain_id")
    is_active = models.BooleanField(default=True)
    sequence = models.IntegerField(default=0)


class MoleculeTopicSubtopic(TimeAuditModel):

    molecule = models.ForeignKey(Molecule,on_delete=models.CASCADE,related_name="moleculetopicsubtopic_id")
    topic = models.ForeignKey(Topic,on_delete=models.CASCADE,null=True, blank=True, related_name="moleculetopicsubtopic_id")
    subtopic = models.ForeignKey(SubTopic,on_delete=models.CASCADE,null=True, blank=True,related_name="moleculetopicsubtopic_id")

    class Meta:
        """Meta definition for MoleculeTopicSubtopic."""

        verbose_name = "MoleculeTopicSubtopic"
        verbose_name_plural = "MoleculeTopicSubtopics"
        db_table = "molecule_topic_subtopic"


class Assignment(TimeAuditModel):
    objects = ActiveManager()
    name = models.TextField(blank=True)
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    marks = models.IntegerField(default=0)
    type = models.CharField(
        max_length=255,
        default="PRACTICE_SHEET",
        choices=[("HOME", "HOME"), ("CLASS", "CLASS"),("PRACTICE_SHEET","PRACTICE_SHEET"),("CPEA_R1","CPEA_R1"),("CPEA_R2","CPEA_R2"),("CPEA_R3","CPEA_R3"),("CPEA_W1","CPEA_W1"),("CPEA_W2","CPEA_W2"),("CPEA_W3","CPEA_W3"),("CPEA_M1","CPEA_M1"),("CPEA_M2","CPEA_M2"),("CPEA_M3","CPEA_M3")], 
    )
    
    subTopic = models.ForeignKey(
        SubTopic,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="assignments",
    )

    category = models.CharField(
        max_length=20,
        choices=(
            ("r", "R"),
            ("s", "S"),
            ("t", "T"),
        ),
        default="r",
    )
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE, null=True, blank=True, related_name="subjects")
    sequence = models.IntegerField(default=0)
    pdf_url =  models.URLField(blank=True, null=True)

    def __str__(self):
        return self.name

    class Meta:
        """Meta definition for Assignment."""

        verbose_name = "Assignment"
        verbose_name_plural = "Assignments"
        db_table = "assignment"


class AssignmentQuestion(TimeAuditModel):
    objects = ActiveManager()
    name = models.TextField(blank=True)
    passage = models.TextField(blank=True)
    # description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    # marks = models.IntegerField(default=0)
    sequence = models.IntegerField(default=0)
    explanation = models.TextField(blank=True)
    remarks = models.TextField(blank=True)
    type = models.CharField(
        max_length=255,
        default="MCQ",
        choices=[("MCQ", "MCQ"), ("FIB", "FIB"), ("TF", "TF"), ("SPR", "SPR")],
    )
    assignment = models.ForeignKey(
        Assignment, on_delete=models.CASCADE, related_name="assignment_questions"
    )
    enter_your_answer = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.name

    class Meta:
        """Meta definition for AssignmentQuestion."""

        verbose_name = "AssignmentQuestion"
        verbose_name_plural = "AssignmentQuestions"
        db_table = "assignment_question"



class QuestionOption(TimeAuditModel):
    objects = ActiveManager()
    name = models.TextField(blank=True)
    # description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    is_correct = models.BooleanField(default=False)
    sequence = models.IntegerField(default=0)
    questions = models.ForeignKey(
        AssignmentQuestion, on_delete=models.CASCADE, related_name="question_options"
    )

    def __str__(self):
        return self.name

    def active(self):
        return self.filter(is_active=True)

    class Meta:
        """Meta definition for QuestionOption."""

        verbose_name = "QuestionOption"
        verbose_name_plural = "QuestionOptions"
        db_table = "question_option"


class ReasonForError(TimeAuditModel):
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    topic = models.ForeignKey(
        Topic, on_delete=models.CASCADE, related_name="reason_for_error"
    )

    def __str__(self):
        return self.name

    class Meta:
        """Meta definition for ReasonForError."""

        verbose_name = "ReasonForError"
        verbose_name_plural = "ReasonForErrors"
        db_table = "reason_for_errors"


class SingletonModel(models.Model):
    class Meta:
        abstract = True

    def save(self, *args, **kwargs):
        self.pk = 1
        super(SingletonModel, self).save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        pass

    @classmethod
    def load(cls):
        obj, created = cls.objects.get_or_create(pk=1)
        return obj

class Settings(SingletonModel):
    disabled_mistake_analyzer = models.BooleanField(default=False)

    def __str__(self):
        return "<Zuperscore>"


class MotherSessionMolecule(TimeAuditModel):
    name = models.CharField(max_length=255, default='Session Plan')
    description = models.TextField(null=True, blank=True)
    molecule = models.ForeignKey(Molecule,on_delete=models.CASCADE,null=True,
        blank=True,related_name="mother_session_molecule_id")
    session_plan = models.ForeignKey(SessionPlan,on_delete=models.CASCADE,null=True,
        blank=True, related_name='mother_session_molecule_id')
    

class CpeaReport(TimeAuditModel):
    cpea_question =  models.CharField(max_length=150)
    mega_domain = models.ForeignKey(MegaDomain, on_delete=models.CASCADE, related_name='cpea_report_mega_domian')
    remedial_action = models.CharField(max_length=150, blank=True, null=True)
    
    class Meta:
        verbose_name = "CPEA Report"
        verbose_name_plural = "CPEA Reports"
        db_table = "cpea_reports"

class TutorAvailability(TimeAuditModel):
    tutor = models.ForeignKey(User, on_delete=models.CASCADE, related_name='tutor_availability')
    slot = models.IntegerField(default=0)
    total_week_supply = models.IntegerField(default=0)
    total_weekly_load = models.IntegerField(default=0)
    remaining_weekly_supply = models.IntegerField(default=0)
    total_monthly_load = models.IntegerField(default=0)
    

    
    class Meta:
        db_table='tutor_availablity'

    
