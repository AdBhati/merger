import uuid
from django.db import models
from django.contrib.auth.models import AbstractBaseUser
from django.utils import timezone


from crum import get_current_user

from ..mixins import AuditModel, TimeAuditModel
from django.contrib.auth.models import UserManager
from django.contrib.auth.models import PermissionsMixin
from django.dispatch import receiver
from django.core.mail import send_mail
from django.contrib.auth.signals import user_logged_in


class StudentCategory(TimeAuditModel):
    baseline_score = models.CharField(max_length=20, default="<550")
    ca = models.CharField(
        max_length=20,
        choices=(
            ("2ca", "2 CA"),
            ("3ca", "3 CA"),
            ("4ca", "4 CA"),
        ),
        default="2ca",
    )

    ha = models.CharField(
        max_length=20,
        choices=(
            ("5ha", "5 HA"),
            ("6ha", "6 HA"),
            ("7ha", "7 HA"),
        ),
        default="5ha",
    )
    name = models.CharField(
        max_length=20,
        choices=(
            ("r", "R"),
            ("s", "S"),
            ("t", "T"),
        ),
        default="r",
    )
    difficulty = models.CharField(max_length=20, default="5")
    short_desc = models.CharField(max_length=30)

    class Meta:
        db_table = "student_category"




class EnglishCategory(TimeAuditModel):
    baseline_score = models.CharField(max_length=20, default="<550")
    ca = models.CharField(
        max_length=20,
        choices=(
            ("2ca", "2 CA"),
            ("3ca", "3 CA"),
            ("4ca", "4 CA"),
        ),
        default="2ca",
    )

    ha = models.CharField(
        max_length=20,
        choices=(
            ("5ha", "5 HA"),
            ("6ha", "6 HA"),
            ("7ha", "7 HA"),
        ),
        default="5ha",
    )
    name = models.CharField(
        max_length=20,
        choices=(
            ("r", "R"),
            ("s", "S"),
            ("t", "T"),
        ),
        default="r",
    )
    difficulty = models.CharField(max_length=20, default="5")
    short_desc = models.CharField(max_length=30)

    class Meta:
        db_table = "english_category"



class MathCategory(TimeAuditModel):
    baseline_score = models.CharField(max_length=20, default="<550")
    ca = models.CharField(
        max_length=20,
        choices=(
            ("2ca", "2 CA"),
            ("3ca", "3 CA"),
            ("4ca", "4 CA"),
        ),
        default="2ca",
    )

    ha = models.CharField(
        max_length=20,
        choices=(
            ("5ha", "5 HA"),
            ("6ha", "6 HA"),
            ("7ha", "7 HA"),
        ),
        default="5ha",
    )
    name = models.CharField(
        max_length=20,
        choices=(
            ("r", "R"),
            ("s", "S"),
            ("t", "T"),
        ),
        default="r",
    )
    difficulty = models.CharField(max_length=20, default="5")
    short_desc = models.CharField(max_length=30)

    class Meta:
        db_table = "math_category"



class School(TimeAuditModel):
    TYPE_CHOICES = (("boarding", "Boarding"), ("day_school", "Day School"), ("weekly_boarding", "Weekly Boarding"))

    CURRICULUM_CHOICES = (
        ("ib", "IB"),
        ("gcse", "GSSE"),
        ("cbse", "CBSE"),
        ("isc", "ISC"),
        ("state_board", "State Board"),
        ("american_curriculum", "American Curriculum"),
        ("ap_curriculum", "AP Curriculum"),
        ("level", "Level"),
    )

    school_name = models.CharField(max_length=255, blank=True)
    school_city = models.CharField(max_length=255, blank=True)
    school_state = models.CharField(max_length=255, blank=True)
    school_country = models.CharField(max_length=255, blank=True)
    school_curriculum = models.CharField(max_length=255, choices=CURRICULUM_CHOICES, default="ib")
    school_type = models.CharField(max_length=255, choices=TYPE_CHOICES, default="boarding")

    def __str__(self):
        return self.school_name

    class Meta:
        db_table = "db_school"
        ordering = ('school_name',)


class User(AbstractBaseUser, PermissionsMixin):
    id = models.BigAutoField(unique=True, primary_key=True)
    username = models.CharField(max_length=128, unique=True)

    # user fields
    mobile_number = models.CharField(max_length=255, blank=True, null=True)
    email = models.CharField(max_length=255, unique=True)
    first_name = models.CharField(max_length=255, blank=True)
    last_name = models.CharField(max_length=255, blank=True)
    about = models.TextField(blank=True)
    profile_img = models.TextField(blank=True)

    # tracking metrics
    date_joined = models.DateTimeField(auto_now_add=True, verbose_name="Created At")
    class_start_date = models.DateField(null=True) # new_field_date
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Created At")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Last Modified At")
    last_location = models.CharField(max_length=255, blank=True)
    created_location = models.CharField(max_length=255, blank=True)

    # the is' es
    is_superuser = models.BooleanField(default=False)
    is_managed = models.BooleanField(default=False)
    is_password_expired = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_email_verified = models.BooleanField(default=False)
    is_password_autoset = models.BooleanField(default=False)

    token = models.CharField(max_length=64, blank=True)

    ROLE_CHOICES = (
        ("admin", "Admin"),
        ("user", "User"),
        ("tutor", "Tutor"),
        ("typist", "Typist"),
        ("manager", "Manager"),
        ("prep_manager", "Prep Manager"),
        ("sso_manager", "SSO Manager"),
        ("parent", "Parent"),
        ("counselor", "Counselor"),
        ("user_manager", "User Manager"),
        ("guest", "Guest"),
        ("hod_reading", "HOD Reading"),
        ("hod_writing", "HOD Writing"),
        ("hod_math", "HOD Math"),
    )

    role = models.CharField(max_length=64, choices=ROLE_CHOICES, default="guest")
    billing_address_country = models.CharField(max_length=255, default="INDIA")
    billing_address = models.JSONField(null=True)
    has_billing_address = models.BooleanField(default=False)

    user_timezone = models.CharField(max_length=255, default="Asia/Kolkata")

    last_active = models.DateTimeField(default=timezone.now, null=True)
    last_login_time = models.DateTimeField(null=True)
    last_logout_time = models.DateTimeField(null=True)
    last_login_ip = models.CharField(max_length=255, blank=True)
    last_logout_ip = models.CharField(max_length=255, blank=True)
    last_login_medium = models.CharField(
        max_length=20,
        default="email",
    )
    last_login_uagent = models.TextField(blank=True)
    token_updated_at = models.DateTimeField(null=True)

    initial_assessments = models.JSONField(null=True)
    initial_assessments_completed = models.JSONField(null=True)
    mobile_verified = models.BooleanField(default=False)
    mobile_otp = models.CharField(max_length=255, blank=True)
    USERNAME_FIELD = "username"
    # REQUIRED_FIELDS = ["email"]
    prep_managers = models.ManyToManyField("self", blank=True)
    sso_managers = models.ManyToManyField("self", blank=True)
    ops_managers = models.ManyToManyField("self", blank=True)
    english_tutors = models.ManyToManyField("self", blank=True)
    english_reading_tutors = models.ManyToManyField("self", blank=True)
    english_writing_tutors = models.ManyToManyField("self", blank=True)
    math_tutors = models.ManyToManyField("self", blank=True)
    parents = models.ManyToManyField("self", blank=True)
    counselors = models.ManyToManyField("self", blank=True)

    parent_1_name = models.CharField(max_length=255, blank=True)
    parent_2_name = models.CharField(max_length=255, blank=True)
    parent_1_email = models.CharField(max_length=255, blank=True)
    parent_2_email = models.CharField(max_length=255, blank=True)
    parent_1_mobile = models.CharField(max_length=255, blank=True)
    parent_2_mobile = models.CharField(max_length=255, blank=True)

    dob = models.DateField(null=True)
    address = models.CharField(max_length=255, blank=True)
    city = models.CharField(max_length=255, blank=True)
    state = models.CharField(max_length=255, blank=True)
    country = models.CharField(max_length=255, blank=True)
    pincode = models.CharField(max_length=255, blank=True)
    school = models.ForeignKey(
        School,
        on_delete=models.CASCADE,
        related_name="school",
        null=True,
        blank=True,
    )
    year_of_passing = models.CharField(max_length=255, blank=True)
    timezone = models.CharField(max_length=255, blank=True)
    test_results = models.JSONField(null=True)
    referred_by = models.JSONField(null=True)
    set_password_by_user = models.BooleanField(default=False)
    whatsapp_number = models.CharField(max_length=255, blank=True)
    # school_state = models.CharField(max_length=255, blank=True)
    # school_country = models.CharField(max_length=255, blank=True)
    # school_curriculum = models.CharField(max_length=255, blank=True)
    starting_scores = models.JSONField(null=True)
    goal_post = models.JSONField(null=True)
    student_comments = models.CharField(max_length=255, blank=True)
    parents_comments = models.CharField(max_length=255, blank=True)
    sso_comments = models.CharField(max_length=255, blank=True)
    bd_comments_enquiry = models.CharField(max_length=255, blank=True)
    help = models.JSONField(null=True)
    prep_navigation = models.JSONField(null=True)
    day_schedule_user_id = models.CharField(max_length=255, blank=True)
    english_category = models.ForeignKey(EnglishCategory, on_delete=models.CASCADE, null=True, blank=True, related_name="english_category")
    math_category = models.ForeignKey(MathCategory, on_delete=models.CASCADE, null=True, blank=True, related_name="math_category")
    


    TUTOR_CHOICES = (
        ("english", "English"),
        ("math", "Math"),
        ("english_reading","English_Reading"),
        ("english_writing","English_Writing"),
    )

    tutor_type = models.CharField(max_length=64, choices=TUTOR_CHOICES, default="english")
    is_onboarded = models.BooleanField(default=False)
    is_cpea_eligible = models.BooleanField(default=False)
    total_class_per_day = models.IntegerField(default=2)
    total_mega_domain_class_per_day = models.IntegerField(default=1)
    is_english_reading_assigned = models.BooleanField(default=False, null=True, blank=True)
    is_english_writing_assigned = models.BooleanField(default=False, null=True, blank=True)
    is_math_assigned = models.BooleanField(default=False, null=True, blank=True)
    isRepeater = models.BooleanField(default=False, null=True, blank=True) #change the name
    tutor_slot = models.IntegerField(default=0) #change the name
  


    objects = UserManager()

    def __str__(self):
        return self.username

    def save(self, *args, **kwargs):
        self.email = self.email.lower().strip()
        super(User, self).save(*args, **kwargs)



class Comment(TimeAuditModel):
   
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True, related_name="student_id")
    comment = models.CharField(max_length=500, blank=True)
    COMMENT_TYPE = (
        ("student", "Student"),
        ("parent", "Parent"),
    )
    type = models.CharField(max_length=255, choices= COMMENT_TYPE, default="parent")

    def __str__(self):
        return self.comment

    class Meta:
        db_table = "comments"


class Target_Test_Date(TimeAuditModel):
    date=models.DateField()

    class Meta:
        db_table='target_test_dates'
        

class BaseModel(AuditModel):
    uuid = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)

    class Meta:
        abstract = True

    def save(self, *args, **kwargs):
        user = get_current_user()

        if user is None or user.is_anonymous:
            self.created_by = None
            self.updated_by = None
            super(BaseModel, self).save(*args, **kwargs)
        else:
            self.created_by = user
            self.updated_by = user
            super(BaseModel, self).save(*args, **kwargs)

    def __str__(self):
        return str(self.uuid)


@receiver(user_logged_in)
def user_email_handler(
    user, first_name=None, last_name=None, user_email=None, user_password=None, **kwargs
):
    if user and first_name and last_name and user_email and user_password:
        email_body = """Dear {} {},

Thank you for contacting Zuperscore

Please visit our website https://zuperscore.com/ and click Login.

Here are your login details

Email: {}
Password: {}

The password you received is the system generated default password, you will need to change the password after you log into the platform.

Wish you Good luck!

Warm Regards,

Team Zuperscore
    """
        email_body = email_body.format(first_name, last_name, user_email, user_password)
        email_subject = "Welcome to Zuperscore"
        email = user_email
        send_mail(
            email_subject,
            email_body,
            "Team Zuperscore <support@satnpaper.com>",
            [email],
            fail_silently=True,
        )
        print("Mail sent successfully.")
