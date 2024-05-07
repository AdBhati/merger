from django.db import models
from ..mixins import TimeAuditModel
from zuperscore.db.models.base import User
from zuperscore.db.models.subjects import SubjectNode
from zuperscore.db.models.library import Exam, MegaDomain, Subject, Domain, Topic, SubTopic
from django.conf import settings
from django.db.models.signals import pre_delete
from django.dispatch import receiver

class Question(TimeAuditModel):
    title = models.TextField()
    data = models.JSONField(default=dict)
    is_active = models.BooleanField(default=True)
    files = models.JSONField(default=dict)
    timers = models.JSONField(default=dict)
    assets = models.JSONField(default=dict)
    score = models.IntegerField(default=0)
    explanation = models.JSONField(default=dict)
    feedback = models.TextField(default=dict)
    type = models.CharField(
        max_length=255,
        default="MCQ",
        choices=[("MCQ", "MCQ"), ("FIB", "FIB"), ("TF", "TF"), ("SPR", "SPR")],
    )
    calculator = models.CharField(
        max_length=255, default="", choices=[("", ""), ("yes", "yes"), ("no", "no")]
    )
    parent = models.ForeignKey("self", on_delete=models.CASCADE, null=True, blank=True)
    content = models.JSONField(default=dict)
    passage = models.JSONField(null=True, blank=True)

    approvers_difficulty = models.PositiveSmallIntegerField(default=0)
    statistical_difficulty = models.PositiveSmallIntegerField(default=0)
    # - Class assignments class_assignment = true
    # - Home assignments  home_assignment
    # - Practice tests pratice_test = true
    # - Sectional tests sectional_test = true
    # - Mock tests if mocks every thing else gets unticked (Checked) mock_test = true

    used_in = models.JSONField(default=dict)

    # -1, 0, 1 -> -1 = reject, 0 = pending, 1 = approve

    decision = models.PositiveSmallIntegerField(default=0)

    sourced_from = models.CharField(max_length=255, default="ZUPERSCORE")
    remarks = models.CharField(max_length=255, blank=True)
    irt_a = models.FloatField(default=0)
    irt_b = models.FloatField(default=0)
    irt_c = models.FloatField(default=0)
    weight = models.FloatField(default=1.0)
    # - Memory memory = true
    # - Comprehension comprehension = true
    # - Application application = true
    # - Analysis analysis = true
    # - Synthesis synthesis = true
    # - Judgment judgment = true

    blume_taxonomy = models.JSONField(default=dict)

    # tagging
    exam = models.ForeignKey(
        Exam,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="question_exam",
    )
    subject = models.ForeignKey(
        Subject,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="question_subject",
    )
    mega_domain = models.ForeignKey(
        MegaDomain,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="question_mega_domain",
    )
    domain = models.ForeignKey(
        Domain,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="question_domain",
    )
    topic = models.ForeignKey(
        Topic,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="question_topic",
    )
    sub_topic = models.ForeignKey(
        SubTopic,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="question_sub_topic",
    )

    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="created_questions",
        null=True,
    )

    approved_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="approved_questions",
        null=True,
    )

    class Meta:
        db_table = "questions"
        ordering = ("-created_at",)

class Option(TimeAuditModel):
    question = models.ForeignKey(
        Question, on_delete=models.CASCADE, related_name="options"
    )
    hash = models.CharField(max_length=255)
    data = models.JSONField(default=dict)
    sequence = models.FloatField(default=0)
    assets = models.JSONField(default=dict)

    def __str__(self):
        return self.hash

    class Meta:
        db_table = "options"
        ordering = ("sequence",)


class AssessmentTags(TimeAuditModel):
    name = models.CharField(max_length=255)
    description = models.TextField()
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.name

    class Meta:
        db_table = "assessment_tags"


class Assessment(TimeAuditModel):
    name = models.CharField(max_length=255)
    description = models.JSONField(null=True, blank=True)
    instructions = models.JSONField(null=True, blank=True)
    cover_url = models.TextField(default=dict)
    link = models.TextField(default=dict)
    data = models.JSONField(default=dict)
    kind = models.CharField(
        max_length=255,
        choices=(
            ("MOCK", "MOCK"),
            ("SECTIONAL", "SECTIONAL"),
            ("MICRO", "MICRO"),
            ("PRACTICE_SHEET", "PRACTICE_SHEET"),
            ("DIAGNOSTIC", "DIAGNOSTIC"),
        ),
        default="MOCK",
    )
    assessment_type = models.CharField(
        max_length=255,
        choices=(
            ("STUDENT", "STUDENT"),
            ("TUTOR", "TUTOR"),
            ("EXTENDED", "EXTENDED"),
        ),
        default="STUDENT",
    )
    state = models.CharField(
        max_length=255,
        choices=(
            ("ACTIVE", "ACTIVE"),
            ("ARCHIVED", "ARCHIVED"),
        ),
        default="ACTIVE",
    )
    max_attempts = models.PositiveIntegerField(default=1)

    # is_extended = models.BooleanField(default=False)
    # is_tutor_test = models.BooleanField(default=False)
    exam = models.ForeignKey(
        Exam,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="assessment_exam",
    )
    subject = models.ForeignKey(
        Subject,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="assessment_subject",
    )
    mega_domain = models.ForeignKey(
        MegaDomain,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="assessment_mega_domain",
    )
    domain = models.ForeignKey(
        Domain,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="assessment_domain",
    )
    topic = models.ForeignKey(
        Topic,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="assessment_topic",
    )
    tags = models.ManyToManyField(
        AssessmentTags, blank=True, related_name="assessment_tags"
    )

    english_sigma = models.FloatField(null=True, blank=True)
    english_xbar = models.FloatField(null=True, blank=True)
    math_sigma = models.FloatField(null=True, blank=True)
    math_xbar = models.FloatField(null=True, blank=True)
    # data_downloads = models.JSONField(default=dict)
    assessment_sessions = models.TextField(null=True, blank=True)

    def __str__(self):
        return self.name


class AssessmentSection(TimeAuditModel):
    name = models.CharField(max_length=255, default="DEFAULT")
    description = models.JSONField(default=dict)
    instructions = models.JSONField(default=dict)
    assessment = models.ForeignKey(
        Assessment, related_name="assessment_sections", on_delete=models.CASCADE
    )
    is_timed = models.BooleanField(default=False)
    time_limit = models.IntegerField(default=0)
    tools = models.JSONField(default=dict)
    pre_screen = models.JSONField(default=dict)
    post_screen = models.JSONField(default=dict)
    sequence = models.FloatField(default=0)
    layout = models.JSONField(default=dict)
    data = models.JSONField(default=dict)
    timers = models.JSONField(default=dict)
    bubble_sheet_data = models.JSONField(default=dict)
    bubble_sheet_questions = models.JSONField(default=dict)
    bubble_sheet_answers = models.JSONField(default=dict)
    paragraphs = models.JSONField(default=dict)
    switching_route = models.JSONField(default=dict)
    type = models.CharField(
        max_length=255,
        choices=(
            ("STANDARD", "STANDARD"),
            ("RANDOM", "RANDOM"),
            ("ADAPTIVE", "ADAPTIVE"),
        ),
        default="STANDARD",
    )
    """
    data = [{
        "score": 22,
        "folder_id": 1,
        "operator": "add",
    }]
    """
    def __str__(self):
        return self.name

    class Meta:
        ordering = [
            "sequence",
        ]


class SectionQuestion(TimeAuditModel):

    question = models.ForeignKey(
        Question, on_delete=models.CASCADE, related_name="section_questions"
    )
    section = models.ForeignKey(
        AssessmentSection, related_name="section_questions", on_delete=models.CASCADE
    )
    data = models.JSONField(default=dict)
    blocks = models.JSONField(default=dict)

    questions = models.JSONField(default=dict)
    sequence = models.FloatField(default=0)
    layout = models.JSONField(default=dict)
    order = models.IntegerField(default=0)

    def __str__(self):
        return self.question.title

    class Meta:
        ordering = ("sequence",)


class QuestionNode(TimeAuditModel):
    question = models.ForeignKey(
        Question, on_delete=models.CASCADE, related_name="question_nodes"
    )
    data = models.JSONField(default=dict)
    node = models.ForeignKey(
        SubjectNode,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="question_nodes",
    )
    sequence = models.FloatField(default=0)

    def __str__(self):
        return f"{self.question.id} -> {self.tag.id}"

    class Meta:
        unique_together = ("question", "node")
        ordering = (
            "sequence",
            "created_at",
        )


class UserAssessmentSession(TimeAuditModel):
    assessment = models.ForeignKey(
        Assessment, on_delete=models.CASCADE, related_name="user_assessment_sessions"
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="user_assessment_sessions",
    )
    data = models.JSONField(default=dict)
    is_submitted = models.BooleanField(default=False)
    is_reviewed = models.BooleanField(default=False)
    is_started = models.BooleanField(default=False)
    started_at = models.DateTimeField(null=True, blank=True)
    submitted_at = models.DateTimeField(null=True, blank=True)
    reviewed_at = models.DateTimeField(null=True, blank=True)
    total_time = models.PositiveIntegerField(default=0)
    total_marks = models.PositiveIntegerField(default=0)
    total_questions = models.IntegerField(default=0)
    total_correct = models.IntegerField(default=0)
    total_incorrect = models.IntegerField(default=0)
    total_answered = models.IntegerField(default=0)
    total_unanswered = models.IntegerField(default=0)
    total_visited = models.IntegerField(default=0)
    total_unvisited = models.IntegerField(default=0)
    total_unattempted = models.IntegerField(default=0)
    section_analysis_data = models.JSONField(default=dict)
    total_correct_qids = models.JSONField(default=dict)
    """
    {"section_id": 4, "qid": [1,2,3]"}
    """
    total_incorrect_qids = models.JSONField(default=dict)
    total_unanswered_qids = models.JSONField(default=dict)
    total_visited_qids = models.JSONField(default=dict)
    total_unvisited_qids = models.JSONField(default=dict)
    total_answered_qids = models.JSONField(default=dict)
    is_pscale_success = models.BooleanField(default=False)
    pscale_data = models.JSONField(default=dict)

    section_question_data = models.JSONField(default=dict)
    section_info_data = models.JSONField(default=dict)
    section_time_data = models.JSONField(default=dict)
    section_marks_data = models.JSONField(default=dict)
    generated_by = models.JSONField(null=True, blank=True)
    is_resume_enabled = models.BooleanField(default=False)

    state = models.CharField(
        max_length=255,
        choices=(
            ("UNTOUCHED", "UNTOUCHED"),
            ("STARTED", "STARTED"),
            ("IN_PROGRESS", "IN_PROGRESS"),
            ("COMPLETED", "COMPLETED"),
            ("CANCELLED", "CANCELLED"),
            ("ARCHIVED", "ARCHIVED"),
            ("ANALYSED", "ANALYSED"),
        ),
        default="UNTOUCHED",
    )
    scheduled_at = models.DateTimeField(null=True, blank=True)


class UserAttempt(TimeAuditModel):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="assessment_attempts",
    )
    section = models.ForeignKey(
        AssessmentSection, on_delete=models.CASCADE, related_name="assessment_attempts"
    )
    question = models.ForeignKey(
        Question,
        on_delete=models.CASCADE,
        related_name="assessment_attempts",
        null=True,
        blank=True,
    )
    type = models.CharField(max_length=255, null=True, blank=True)
    is_bookmark = models.BooleanField(default=False)
    data = models.JSONField(default=dict)
    extra = models.JSONField(default=dict)
    info = models.JSONField(default=dict)
    time_taken = models.JSONField(default=dict)
    session = models.ForeignKey(
        UserAssessmentSession,
        on_delete=models.CASCADE,
        related_name="assessment_attempts",
    )
    assessment = models.ForeignKey(
        Assessment, on_delete=models.CASCADE, related_name="assessment_attempts"
    )
    is_visited = models.BooleanField(default=False)
    masked_options = models.JSONField(default=dict)
    is_answered = models.BooleanField(default=False)
    analysis_data = models.JSONField(default=dict)
    stat = models.CharField(
        max_length=255,
        choices=(
            ("ORIGIN", "ORIGIN"),
            ("MIGRATED", "MIGRATED"),
            ("DESKTOP", "DESKTOP"),
        ),
        default="ORIGIN",
    )

    def __str__(self):
        return f"{self.user.id} -> {self.question.id}"


class Group(TimeAuditModel):
    name = models.CharField(max_length=255)
    target_date = models.DateField(null=True)
    status = models.BooleanField(default=False)
    data = models.JSONField(null=True, blank=True)

    def __str__(self):
        return self.name
    class Meta:
        """Meta definition for Group."""

        db_table = "group"


class GroupUser(TimeAuditModel):
    group = models.ForeignKey(
        Group, on_delete=models.CASCADE, null=True, blank=True, related_name="groups"
    )
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, null=True, blank=True, related_name="users"
    )

    def __str__(self):
        return self.group.name

    class Meta:
        """Meta definition for Group User."""

        db_table = "group_user"


class PracticeSet(TimeAuditModel):
    name = models.CharField(max_length=255)
    status = models.BooleanField(default=False)
    data = models.JSONField(null=True, blank=True)

    def __str__(self):
        return self.name
    class Meta:
        """Meta definition for Practice Set."""

        db_table = "practice_set"


class PracticeSetAssessment(TimeAuditModel):
    practice_set = models.ForeignKey(
        PracticeSet,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="practice_set",
    )
    assessment = models.ForeignKey(
        Assessment,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="set_assessment",
    )

    def __str__(self):
        return self.practice_set.name

    class Meta:
        """Meta definition for Practice Set Assessment."""

        db_table = "practice_set_assessment"


class TestAllocationLogger(TimeAuditModel):
    kind = models.CharField(
        max_length=255,
        choices=(
            ("MOCK", "MOCK"),
            ("SECTIONAL", "SECTIONAL"),
            ("MICRO", "MICRO"),
            ("PRACTICE_SHEET", "PRACTICE_SHEET"),
        ),
        default="MOCK",
    )
    assessment = models.ManyToManyField(
        Assessment, related_name="assessments", blank=True
    )
    scheduled_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return self.pk

    class Meta:
        db_table = "test_allocation_logger"


# signal to remove the assessment from assessment list
@receiver(pre_delete, sender=Assessment)
def remove_assessments(sender, instance, **kwargs):
    instance.assessments.clear()


class TestAllocationPracticeSetAssessment(TimeAuditModel):
    test_allocation = models.ForeignKey(
        TestAllocationLogger,
        on_delete=models.CASCADE,
        related_name="test_allocation_set",
    )
    practice_set = models.ForeignKey(
        PracticeSet,
        on_delete=models.CASCADE,
        related_name="test_allocation_practice_set",
    )
    assessment = models.ForeignKey(
        Assessment,
        on_delete=models.CASCADE,
        related_name="test_allocation_set_assessment",
    )

    def __str__(self):
        return self.practice_set.name

    class Meta:
        db_table = "test_allocation_practice_set_assessment"


class TestAllocationGroupUser(TimeAuditModel):
    test_allocation = models.ForeignKey(
        TestAllocationLogger,
        on_delete=models.CASCADE,
        related_name="test_allocation_group_user",
    )
    group = models.ForeignKey(
        Group,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="test_allocation_groups",
    )
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="test_allocation_users",
    )

    def __str__(self):
        return self.group.name

    class Meta:
        db_table = "test_allocation_group_user"


class WeeklyProgress(TimeAuditModel):
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="weekly_progress_user"
    )
    start_date = models.DateField(null=True)
    end_date = models.DateField(null=True)
    progress = models.JSONField(null=True, blank=True)
    core_class = models.IntegerField(default=0)
    doubts_class = models.IntegerField(default=0)
    strategy_class = models.IntegerField(default=0)
    sectional_class = models.IntegerField(default=0)
    reading_articles = models.IntegerField(default=0)
    mock_tests = models.IntegerField(default=0)
    practice_sheet = models.IntegerField(default=0)
    analyse = models.IntegerField(default=0)

    def __str__(self):
        return self.user.username

    class Meta:
        """Meta definition for Weekly Progress."""

        db_table = "weekly_progress"
