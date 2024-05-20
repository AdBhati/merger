# accounts.utils
import uuid
import re

# accounts.views

from django.utils import timezone
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from zuperscore.api.permissions import IsAdminOrUserManager
from rest_framework.views import APIView
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken

from sentry_sdk import capture_exception, capture_message

from zuperscore.db.models import User
from zuperscore.api.serializers.people import UserSerializer, UserBaseSerializer
from zuperscore.db.models.conduct import (
    StudentAvailability,
)
from zuperscore.api.views.conduct import (
    StudentAvailabilitySerializer,
)


from .base import BaseSerializer, BaseViewset
from django.contrib.auth import get_user_model
from django.conf import settings
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.core.mail import EmailMultiAlternatives
from django.core.mail import send_mail
from django.contrib.auth.signals import user_logged_in
from random import randint

from zuperscore.db.models.conduct import (
    StudentAvailability,
)

from zuperscore.utils.msg import send_sms
PHONE_NUMBER_REGEX_PATTERN = ".*?(\\(?\\d{3}\\D{0,3}\\d{3}\\D{0,3}\\d{4}).*?"
EMAIL_ADDRESS_REGEX_PATTERN = (
    "([A-Za-z0-9]+[.-_])*[A-Za-z0-9]+@[A-Za-z0-9-]+(\\.[A-Z|a-z]{2,})+"
)

def check_valid_phone_number(phone_number):
    if len(phone_number) > 15:
        return False

    pattern = re.compile(PHONE_NUMBER_REGEX_PATTERN)
    return pattern.match(phone_number)


def check_valid_email_address(email_address):
    pattern = re.compile(EMAIL_ADDRESS_REGEX_PATTERN)
    return pattern.match(email_address)


def get_tokens_for_user(user):
    refresh = RefreshToken.for_user(user)
    return (
        str(refresh.access_token),
        str(refresh),
    )


class SignInEndpoint(APIView):
    permission_classes = (AllowAny,)

    def post(self, request):
        try:
            medium = request.data.get("medium", False)
            password = request.data.get("password", False)
            ## Raise exception if any of the above are missing
            if not medium or not password:
                capture_message("Sign in endpoint missing medium data")
                return Response(
                    {
                        "error": "Something went wrong. Please try again later or contact the support team."
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )

            if medium == "email":
                if not request.data.get(
                    "email", False
                ) or not check_valid_email_address(
                    request.data.get("email").strip().lower()
                ):
                    return Response(
                        {"error": "Please provide a valid email address."},
                        status=status.HTTP_400_BAD_REQUEST,
                    )

                email = request.data.get("email").strip().lower()
                if email is None:
                    return Response(
                        {"error": "Please provide a valid email address."},
                        status=status.HTTP_400_BAD_REQUEST,
                    )

                user = User.objects.get(email=email)

            elif medium == "mobile":
                if not request.data.get(
                    "mobile", False
                ) or not check_valid_phone_number(
                    request.data.get("mobile").strip().lower()
                ):
                    return Response(
                        {"error": "Please provide a valid mobile number."},
                        status=status.HTTP_400_BAD_REQUEST,
                    )

                mobile_number = request.data.get("mobile").strip().lower()
                if mobile_number is None:
                    return Response(
                        {"error": "Please provide a valid mobile number"},
                        status=status.HTTP_400_BAD_REQUEST,
                    )

                user = User.objects.get(mobile_number=mobile_number)

            else:
                capture_message("Sign in endpoint wrong medium data")
                return Response(
                    {
                        "error": "Something went wrong. Please try again later or contact the support team."
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )
            # send if it finds two? to logger
            if user is None:
                return Response(
                    {
                        "error": "Sorry, we could not find a user with the provided credentials. Please try again."
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )

            if not user.check_password(password):
                return Response(
                    {
                        "error": "Sorry, we could not find a user with the provided credentials. Please try again."
                    },
                    status=status.HTTP_403_FORBIDDEN,
                )
            if not user.is_active:
                return Response(
                    {
                        "error": "Your account has been deactivated. Please contact your site administrator."
                    },
                    status=status.HTTP_403_FORBIDDEN,
                )

            serialized_user = UserBaseSerializer(user).data

            # settings last active for the user
            user.last_active = timezone.now()
            user.last_login_time = timezone.now()
            user.last_login_ip = request.META.get("REMOTE_ADDR")
            user.last_login_medium = medium
            user.last_login_uagent = request.META.get("HTTP_USER_AGENT")
            user.token_updated_at = timezone.now()
            user.save()

            access_token, refresh_token = get_tokens_for_user(user)

            data = {
                "access_token": access_token,
                "refresh_token": refresh_token,
                "user": serialized_user,
            }

            return Response(data, status=status.HTTP_200_OK)

        except User.DoesNotExist:
            return Response(
                {
                    "error": "Sorry, we could not find a user with the provided credentials. Please try again."
                },
                status=status.HTTP_400_BAD_REQUEST,
            )
        except Exception as e:
            capture_exception(e)
            return Response(
                {
                    "error": "Something went wrong. Please try again later or contact the support team."
                },
                status=status.HTTP_400_BAD_REQUEST,
            )


# accounts.authentication


class SignUpEndpoint(APIView):
    permission_classes = [IsAdminOrUserManager]

    def post(self, request):
        try:
            first_name = request.data.get("first_name", "User")
            last_name = request.data.get("last_name", "")
            mobile_number = request.data.get("mobile_number")
            email = request.data.get("email").strip().lower()
            password = request.data.get("password")
            role = request.data.get('role')
            if User.objects.filter(email=email).exists():
                return Response(
                    {
                        "error": "This email address is already taken. Please try another one."
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )

            username = uuid.uuid4().hex
            user = User(
                username=username,
                email=email,
                first_name=first_name,
                last_name=last_name,
                mobile_number=mobile_number,
                role=role,
            )

            user.set_password(password)
            user.set_password_by_user = True
            user.last_active = timezone.now()
            user.last_login_time = timezone.now()
            user.last_login_ip = request.META.get("REMOTE_ADDR")
            user.last_login_uagent = request.META.get("HTTP_USER_AGENT")
            user.token_updated_at = timezone.now()
            user.class_start_date = None
            user.save()
            user_logged_in.send(
                sender=user,
                user=user,
                first_name=first_name,
                last_name=last_name,
                user_email=email,
                user_password=password,
            )

            serialized_user = UserSerializer(user).data

            serialized_student_availability = StudentAvailabilitySerializer(StudentAvailability.objects.create(student=user)).data

            access_token, refresh_token = get_tokens_for_user(user)
            data = {
                "access_token": access_token,
                "refresh_token": refresh_token,
                "user": serialized_user,
            }

            return Response(data, status=status.HTTP_201_CREATED)

        except Exception as e:
            print(e)
            capture_exception(e)
            return Response(
                {
                    "error": "Something went wrong. Please try again later or contact the support team."
                },
                status=status.HTTP_400_BAD_REQUEST,
            )


class SignOutEndpoint(APIView):
    def post(self, request):
        try:
            refresh_token = request.data.get("refresh_token", False)

            if not refresh_token:
                capture_message("No refresh token provided")
                return Response(
                    {
                        "error": "Something went wrong. Please try again later or contact the support team."
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )

            user = User.objects.get(pk=request.user.id)

            user.last_logout_time = timezone.now()
            user.last_logout_ip = request.META.get("REMOTE_ADDR")

            user.save()

            token = RefreshToken(refresh_token)
            token.blacklist()
            return Response({"message": "success"}, status=status.HTTP_200_OK)
        except Exception as e:
            capture_exception(e)
            return Response(
                {
                    "error": "Something went wrong. Please try again later or contact the support team."
                },
                status=status.HTTP_400_BAD_REQUEST,
            )


class ForgotPasswordView(APIView):
    permission_classes = [
        AllowAny,
    ]

    def post(self, request):
        email = request.data.get("email")
        try:
            user = User.objects.get(email=email)
            user.token = uuid.uuid4().hex + uuid.uuid4().hex
            user.save()
            reset_token = user.token
            url = f"{settings.WEB_URL}/reset-password/{reset_token}"
            subject = f"Password Reset Request from Zuperscore"
            message = f"""
Hey there,

Please reset your password by clicking on the link below: {url}

Regards,
Zuperscore Team
            """
            send_mail(
                subject,
                message,
                "team@zuperscore.com",
                [email],
                fail_silently=False,
            )
            return Response({"message": "success"}, status=status.HTTP_200_OK)
        except Exception as e:
            print(e)
            return Response(
                {"error": "Failed to send reset link"},
                status=status.HTTP_400_BAD_REQUEST,
            )


class ResetPasswordView(APIView):
    permission_classes = (AllowAny,)

    def post(self, request):
        token = request.data.get("token")
        password = request.data.get("password")
        try:
            user = User.objects.get(token=token)
            user.set_password(password)
            user.save()
            return Response({"message": "success"}, status=status.HTTP_200_OK)
        except Exception as e:
            print(e)
            return Response({"message": "failed"}, status=status.HTTP_400_BAD_REQUEST)

class SendMobileOtpView(APIView):
    def post(self, request):
        try:
            user = User.objects.get(pk=request.user.id)

            otp = randint(100000, 999999)
            user.mobile_otp = otp
            user.save()
            send_sms(user.mobile_number, otp)
            return Response({"message": "success"}, status=200)
        except Exception as e:
            print(e)
            return Response({"message": "failed"}, status=400)

class VerifyMobileOtpView(APIView):
    def post(self, request):
        otp = request.data.get("token")
        try:
            user = User.objects.get(pk=request.user.id)
            if user.mobile_otp == otp:
                user.mobile_verified = True
                user.save()
                return Response({"message": "success"}, status=status.HTTP_201_CREATED)
            else:
                return Response({"message": "failed"}, status=status.HTTP_200_OK)
        except Exception as e:
            print(e)
            return Response({"message": "failed"}, status=400)
