from rest_framework.serializers import ModelSerializer

from zuperscore.db.models import User


class UserSerializer(ModelSerializer):
    class Meta:
        model = User
        fields = "__all__"
        extra_kwargs = {"password": {"write_only": True}}


class UserBaseSerializer(ModelSerializer):
    class Meta:
        model = User
        fields = (
            "id",
            "username",
            "mobile_number",
            "email",
            "first_name",
            "last_name",
            "password",
            "profile_img",
            "last_location",
            "created_location",
            "is_superuser",
            "is_managed",
            "is_password_expired",
            "is_active",
            "is_staff",
            "is_email_verified",
            "is_password_autoset",
            "role",
            "last_active",
            "last_login_time",
            "last_logout_time",
            "last_login_ip",
            "last_logout_ip",
            "last_login_medium",
            "last_login_uagent",
            "token_updated_at",
            "mobile_verified",
            "timezone",
            "user_timezone",
            "class_start_date",
            "is_onboarded",
            "tutor_type",
            "is_english_writing_assigned",
            "is_english_reading_assigned",
            "is_math_assigned",
            

        )

        extra_kwargs = {"password": {"write_only": True}}