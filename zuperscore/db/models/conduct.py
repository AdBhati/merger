from datetime import datetime
from django.db import models
from django.db.models import JSONField
from django.utils import timezone

from zuperscore.db.models.assessments import Question
from ..mixins import TimeAuditModel, UserAuditModel
from django.conf import settings
from zuperscore.db.models.base import User
from zuperscore.db.models.library import (
    Molecule,
    Subject,
    MegaDomain,
    SessionPlan,
    Module,
    Domain,
    Topic,
    SubTopic,
    Assignment,
    AssignmentQuestion,
    QuestionOption,
)


# Mother Session Master Tables
class StudentSessionPlan(TimeAuditModel):
    name = models.CharField(max_length=255)
    description = models.TextField(null=True)
    is_active = models.BooleanField(default=True)
    category = models.CharField(
        max_length=20,
        choices=(
            ("r", "R"),
            ("s", "S"),
            ("t", "T"),
        ),
        default="r",
    )
    subject = models.ForeignKey(
        Subject, on_delete=models.CASCADE, null=True, blank=True, related_name="student_session_plan"
    )
    mega_domain = models.ForeignKey(
        MegaDomain, on_delete=models.CASCADE, null=True, blank=True, related_name="student_session_plan"
    )
    student = models.ForeignKey(
        User, on_delete=models.CASCADE, null=True, blank=True, related_name="student_session_plan"
    )
    session_plan = models.ForeignKey(
        SessionPlan, on_delete=models.CASCADE, null=True, blank=True, related_name="student_session_plan"
    )
    corePrep = models.DateField(null=True)
    targetTest = models.DateField(null=True)

    class Meta:
        """Meta definition for StudentSessionPlan."""

        verbose_name = "StudentSession"
        verbose_name_plural = "StudentSessions"
        db_table = "student_session"


class StudentModule(TimeAuditModel):
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    student_session = models.ForeignKey(
        StudentSessionPlan, on_delete=models.CASCADE, related_name="student_module", null=True, blank=True
    )
    module = models.ForeignKey(Module, on_delete=models.CASCADE, related_name="student_module", null=True, blank=True)
    student = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True, related_name="student_module")
    sequence = models.IntegerField(default=0)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.name

    class Meta:
        """Meta definition for StudentModule."""

        verbose_name = "StudentModule"
        verbose_name_plural = "StudentModules"
        db_table = "student_module"


class StudentDomain(TimeAuditModel):
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    sequence = models.IntegerField(default=0)
    is_active = models.BooleanField(default=True)
    student = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True, related_name="student_domain")
    domain = models.ForeignKey(Domain, on_delete=models.CASCADE, related_name="student_domain", null=True, blank=True)
    student_session = models.ForeignKey(
        StudentSessionPlan, on_delete=models.CASCADE, related_name="student_session", null=True, blank=True
    )
    # mega_domain = models.ForeignKey(
    #     MegaDomain, on_delete=models.CASCADE, related_name="student_megadomain", null=True, blank=True
    # )

    def __str__(self):
        return self.name

    class Meta:
        """Meta definition for StudentDomain."""

        verbose_name = "StudentDomain"
        verbose_name_plural = "StudentDomains"
        db_table = "student_domain"


class StudentTopic(TimeAuditModel):
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    sequence = models.IntegerField(default=0)
    is_active = models.BooleanField(default=True)
    student_domain = models.ForeignKey(StudentDomain, on_delete=models.CASCADE, related_name="student_topic")
    student = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True, related_name="student_topic")
    topic = models.ForeignKey(Topic, on_delete=models.CASCADE, null=True, blank=True, related_name="student_topic")
    # mega_domain = models.ForeignKey(
    #     MegaDomain, on_delete=models.CASCADE, related_name="student_megadomain", null=True, blank=True
    # )

    def __str__(self):
        return self.name

    class Meta:
        """Meta definition for StudentTopic."""

        verbose_name = "StudentTopic"
        verbose_name_plural = "StudentTopics"
        db_table = "student_topic"


class StudentSubTopic(TimeAuditModel):
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    content = models.TextField(blank=True)
    sequence = models.IntegerField(default=0)
    is_active = models.BooleanField(default=True)
    is_extra = models.BooleanField(default=False)
    time = models.CharField(max_length=20, default="15")
    student_topic = models.ForeignKey(StudentTopic, on_delete=models.CASCADE, related_name="student_subtopic")
    student = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True, related_name="student_subtopic")
    sub_topic = models.ForeignKey(
        SubTopic, on_delete=models.CASCADE, null=True, blank=True, related_name="student_subtopic"
    )
    practice_sheet = models.URLField(blank=True, null=True)
    # mega_domain = models.ForeignKey(
    #     MegaDomain, on_delete=models.CASCADE, related_name="student_megadomain", null=True, blank=True
    # )

    def __str__(self):
        return self.name

    class Meta:
        """Meta definition for StudentSubTopic."""

        verbose_name = "StudentSubTopic"
        verbose_name_plural = "StudentSubTopics"
        db_table = "student_subtopic"


class StudentAssignment(TimeAuditModel):
    name = models.TextField(blank=True)
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    marks = models.IntegerField(default=0)
    type = models.CharField(
        max_length=255,
        default="CLASS",
        choices=[("HOME", "HOME"), ("CLASS", "CLASS")],
    )
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE,null = True, blank=True, related_name="student_assignments")
    megadomain = models.ForeignKey(MegaDomain, on_delete=models.CASCADE,null = True, blank=True,related_name="student_assignments")
    domain = models.ForeignKey(Domain, on_delete=models.CASCADE,null = True, blank=True, related_name="student_assignments")
    module = models.ForeignKey(Module, on_delete=models.CASCADE,null = True, blank=True, related_name="student_assignments")
    topic = models.ForeignKey(Topic, on_delete=models.CASCADE,null = True, blank=True, related_name="student_assignments")
    subtopic = models.ForeignKey(SubTopic, on_delete=models.CASCADE,null = True, blank=True, related_name="student_assignments")
    student = models.ForeignKey(
        User, on_delete=models.CASCADE, null=True, blank=True, related_name="student_assignments"
    )
    assignment = models.ForeignKey(
        Assignment, on_delete=models.CASCADE, null=True, blank=True, related_name="student_assignments"
    )
    is_visible = models.BooleanField(default=False)
    is_completed = models.BooleanField(default=False)

    def __str__(self):
        return self.name

    class Meta:
        """Meta definition for StudentAssignment."""

        verbose_name = "StudentAssignment"
        verbose_name_plural = "StudentAssignments"
        db_table = "student_assignment"


class StudentAssignmentQuestion(TimeAuditModel):
    name = models.TextField(blank=True)
    passage = models.TextField(blank=True)
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    marks = models.IntegerField(default=0)
    sequence = models.IntegerField(default=0)
    type = models.CharField(
        max_length=255,
        default="MCQ",
        choices=[("MCQ", "MCQ"), ("FIB", "FIB"), ("TF", "TF"), ("SPR", "SPR")],
    )
    student = models.ForeignKey(
        User, on_delete=models.CASCADE, null=True, blank=True, related_name="student_assignment_questions"
    )
    student_assignment = models.ForeignKey(
        StudentAssignment, on_delete=models.CASCADE, null=True, blank=True, related_name="student_assignment_questions"
    )
    

    assignment_question = models.ForeignKey(
        AssignmentQuestion,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="student_assignment_questions",
    )

    def __str__(self):
        return self.name

    class Meta:
        """Meta definition for StudentAssignmentQuestion."""

        verbose_name = "StudentAssignmentQuestion"
        verbose_name_plural = "StudentAssignmentQuestions"
        db_table = "student_assignment_question"


class StudentQuestionOption(TimeAuditModel):
    name = models.TextField(blank=True)
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    is_correct = models.BooleanField(default=False)
    sequence = models.IntegerField(default=0)
    student_assignment_question = models.ForeignKey(
        StudentAssignmentQuestion,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="student_question_options",
    )
    student = models.ForeignKey(
        User, on_delete=models.CASCADE, null=True, blank=True, related_name="student_question_options"
    )
    question_option = models.ForeignKey(
        QuestionOption, on_delete=models.CASCADE, null=True, blank=True, related_name="student_question_options"
    )

    def __str__(self):
        return self.name

    class Meta:
        """Meta definition for StudentQuestionOption."""

        verbose_name = "StudentQuestionOption"
        verbose_name_plural = "StudentQuestionOptions"
        db_table = "student_question_option"

    


class Appointments(TimeAuditModel):
    host = models.ForeignKey(User, on_delete=models.CASCADE, related_name="host", null=False)  # tutor
    subject = models.ForeignKey(
        Subject, on_delete=models.CASCADE, null=True, blank=True, related_name="app_subject"
    )  # response
    created_by_ip = models.CharField(max_length=20, null=True)
    updated_by_ip = models.CharField(max_length=20, null=True)
    is_active = models.BooleanField(default=True)
    type = models.CharField(max_length=50, null=True)  
    is_completed = models.BooleanField(default=False)
    appointment_time = timezone.now()  
    zoom_link = models.TextField(null=True)  # response
    title = models.CharField(max_length=255, null=True)
    # start_at = models.CharField(max_length=50, null=True)
    # end_at = models.CharField(max_length=50, null=True)
    start_at = models.DateTimeField(null=True, blank=True)
    end_at = models.DateTimeField(null=True, blank=True)
    duration = models.CharField(max_length=50, null=True)
    timezone = models.CharField(max_length=50, null=True)
    booking = models.CharField(max_length=100,null=True)
    student = models.ForeignKey(User, on_delete=models.CASCADE, related_name="student", null=True)
    invitee_email = models.CharField(max_length=255, default=None, null=True)
    resource_id = models.CharField(max_length=100,null=True)
    invitee_id = models.IntegerField(default=0)
    invitee_name = models.CharField(max_length=255, null=True)
    ds_host_id = models.CharField(max_length=255, null=True)
    host_name = models.CharField(max_length=255, null=True)
    mega_domain = models.CharField(max_length=255, null=True)
    

    class Meta:
        db_table = "appointment"
        # ordering = ("-created")

class Attendee(TimeAuditModel):
    appointment = models.ForeignKey(Appointments, on_delete=models.CASCADE, related_name="appointments")
    attendee = models.ForeignKey(User, on_delete=models.CASCADE, null=False)
    type = models.CharField(max_length=50)
    join_time = timezone.now()

    class Meta:
        db_table = "attendee"

#created by suresh
class Booking(TimeAuditModel):
    invitee_name = models.CharField(max_length=255)
    invitee_email = models.EmailField(max_length=100)
    start_at = models.CharField(max_length=100, null=True)
    resource_id = models.CharField(max_length=100,null=True)
    invitee_id=models.IntegerField(default=0)
    booking = models.CharField(max_length=100,null=True)

    class Meta:
        db_table = "bookings"


class StudentAvailability(TimeAuditModel):
    start_date = models.DateField(null=True)
    end_date = models.DateField(null=True)
    type = models.CharField(max_length=100,null=True)
    target_test_date_1 = models.DateField(null=True)
    target_test_date_2 = models.DateField(null=True)
    target_test_date_3 = models.DateField(null=True)
    target_test_date_4 = models.DateField(null=True)
    core_prep_date = models.DateField(null=True)
    student = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True, related_name="student_availablity")
    total_days=models.IntegerField(default=0)

    class Meta:
        db_table = "student_availability"
        

class AppointmentMolecule(TimeAuditModel):
    molecule = models.ForeignKey(Molecule, on_delete=models.CASCADE,null=True, related_name="molecule")
    appointment = models.ForeignKey(Appointments, on_delete=models.CASCADE, null=True, related_name="appointment") 
    is_completed = models.BooleanField(default=False)
    
class Meta:
    db_table = "appointment_molecule"


class FeedBack(TimeAuditModel):
    comment = models.CharField(max_length=500)
    student = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True, related_name="stundet_comment")
    tutor = models.ForeignKey(User, on_delete = models.CASCADE, null=True, blank=True, related_name="tutor_comment")
    commenter = models.CharField(max_length=255)
    appointment = models.ForeignKey(Appointments, on_delete=models.CASCADE, null=True, blank=True, related_name="appointments_feedback")
    # feedback_question_ratings = models.CharField(max_length=500)

    class Meta:
        db_table = "feedbacks"


class FeedbackQuestions(TimeAuditModel):
    question = models.CharField(max_length=500)
    is_active = models.BooleanField(default=False)
    
    USER_TYPE = (
        ("student","Student"),
        ("tutor","Tutor"),
    )
    type = models.CharField(max_length=64, choices=USER_TYPE, default="student")

    class Meta:
        db_table = "feedback_questions"


class FeedbackQuestionRating(TimeAuditModel):
    feedback = models.ForeignKey(FeedBack, on_delete=models.CASCADE, related_name='question_ratings')
    question = models.ForeignKey(FeedbackQuestions, on_delete=models.CASCADE)
    rating = models.IntegerField()  

    class Meta:
        db_table = 'feedback_question_ratings'


class StudentCpeaReport(TimeAuditModel):
    STATUS_CHOICES = [
        ('Pass', 'Pass'),
        ('Fail', 'Fail'),
        ('Result_Awaited', 'Result_Awaited'),
    ]
    student = models.ForeignKey(User, on_delete=models.CASCADE, related_name='cpea_reports')
    tutor = models.ForeignKey(User, on_delete=models.CASCADE, related_name='cpea_tutor_reports')
    appointment = models.ForeignKey(Appointments, on_delete=models.CASCADE)
    assignment = models.ForeignKey(Assignment, on_delete=models.CASCADE, default=None, null=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default= 'Result_Awaited')
    answers = JSONField(default=dict)
    overall_feedback = models.CharField(max_length=500, default=None, null=True)
    is_student_view = models.BooleanField(default=False)

    class Meta:
        db_table ='student_cpea_reports'


class StudentTeam(TimeAuditModel):
    TYPE_CHOICE = [
        ('PRIMARY', 'Primary'),
        ('SECONDARY', 'Secondary'),
    ]
    student = models.ForeignKey(User, on_delete=models.CASCADE, related_name='students')
    tutor = models.ForeignKey(User, on_delete=models.CASCADE, related_name='tutors')
    type = models.CharField(max_length=20, choices=TYPE_CHOICE)
    is_active_tutor= models.BooleanField(default=False)

    class Meta:
        db_table = 'student_teams'

class StudentGroupEvents(TimeAuditModel):
    sso = models.ForeignKey(User, on_delete=models.CASCADE,related_name='sso')
    deptHead = models.ForeignKey(User, on_delete=models.CASCADE,related_name='deptHead')
    event_id = models.CharField(max_length=100)
    student = models.ForeignKey(User, on_delete=models.CASCADE, related_name='StudentGroupEvents')
    class_name = models.CharField(max_length=500, default=None, null=True)
    tutor_name = models.CharField(max_length=100)
    tutor = models.ForeignKey(User, on_delete=models.CASCADE, related_name='StudentGroupEventTutor')
    subject = models.CharField(max_length=100)
    is_taken = models.BooleanField(default=False, null=True)
    is_sso_verified = models.BooleanField(default=False, null=True)
    target_test_date = models.DateField(null=True)
    group_id = models.CharField(max_length=200, default=None, null=True)

    class Meta:
        db_table = 'student_group_events'


class TimeAnalytics(TimeAuditModel):
    TYPE_CHOICE = [('QUESTION','Question'),
                   ('PRACTICE_SHEET','Practice_Sheet'),
                   ('CPEA_SHEET','Cpea_Sheet'),] 
    student = models.ForeignKey(User, on_delete=models.CASCADE, related_name='time_analytics_user')
    assignment = models.ForeignKey(Assignment, on_delete=models.CASCADE, related_name='time_analytics_assignment')
    student_assignment_question = models.ForeignKey(StudentAssignmentQuestion, on_delete=models.CASCADE, related_name='time_analytics_assignment_question')
    student_question_option = models.ForeignKey(StudentQuestionOption, on_delete=models.CASCADE, related_name='time_analytics_question_option')
    time_taken = models.JSONField(default=dict)
    data = models.JSONField(default=dict)
    type = models.CharField(max_length=20, choices=TYPE_CHOICE)
    is_visited= models.BooleanField(default=False)
    is_answered = models.BooleanField(default=False)

class AppointmentReport(TimeAuditModel):
    REASON_CHOICE = [('TUTOR_NOT_JOINED','Tutor_not_joined'),
                   ('STUDENT_NOT_JOINED','Student_not_joined'),
                   ('CANCEL','Cancel'),
                   ('RESCHEDULE','Reshedule'),]
    is_student_joined = models.BooleanField(default=False)
    is_tutor_joined = models.BooleanField(default=False)
    appointment = models.ForeignKey(Appointments, on_delete=models.CASCADE, related_name='appointment_reports')
    reason = models.CharField(max_length=100, choices=REASON_CHOICE)

    class Meta:
        db_table = 'appointment_reports'



class ClassClassification(TimeAuditModel):
    type = models.CharField(max_length=255)

    class Meta:
        db_table = 'class_classification'

class StudentJourney(TimeAuditModel):
    # STATUS_CHOICES = [
    #     ('Pending', 'Pending'),
    #     ('Completed', 'Completed'),
    # ]
    CLASS_TYPE_CHOICES = [
        ('Core_prep', 'Core Prep'),
        ('CPEA', 'CPEA'),
        ('Group_class', 'Group Class'),
    ]
    # student = models.ForeignKey(User, on_delete=models.CASCADE, related_name='student_journey')
    # subject = models.CharField(max_length=255)
    completion_date = models.DateTimeField(null=True)
    appointment = models.ForeignKey(Appointments, on_delete=models.CASCADE, related_name='appointment_student_journey')
    # status = models.CharField(max_length=500, choices=STATUS_CHOICES, default='Pending')
    class_type = models.CharField(max_length=500, choices=CLASS_TYPE_CHOICES)

    class Meta:
        db_table = 'student_journey'


class StudentClasses(TimeAuditModel):
    student = models.ForeignKey(User, on_delete=models.CASCADE, related_name='student_class')
    is_cpea_enabled = models.BooleanField(default=False)
    is_core_prep_enabled = models.BooleanField(default= False)
    is_group_class_enabled = models.BooleanField(default= False) 

    class Meta:
        db_table = 'student_classes'
    



    
                                






    
    



        

























