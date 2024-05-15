from django.forms import model_to_dict
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from sentry_sdk import capture_exception
import django_filters
from datetime import date, datetime, timedelta
from django_filters import rest_framework as filters
from rest_framework import filters as rest_filters
from django.db.models import Q

from zuperscore.db.models.conduct import StudentAvailability, StudentSessionPlan
from zuperscore.db.models.library import TutorAvailability
from .base import BaseSerializer, BaseViewset
from zuperscore.api.serializers.people import UserSerializer
from django.db.models.functions import ExtractMonth, ExtractYear
from datetime import datetime, timedelta
from rest_framework.permissions import AllowAny

from django.db.models.functions import Coalesce
from django.db.models import Prefetch, Exists, OuterRef
from zuperscore.db.models.conduct import (
    StudentAvailability,
)

# from zuperscore.api.views.conduct import (
#     StudentAvailabilitySerializer,
# )

from django_filters import rest_framework as filters
from rest_framework import filters as rest_filters
from django.db.models import (
    Q,
    F,
    Case,
    When,
)
from django.db.models.functions import Cast
from .base import BaseSerializer, BaseViewset
from zuperscore.api.serializers.people import UserSerializer
from zuperscore.api.serializers.assessments import (
    UserAssessmentSessionMinimumSerializer,
)
from django.db.models.functions import ExtractMonth, ExtractYear, Trim
from datetime import datetime

from zuperscore.utils.paginator import BasePaginator

from zuperscore.db.models import User

from zuperscore.db.models.base import School, Comment, Target_Test_Date
from rest_framework import serializers
from rest_framework import viewsets
from zuperscore.db.models.base import School
from zuperscore.db.models.assessments import UserAssessmentSession
from rest_framework import serializers
from rest_framework import viewsets
from zuperscore.api.permissions.permissions import IsNotStudent, IsPlatformAdmin
from rest_framework.exceptions import APIException


class SchoolSerializer(BaseSerializer):
    class Meta:
        model = School
        fields = "__all__"


class UserMinimumSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = (
            "id",
            "first_name",
            "last_name",
            "email",
            "about",
            "profile_img",
            "role",
            "is_onboarded",
            "is_english_writing_assigned",
            "is_english_reading_assigned",
            "is_math_assigned",
            "tutor_type",
            "isRepeater",
        )


class UserManagerFilterSerializer(UserMinimumSerializer):
    latest_assessment_session = serializers.SerializerMethodField()

    class Meta(UserMinimumSerializer):
        model = User
        fields = UserMinimumSerializer.Meta.fields + (
            "test_results",
            "last_ptm_date",
            "latest_assessment_session",
            "pending_classes",
            "goal_post",
        )

    def get_latest_assessment_session(self, instance):
        latest_session = (
            instance.user_assessment_sessions.filter(is_submitted=True)
            .order_by("-submitted_at")
            .first()
        )
        if latest_session:
            return UserAssessmentSessionMinimumSerializer(instance=latest_session).data
        return None


class UserAllocateManagerSerializer(BaseSerializer):
    class Meta:
        model = User
        fields = (
            "prep_managers",
            "sso_managers",
            "ops_managers",
            "english_tutors",
            "math_tutors",
        )


class UserSerializer(serializers.ModelSerializer):
    """
    User Serializer View
    """

    school = SchoolSerializer(read_only=True)
    prep_managers_detail = UserMinimumSerializer(
        read_only=True, many=True, source="prep_managers"
    )
    sso_managers_detail = UserMinimumSerializer(
        read_only=True, many=True, source="sso_managers"
    )
    ops_managers_detail = UserMinimumSerializer(
        read_only=True, many=True, source="ops_managers"
    )
    english_tutors_detail = UserMinimumSerializer(
        read_only=True, many=True, source="english_tutors"
    )
    math_tutors_detail = UserMinimumSerializer(
        read_only=True, many=True, source="math_tutors"
    )
    parents_detail = UserMinimumSerializer(read_only=True, many=True, source="parents")
    counselors_detail = UserMinimumSerializer(
        read_only=True, many=True, source="counselors"
    )
    latest_assessment_session = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            "id",
            "mobile_number",
            "email",
            "first_name",
            "last_name",
            "about",
            "profile_img",
            "whatsapp_number",
            "is_active",
            "is_staff",
            "initial_assessments",
            "initial_assessments_completed",
            "user_timezone",
            "role",
            "prep_managers",
            "sso_managers",
            "ops_managers",
            "english_tutors",
            "math_tutors",
            "parents",
            "counselors",
            "prep_managers_detail",
            "sso_managers_detail",
            "ops_managers_detail",
            "english_tutors_detail",
            "math_tutors_detail",
            "parents_detail",
            "counselors_detail",
            "dob",
            "address",
            "city",
            "state",
            "country",
            "pincode",
            "school",
            "year_of_passing",
            "timezone",
            "test_results",
            "referred_by",
            "set_password_by_user",
            "prep_navigation",
            "help",
            "goal_post",
            "student_comments",
            "parents_comments",
            "sso_comments",
            "bd_comments_enquiry",
            "starting_scores",
            "parent_1_name",
            "parent_2_name",
            "parent_1_email",
            "parent_2_email",
            "parent_1_mobile",
            "parent_2_mobile",
            "class_start_date",
            "is_onboarded",
            "total_class_per_day",
            "total_mega_domain_class_per_day",
            "is_english_writing_assigned",
            "is_english_reading_assigned",
            "is_math_assigned",
            "tutor_type",
            "tutor_slot",
            "last_ptm_date",
            "latest_assessment_session",
            "pending_classes",
        )

    def get_latest_assessment_session(self, instance):
        latest_session = (
            instance.user_assessment_sessions.filter(is_submitted=True)
            .order_by("-submitted_at")
            .first()
        )
        if latest_session:
            return UserAssessmentSessionMinimumSerializer(instance=latest_session).data
        return None


class NewUserSerializer(serializers.ModelSerializer):
    """
    User Serializer View
    """

    # school = SchoolSerializer(read_only=True)
    prep_managers_detail = UserMinimumSerializer(
        read_only=True, many=True, source="prep_managers"
    )
    sso_managers_detail = UserMinimumSerializer(
        read_only=True, many=True, source="sso_managers"
    )
    ops_managers_detail = UserMinimumSerializer(
        read_only=True, many=True, source="ops_managers"
    )
    english_tutors_detail = UserMinimumSerializer(
        read_only=True, many=True, source="english_tutors"
    )
    english_reading_tutors_detail = UserMinimumSerializer(
        read_only=True, many=True, source="english_reading_tutors"
    )
    english_writing_tutors_detail = UserMinimumSerializer(
        read_only=True, many=True, source="english_writing_tutors"
    )
    math_tutors_detail = UserMinimumSerializer(
        read_only=True, many=True, source="math_tutors"
    )
    parents_detail = UserMinimumSerializer(read_only=True, many=True, source="parents")
    counselors_detail = UserMinimumSerializer(
        read_only=True, many=True, source="counselors"
    )

    class Meta:
        model = User
        fields = (
            "id",
            "mobile_number",
            "email",
            "first_name",
            "last_name",
            "about",
            "profile_img",
            "whatsapp_number",
            "is_active",
            "is_staff",
            "initial_assessments",
            "initial_assessments_completed",
            "user_timezone",
            "role",
            "prep_managers",
            "sso_managers",
            "ops_managers",
            "english_tutors",
            "english_reading_tutors",
            "english_writing_tutors",
            "math_tutors",
            "parents",
            "counselors",
            "prep_managers_detail",
            "sso_managers_detail",
            "ops_managers_detail",
            "english_tutors_detail",
            "english_reading_tutors_detail",
            "english_writing_tutors_detail",
            "math_tutors_detail",
            "parents_detail",
            "counselors_detail",
            "dob",
            "address",
            "city",
            "state",
            "country",
            "pincode",
            "school",
            "year_of_passing",
            "timezone",
            "test_results",
            "referred_by",
            "set_password_by_user",
            "prep_navigation",
            "help",
            "goal_post",
            "student_comments",
            "parents_comments",
            "sso_comments",
            "bd_comments_enquiry",
            "starting_scores",
            "parent_1_name",
            "parent_2_name",
            "parent_1_email",
            "parent_2_email",
            "parent_1_mobile",
            "parent_2_mobile",
            "class_start_date",
            "is_onboarded",
            "total_class_per_day",
            "total_mega_domain_class_per_day",
            "is_english_writing_assigned",
            "is_english_reading_assigned",
            "is_math_assigned",
            "tutor_type",
            "tutor_slot",
        )


class UserMinimumSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = (
            "id",
            "first_name",
            "last_name",
            "email",
            "about",
            "profile_img",
            "role",
            "created_at",
            "tutor_type",
            "class_start_date",
            "is_onboarded",
            "is_english_writing_assigned",
            "is_english_reading_assigned",
            "is_math_assigned",
            "user_timezone",
            "isRepeater",
        )


class UserTeachersSerializer(serializers.ModelSerializer):
    # math_tutors_detail = UserMinimumSerializer(read_only=True, many=True, source="math_tutors")
    class Meta:
        model = User
        fields = (
            "id",
            "first_name",
            "last_name",
            "email",
            "about",
            "profile_img",
            "day_schedule_user_id",
            "is_onboarded",
            "tutor_type",
        )

    # filterset_fields = (
    #     "date_joined",
    #     "school",
    # )

    # search_fields = (
    #     "^first_name",
    #     "^last_name",
    #     "^email",
    #     "^username",
    # )

    # filter_backends = (
    #     filters.DjangoFilterBackend,
    #     rest_filters.SearchFilter,
    # )

    # def filter_queryset(self, queryset):
    #     for backend in list(self.filter_backends):
    #         queryset = backend().filter_queryset(self.request, queryset, self)
    #     return queryset

    # def get(self, request):
    #     try:
    #         role = request.GET.get("role")
    #         tutor_id = request.GET.get("tutor_id")
    #         manager_id = request.GET.get("manager_id")
    #         parent_id = request.GET.get("parent_id")
    #         counselor_id = request.GET.get("counselor_id")

    #         if role:
    #             users = User.objects.filter(role=role).order_by("-date_joined")
    #         elif tutor_id:
    #             users = (
    #                 User.objects.filter(Q(english_tutors__in=[tutor_id]) | Q(math_tutors__in=[tutor_id]))
    #                 .order_by("-date_joined")
    #                 .distinct()
    #             )
    #         elif manager_id:
    #             users = User.objects.filter(
    #                 Q(prep_managers__in=[manager_id])
    #                 | Q(sso_managers__in=[manager_id])
    #                 | Q(ops_managers__in=[manager_id])
    #             ).order_by("-date_joined")
    #         elif parent_id:
    #             users = User.objects.filter(Q(parents__in=[parent_id])).order_by("-date_joined")
    #         elif counselor_id:
    #             users = User.objects.filter(Q(counselor__in=[counselor_id])).order_by("-date_joined")
    #         else:
    #             users = User.objects.all().order_by("-date_joined")

    #         targeted_date = request.GET.get("targeted_date")
    #         if targeted_date:
    #             year, month, _ = targeted_date.split("-")
    #             print("year", year, "month", month)
    #             users = users.filter(Q(goal_post__isnull=False))
    #             users = users.exclude(Q(goal_post__target_test_date=""))

    #             for user in users:
    #                 goal_post = user.goal_post
    #                 temp_year, temp_month, temp_day = goal_post["target_test_date"].split("-")
    #                 if not (temp_year == year and temp_month == month):
    #                     users = users.exclude(id=user.id)
    #             # users = users.filter(Q(goal_post__target_test_date__year=year, goal_post__target_test_date__month=month))

    #         print("users length", len(users))

    #         if request.GET.get("search", None) is not None and len(request.GET.get("search")) < 3:
    #             return Response(
    #                 {"message": "Search term must be at least 3 characters long"},
    #                 status=status.HTTP_400_BAD_REQUEST,
    #             )

    #         return self.paginate(
    #             request=request,
    #             queryset=self.filter_queryset(users),
    #             on_results=lambda data: UserSerializer(data, many=True).data,
    #         )
    #     except Exception as e:
    #         capture_exception(e)
    #         print("this is error ", e)
    #         return Response({"message": "Something went wrong"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    # def post(self, request):
    #     try:
    #         serializer = UserSerializer(data=request.data)
    #         if serializer.is_valid():
    #             serializer.save()
    #             return Response(
    #                 {"message": "User created successfully"},
    #                 status=status.HTTP_201_CREATED,
    #             )
    #         return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    #     except Exception as e:
    #         capture_exception(e)
    #         return Response({"message": "Something went wrong"}, status=status.HTTP_400_BAD_REQUEST)


class PeopleView(APIView, BasePaginator):
    filterset_fields = (
        "date_joined",
        "school",
    )

    search_fields = (
        "^first_name",
        "^last_name",
        "^email",
        "^username",
    )

    filter_backends = (
        filters.DjangoFilterBackend,
        rest_filters.SearchFilter,
    )

    def filter_queryset(self, queryset):
        for backend in list(self.filter_backends):
            queryset = backend().filter_queryset(self.request, queryset, self)
        return queryset

    def get_session_allotment_info(self, user):
        print("====>")
        sessions = StudentSessionPlan.objects.filter(student=user)
        print("sessions===>", sessions)

        return {
            "english_reading_session_allotted": sessions.filter(
                mega_domain__name="Reading"
            ).exists(),
            "math_reading_session_allotted": sessions.filter(
                mega_domain__name="Math"
            ).exists(),
            "english_writing_session_allotted": sessions.filter(
                mega_domain__name="Writing"
            ).exists(),
        }

    def get(self, request):

        try:
            role = request.GET.get("role")
            tutor_id = request.GET.get("tutor_id")
            manager_id = request.GET.get("manager_id")
            parent_id = request.GET.get("parent_id")
            counselor_id = request.GET.get("counselor_id")
            active = request.GET.get("is_active")
            minimum = True if request.GET.get("is_minimum", False) == "true" else False

            if active == "false":
                if request.user.role == "admin":
                    userObjects = User.objects.filter(is_active=False)
                else:
                    return self.paginate(
                        request=request,
                        queryset=self.filter_queryset(User.objects.none()),
                        on_results=lambda data: UserSerializer(data, many=True).data,
                    )

            else:
                userObjects = User.objects.filter(is_active=True)

            if role:
                users = userObjects.filter(role=role).order_by("-date_joined")
            elif tutor_id:
                users = (
                    userObjects.filter(
                        Q(english_tutors__in=[tutor_id]) | Q(math_tutors__in=[tutor_id])
                    )
                    .order_by("-date_joined")
                    .distinct()
                )
            elif manager_id:
                users = userObjects.filter(
                    Q(prep_managers__in=[manager_id])
                    | Q(sso_managers__in=[manager_id])
                    | Q(ops_managers__in=[manager_id])
                ).order_by("-date_joined")
            elif parent_id:
                users = userObjects.filter(Q(parents__in=[parent_id])).order_by(
                    "-date_joined"
                )
            elif counselor_id:
                users = userObjects.filter(Q(counselors__in=[counselor_id])).order_by(
                    "-date_joined"
                )
            else:
                users = userObjects.all().order_by("-date_joined")

            targeted_date = request.GET.get("targeted_date")
            if targeted_date:
                year, month, _ = targeted_date.split("-")
                print("year", year, "month", month)
                users = users.filter(Q(goal_post__isnull=False))
                users = users.exclude(Q(goal_post__target_test_date=""))

                for user in users:
                    goal_post = user.goal_post
                    temp_year, temp_month, temp_day = goal_post[
                        "target_test_date"
                    ].split("-")
                    if not (temp_year == year and temp_month == month):
                        users = users.exclude(id=user.id)
                # users = users.filter(Q(goal_post__target_test_date__year=year, goal_post__target_test_date__month=month))

            if (
                request.GET.get("search", None) is not None
                and len(request.GET.get("search")) < 3
            ):
                return Response(
                    {"message": "Search term must be at least 3 characters long"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            return self.paginate(
                request=request,
                queryset=self.filter_queryset(users.distinct()),
                on_results=lambda data: (
                    UserMinimumSerializer(data, many=True).data
                    if minimum
                    else UserSerializer(data, many=True).data
                ),
                extra_stats={"total_users": users.distinct().count()},
            )
        except Exception as e:
            capture_exception(e)
            print("this is error ", e)
            return Response(
                {"message": "Something went wrong"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


class FilterPeopleViewSet(APIView, BasePaginator):

    search_fields = (
        "^first_name",
        "^last_name",
        "^email",
        "^username",
    )

    filter_backends = (
        filters.DjangoFilterBackend,
        rest_filters.SearchFilter,
    )

    def filter_queryset(self, queryset):
        for backend in list(self.filter_backends):
            queryset = backend().filter_queryset(self.request, queryset, self)
        return queryset

    def compute_temporary_field(self, user_instance):
        # Example: Compute some value based on existing fields or data
        test_results = user_instance.test_results
        if test_results:
            count_of_sat_results = len(
                [
                    result
                    for result in test_results
                    if result.get("type_of_test") == "SAT"
                ]
            )
            # print(count_of_sat_results)
            return count_of_sat_results
        return 0

    def calculate_section_marks(self, section_data, section_name):
        try:

            if section_name == "english" and len(section_data) > 1:
                sec_one_score = (
                    section_data[0].get("results", {}).get("correct_answers", 0)
                )
                sec_two_score = (
                    section_data[1].get("results", {}).get("correct_answers", 0)
                )
                return sec_one_score + sec_two_score
            elif section_name == "math" and len(section_data) > 2:
                sec_third_score = (
                    section_data[2].get("results", {}).get("correct_answers", 0)
                )
                sec_fourth_score = (
                    section_data[3].get("results", {}).get("correct_answers", 0)
                )
                return sec_third_score + sec_fourth_score
            else:
                return 0

        except Exception as e:
            print("this is error 2", e)

    def post(self, request):

        # filter_params = request.data
        try:
            # view query params
            tutor_id = request.GET.get("tutor_id", "")
            manager_id = request.GET.get("manager_id", "")
            parent_id = request.GET.get("parent_id", "")
            counselor_id = request.GET.get("counselor_id", "")
            # filter params
            school = request.data.get("school", [])
            target_test_date = request.data.get("target_test_date", [])
            role = request.data.get("role", [])
            city = request.data.get("city", "")
            state = request.data.get("state", "")
            country = request.data.get("country", "")
            tutor = request.data.get("tutor", [])
            ops_manager = request.data.get("ops_manager", [])
            prep_manager = request.data.get("prep_manager", [])
            sso_manager = request.data.get("sso_manager", [])
            accommodation = request.data.get("accommodation", "")
            active = request.GET.get("is_active")
            minimum = True if request.GET.get("is_minimum", False) == "true" else False
            # sort params
            field_name = request.GET.get("sort")
            order = request.GET.get("order")

            if active == "false":
                if request.user.role == "admin":
                    userObjects = User.objects.filter(is_active=False).order_by(
                        "-date_joined"
                    )
            else:
                if tutor_id:
                    userObjects = User.objects.filter(
                        Q(is_active=True)
                        & (
                            Q(english_tutors__in=[tutor_id])
                            | Q(math_tutors__in=[tutor_id])
                        )
                    ).order_by("-date_joined")

                elif manager_id:
                    userObjects = User.objects.filter(
                        Q(is_active=True)
                        & (
                            Q(prep_managers__in=[manager_id])
                            | Q(sso_managers__in=[manager_id])
                            | Q(ops_managers__in=[manager_id])
                        )
                    ).order_by("-date_joined")

                elif parent_id:
                    userObjects = User.objects.filter(
                        Q(is_active=True) & Q(parents__in=[parent_id])
                    ).order_by("-date_joined")
                elif counselor_id:
                    userObjects = User.objects.filter(
                        Q(is_active=True) & Q(counselors__in=[counselor_id])
                    ).order_by("-date_joined")

                else:
                    userObjects = User.objects.filter(is_active=True).order_by(
                        "-date_joined"
                    )

            # filters
            if len(school) > 0:
                userObjects = userObjects.filter(school__in=school)

            if len(role) > 0:
                userObjects = userObjects.filter(role__in=role)

            if country:
                userObjects = userObjects.filter(country=country)

            if state:
                userObjects = userObjects.filter(state=state)

            if city:
                userObjects = userObjects.filter(city=city)

            if len(prep_manager) > 0:
                userObjects = userObjects.filter(prep_managers__in=prep_manager)

            if len(sso_manager) > 0:
                userObjects = userObjects.filter(sso_managers__in=sso_manager)

            if len(ops_manager) > 0:
                userObjects = userObjects.filter(ops_managers__in=ops_manager)

            if len(tutor) > 0:
                userObjects = userObjects.filter(
                    Q(math_tutors__in=tutor) | Q(english_tutors__in=tutor)
                )
            if len(target_test_date) > 0:
                filter_query = Q()
                for date in target_test_date:
                    filter_query |= Q(goal_post__contains={"target_test_date": date})

                userObjects = userObjects.filter(filter_query)

            if accommodation:
                userObjects = userObjects.filter(
                    goal_post__contains={
                        "accommodation": True if accommodation == "yes" else False
                    }
                )

            if (
                request.GET.get("search", None) is not None
                and len(request.GET.get("search")) < 3
            ):
                return Response(
                    {"message": "Search term must be at least 3 characters long"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            if field_name == "name":
                userObjects = userObjects.annotate(
                    trimmed_first_name=Trim(F("first_name"), chars=" ")
                ).order_by(
                    "trimmed_first_name" if order == "ascend" else "-trimmed_first_name"
                )

            if field_name == "target_test_date":

                userObjects = userObjects.filter(
                    Q(goal_post__has_key="target_test_date")
                    # & ~Q(goal_post__target_test_date="")
                ).order_by(
                    "-goal_post__target_test_date"
                    if order == "ascend"
                    else "goal_post__target_test_date"
                )

            if (
                field_name == "pc_reading"
                or field_name == "pc_writing"
                or field_name == "pc_math"
            ):
                user_pending_cls = []
                filtered_ids = []
                for user in userObjects:
                    if user.pending_classes:
                        user_pending_cls.append(
                            {
                                "id": user.id,
                                "reading": (
                                    user.pending_classes.get("reading", "-")
                                    if user.pending_classes.get("reading", "-").strip()
                                    != ""
                                    else "-"
                                ),
                                "writing": (
                                    user.pending_classes.get("writing", "-")
                                    if user.pending_classes.get("writing", "-").strip()
                                    != ""
                                    else "-"
                                ),
                                "math": (
                                    user.pending_classes.get("math", "-")
                                    if user.pending_classes.get("math", "-").strip()
                                    != ""
                                    else "-"
                                ),
                            }
                        )
                if field_name == "pc_reading":
                    reading_cls = [
                        pc for pc in user_pending_cls if pc.get("reading", "") != "-"
                    ]
                    reading_cls = sorted(
                        reading_cls, key=lambda item: item.get("reading")
                    )
                    if order == "descend":
                        reading_cls = reading_cls[::-1]

                    filtered_ids = [rc.get("id") for rc in reading_cls]

                if field_name == "pc_writing":
                    writing_cls = [
                        pc for pc in user_pending_cls if pc.get("writing", "") != "-"
                    ]
                    writing_cls = sorted(
                        writing_cls, key=lambda item: item.get("writing")
                    )
                    if order == "descend":
                        writing_cls = writing_cls[::-1]

                    filtered_ids = [rc.get("id") for rc in writing_cls]

                if field_name == "pc_math":
                    math_cls = [
                        pc for pc in user_pending_cls if pc.get("math", "") != "-"
                    ]
                    math_cls = sorted(math_cls, key=lambda item: item.get("math"))
                    if order == "descend":
                        math_cls = math_cls[::-1]

                    filtered_ids = [rc.get("id") for rc in math_cls]

                userObjects = userObjects.order_by(
                    Case(
                        *[
                            When(id=id_val, then=pos)
                            for pos, id_val in enumerate(filtered_ids)
                        ]
                    )
                )

            # if field_name == "pc_english":
            #     userObjects = userObjects.filter(
            #         Q(pending_classes__has_key="reading")
            #         & ~Q(pending_classes__reading="")
            #         & ~Q(pending_classes__reading="-")
            #     ).order_by(
            #         "-pending_classes__reading"
            #         if order == "ascend"
            #         else "pending_classes__reading"
            #     )

            # if field_name == "pc_writing":
            #     userObjects = userObjects.filter(
            #         Q(pending_classes__has_key="writing")
            #         & ~Q(pending_classes__writing="")
            #         & ~Q(pending_classes__writing="-")
            #     ).order_by(
            #         "-pending_classes__writing"
            #         if order == "ascend"
            #         else "pending_classes__writing"
            #     )

            # if field_name == "pc_math":
            #     userObjects = userObjects.filter(
            #         Q(pending_classes__has_key="math")
            #         & ~Q(pending_classes__math="")
            #         & ~Q(pending_classes__math="-")
            #     ).order_by(
            #         "-pending_classes__math"
            #         if order == "ascend"
            #         else "pending_classes__math"
            #     )

            if field_name == "bs_english" or field_name == "bs_math":
                user_score_data = []

                for user in userObjects:
                    if user.test_results:
                        score = [
                            ts.get("score", "")
                            for ts in user.test_results
                            if ts.get("type_of_test", "") == "SAT"
                            and ts.get("kind", "") in ["diagnostic", "actual", "outside_actual"]
                        ]

                        if len(score) > 0 and type(score[-1]) != type(" "):
                            user_score_data.append(
                                {
                                    "id": user.id,
                                    # "english": int(score[-1].get("english", 0)),
                                    "english": int(
                                        sorted(
                                            score, key=lambda item: item.get("english")
                                        )[-1].get("english", 0)
                                    ),
                                    "math": int(
                                        sorted(
                                            score, key=lambda item: item.get("math")
                                        )[-1].get("math", 0)
                                    ),
                                }
                            )

                if field_name == "bs_english":
                    sorted_english_score = sorted(
                        user_score_data, key=lambda item: item.get("english")
                    )
                    if order == "descend":
                        sorted_english_score = sorted_english_score[::-1]
                    filtered_ids = [score.get("id") for score in sorted_english_score]

                    userObjects = userObjects.order_by(
                        Case(
                            *[
                                When(id=id_val, then=pos)
                                for pos, id_val in enumerate(filtered_ids)
                            ]
                        )
                    )

                if field_name == "bs_math":
                    sorted_math_score = sorted(
                        user_score_data, key=lambda item: item.get("math")
                    )
                    if order == "descend":
                        sorted_math_score = sorted_math_score[::-1]

                    filtered_ids = [score.get("id") for score in sorted_math_score]
                    userObjects = userObjects.order_by(
                        Case(
                            *[
                                When(id=id_val, then=pos)
                                for pos, id_val in enumerate(filtered_ids)
                            ]
                        )
                    )

            if field_name == "attempts":
                user_sat_attempts = []
                for user in userObjects:
                    if user.test_results:
                        user_sat_attempts.append(
                            {
                                "id": user.id,
                                "count": len(
                                    [
                                        ts
                                        for ts in user.test_results
                                        if ts.get("type_of_test", "") == "SAT"
                                        and ts.get("kind", "") == "actual"
                                    ]
                                ),
                            }
                        )

                sorted_attempts_lst = sorted(
                    user_sat_attempts, key=lambda item: item.get("count")
                )
                if order == "descend":
                    sorted_attempts_lst = sorted_attempts_lst[::-1]

                filtered_ids = [
                    sat_count.get("id") for sat_count in sorted_attempts_lst
                ]
                userObjects = userObjects.order_by(
                    Case(
                        *[
                            When(id=id_val, then=pos)
                            for pos, id_val in enumerate(filtered_ids)
                        ]
                    )
                )

            # if field_name == "lms_english" or field_name == "lms_math":
            #     users_session_data = []

            #     for user in userObjects:
            #         latest_assessment = UserAssessmentSession.objects.filter(
            #                 user__id=user.id, is_submitted=True
            #             ).order_by("-submitted_at").first()

            #         print('this is latest assessment', latest_assessment)

            #         if latest_assessment and latest_assessment.section_analysis_data:
            #             users_session_data.append(
            #                 {
            #                     "user": user.id,
            #                     "english": self.calculate_section_marks(
            #                         latest_assessment.section_analysis_data, "english"
            #                     ) if len(latest_assessment.section_analysis_data) > 1 else 0,
            #                     "math": self.calculate_section_marks(
            #                         latest_assessment.section_analysis_data, "math"
            #                     ) if len(latest_assessment.section_analysis_data) > 2 else 0,
            #                 }
            #             )
            #     if field_name == "lms_english":
            #         sorted_english_data = sorted(
            #             users_session_data, key=lambda item: item.get("english")
            #         )
            #         if order == "descend":
            #             sorted_english_data = sorted_english_data[::-1]

            #         filtered_ids = [
            #             session.get("user") for session in sorted_english_data
            #         ]

            #         userObjects = userObjects.order_by(
            #             Case(
            #                 *[
            #                     When(id=id_val, then=pos)
            #                     for pos, id_val in enumerate(filtered_ids)
            #                 ]
            #             )
            #         )
            #         userObjects = userObjects.filter(id__in=filtered_ids)

            return self.paginate(
                request=request,
                queryset=self.filter_queryset(userObjects.distinct()),
                on_results=lambda data: (
                    UserMinimumSerializer(data, many=True).data
                    if request.user.role == "admin"
                    else (
                        UserManagerFilterSerializer(data, many=True).data
                        if minimum
                        else UserSerializer(data, many=True).data
                    )
                ),
                extra_stats={"total_users": userObjects.distinct().count()},
            )
        except Exception as e:
            capture_exception(e)
            print("this is error ", e)
            return Response(
                {"message": "Something went wrong"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer

    def retrieve(self, request, pk):
        try:
            user = NewUserSerializer(User.objects.get(pk=pk)).data
            ops_managers = [
                {
                    "id": user.id,
                    "name": user.first_name + " " + user.last_name,
                    "email": user.email,
                    "about": user.about,
                    "profile_img": user.profile_img,
                }
                for user in User.objects.filter(id__in=user["ops_managers"])
            ]

            prep_managers = [
                {
                    "id": user.id,
                    "name": user.first_name + " " + user.last_name,
                    "email": user.email,
                    "about": user.about,
                    "profile_img": user.profile_img,
                }
                for user in User.objects.filter(id__in=user["prep_managers"])
            ]

            sso_managers = [
                {
                    "id": user.id,
                    "name": user.first_name + " " + user.last_name,
                    "email": user.email,
                    "about": user.about,
                    "profile_img": user.profile_img,
                }
                for user in User.objects.filter(id__in=user["sso_managers"])
            ]

            english_tutors = [
                {
                    "id": user.id,
                    "name": user.first_name + " " + user.last_name,
                    "email": user.email,
                    "about": user.about,
                    "profile_img": user.profile_img,
                }
                for user in User.objects.filter(id__in=user["english_tutors"])
            ]

            print("@@@@@@@@@")
            english_reading_tutors = [
                {
                    "id": user.id,
                    "name": user.first_name + " " + user.last_name,
                    "email": user.email,
                    "about": user.about,
                    "profile_img": user.profile_img,
                }
                for user in User.objects.filter(id__in=user["english_reading_tutors"])
            ]

            english_writing_tutors = [
                {
                    "id": user.id,
                    "name": user.first_name + " " + user.last_name,
                    "email": user.email,
                    "about": user.about,
                    "profile_img": user.profile_img,
                }
                for user in User.objects.filter(id__in=user["english_writing_tutors"])
            ]

            math_tutors = [
                {
                    "id": user.id,
                    "name": user.first_name + " " + user.last_name,
                    "email": user.email,
                    "about": user.about,
                    "profile_img": user.profile_img,
                }
                for user in User.objects.filter(id__in=user["math_tutors"])
            ]
            user["manager_details"] = {
                "ops_managers": ops_managers,
                "prep_managers": prep_managers,
                "sso_managers": sso_managers,
                "english_tutors": english_tutors,
                "math_tutors": math_tutors,
                "english_reading_tutors": english_reading_tutors,
                "english_writing_tutors": english_writing_tutors,
                # "tutor_type":tutor_type,
            }
            return Response(user, status=status.HTTP_200_OK)

        except Exception as e:
            print("Exception=====>", e)
            return Response(
                {
                    "success": False,
                    "status": "error",
                    "message": "Something went wrong",
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    # def set_password(self, request, pk):
    #     user = self.get_object()
    #     user.set_password(request.data.get("password"))
    #     user.save()
    #     return Response(status=status.HTTP_200_OK)

    def perform_create(self, serializer):
        serializer.save()

    def list(self, serializer):
        serializer = UserSerializer(User.objects.all(), many=True)
        return Response(serializer.data)

    def partial_update(self, request, pk):
        try:
            user = User.objects.get(pk=pk)
            slots = request.data.get("slots", user.tutor_slot)
            print("slots=====>", slots)

            total_weekly_supply = (slots * 60 * 5) / 60
            total_monthly_supply = total_weekly_supply * 4

            tutor_availability, created = TutorAvailability.objects.get_or_create(
                tutor=user
            )

            tutor_availability.tutor = user
            tutor_availability.slot = slots
            tutor_availability.total_weekly_supply = total_weekly_supply
            tutor_availability.total_monthly_supply = total_monthly_supply
            # total_monthly_load = tutor_availability.total_weekly_load * 4
            # tutor_availability.total_monthly_load = total_monthly_load

            tutor_availability.save()

            goal_post_data = request.data.get("goal_post", {})
            target_test_date = goal_post_data.get("target_test_date")

            class_start_date=request.data.get("class_start_date")#add
            print("class_sart_date====>",class_start_date)#add
            if class_start_date is not None and target_test_date is not None and class_start_date > target_test_date:#add
                return Response(
                        {"message": "class start date should not be greater than target test date"},
                        status=status.HTTP_400_BAD_REQUEST,
                    )#add
            print("goal_post_data===>", target_test_date)

            if target_test_date:
                target_test_date = datetime.strptime(
                    target_test_date, "%Y-%m-%d"
                ).date()
                core_prep_date = target_test_date - timedelta(weeks=8)

                student_availability = StudentAvailability.objects.filter(student=user)
                print("Student Availability=====>", student_availability)
                student_check = student_availability.filter(
                    Q(target_test_date_1=target_test_date)
                    | Q(target_test_date_2=target_test_date)
                    | Q(target_test_date_3=target_test_date)
                    | Q(target_test_date_4=target_test_date)
                )
                if student_check.exists():
                    pass
                elif student_availability.exists():
                    # check target_test_date max
                    student_ch = student_availability.filter(
                        Q(target_test_date_1__gte=target_test_date)
                        | Q(target_test_date_2__gte=target_test_date)
                        | Q(target_test_date_3__gte=target_test_date)
                        | Q(target_test_date_4__gte=target_test_date)
                    )
                    if student_ch.exists():
                        raise Response("Target Test Date is not valid")
                    test_tracker = 0
                    student_check = student_availability.filter(
                        target_test_date_1__isnull=False
                    )
                    if not student_check.exists():
                        test_tracker = 1

                    student_check = student_availability.filter(
                        target_test_date_2__isnull=False
                    )
                    if not student_check.exists() and test_tracker == 0:
                        test_tracker = 2

                    student_check = student_availability.filter(
                        target_test_date_3__isnull=False
                    )
                    if not student_check.exists() and test_tracker == 0:
                        test_tracker = 3

                    student_check = student_availability.filter(
                        target_test_date_4__isnull=False
                    )
                    if not student_check.exists() and test_tracker == 0:
                        test_tracker = 4

                    if test_tracker == 0:
                        raise Response("No More targeted test date assign")
                    for student_object in student_availability:

                        if test_tracker == 1:
                            student_object.target_test_date_1 = target_test_date

                        elif test_tracker == 2:
                            student_object.target_test_date_2 = target_test_date

                        elif test_tracker == 3:
                            student_object.target_test_date_3 = target_test_date

                        else:
                            student_object.target_test_date_4 = target_test_date

                        student_object.core_prep_date = core_prep_date
                        student_object.save()

                else:
                    raise Response("Student is not present in Student Availability")

            is_onboarded = request.data.get("onboarded")
            if is_onboarded is not None:
                user.is_onboarded = is_onboarded
                user.save()

            serializer = UserSerializer(user, data=request.data, partial=True)
            if serializer.is_valid():
                prep_managers = request.data.get("prep_managers", [])
                ops_managers = request.data.get("ops_managers", [])
                sso_managers = request.data.get("sso_managers", [])

                combined_ids = prep_managers + ops_managers + sso_managers
                if len(set(combined_ids)) != len(combined_ids):
                    return Response(
                        {
                            "message": "Duplicate IDs found in prep_managers, ops_managers, or sso_managers"
                        },
                        status=status.HTTP_400_BAD_REQUEST,
                    )

                school_id = request.data.get("school")

                if school_id is not None:
                    try:
                        school = School.objects.get(pk=school_id)
                        user.school = school

                    except School.DoesNotExist:
                        return Response(
                            {"message": "Invalid school ID"},
                            status=status.HTTP_400_BAD_REQUEST,
                        )

                serializer.save()
                return Response(
                    {"message": "User updated successfully"},
                    status=status.HTTP_200_OK,
                )
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            print("Exception ====> ", e)
            return Response(
                {"success": False, "error": "Something went wrong"},
                status=status.HTTP_400_BAD_REQUEST,
            )

    def get_sso_students(self, request):
        try:
            user = request.user
            print("User=====>", user.role)
            sso_id = request.query_params.get("sso_id", None)

            if user.role == "admin":
                if not sso_id:
                    return Response(
                        {
                            "success": False,
                            "status": "error",
                            "message": "SSO ID is required for admin.",
                        },
                        status=400,
                    )
            elif user.role == "sso_manager":
                sso_id = user.id
                print("SSO ID=====>", sso_id)
            else:
                sso_id = sso_id
            all_categories = ["R", "S", "T"]
            subject = request.query_params.get("subject", None)
            category_name = request.query_params.get("category", "")
            target_test_date_str = request.query_params.get("target_test_date", None)
            student_type = request.query_params.get("student_type", "both").lower()

            categories = category_name.split(",") if category_name else all_categories
            target_test_date = (
                datetime.strptime(target_test_date_str, "%Y-%m-%d").date()
                if target_test_date_str
                else None
            )

            user_queryset = User.objects.filter(sso_managers__id=sso_id)

            # Filter based on student type
            if student_type == "repeater":
                user_queryset = user_queryset.filter(isRepeater=True)
            elif student_type == "fresher":
                user_queryset = user_queryset.filter(isRepeater=False)

            if target_test_date:
                student_ids_with_target_date = (
                    StudentAvailability.objects.filter(
                        Q(target_test_date_1=target_test_date)
                        | Q(target_test_date_2=target_test_date)
                        | Q(target_test_date_3=target_test_date)
                        | Q(target_test_date_4=target_test_date)
                    )
                    .values_list("student", flat=True)
                    .distinct()
                )
                user_queryset = user_queryset.filter(
                    id__in=student_ids_with_target_date
                )

            results = []
            category_counts = {category: 0 for category in all_categories}

            for user in user_queryset:
                categories_matched = []
                if (
                    subject == "English_Writing"
                    and hasattr(user, "english_category")
                    and user.english_category.name in categories
                ):
                    categories_matched.append(user.english_category.name)
                if (
                    subject == "English_Reading"
                    and hasattr(user, "english_category")
                    and user.english_category.name in categories
                ):
                    categories_matched.append(user.english_category.name)
                elif (
                    subject == "Math"
                    and hasattr(user, "math_category")
                    and user.math_category.name in categories
                ):
                    categories_matched.append(user.math_category.name)

                if categories_matched:
                    user_info = UserMinimumSerializer(user).data
                    user_info["category"] = ", ".join(categories_matched)
                    results.append(user_info)
                    for category in categories_matched:
                        category_counts[category] += 1

            total_students = len(results)

            return Response(
                {
                    "success": True,
                    "status": "success",
                    "message": "Filtered SSO's Students.",
                    "results": results,
                    "total_students": total_students,
                    "category_counts": category_counts,
                }
            )
        except Exception as e:
            print("Exception=====>", e)
            return Response(
                {
                    "success": False,
                    "status": "error",
                    "message": "Something went wrong",
                },
                status=500,
            )

    def get_subject_tutors(self, request):
        subject = request.query_params.get("subject")
        tutors = User.objects.filter(role="tutor")

        if subject == "English":
            tutors = tutors.filter(
                Q(tutor_type="english_reading") | Q(tutor_type="english_writing")
            )

        elif subject == "Math":
            tutors = tutors.filter(tutor_type="math")

        serializer = UserMinimumSerializer(tutors, many=True)

        return Response(
            {
                "success": True,
                "status": "success",
                "message": "Tutor List",
                "results": serializer.data,
            }
        )

    def get_all_sso_managers(self, request):
        sso = User.objects.filter(role="sso_manager")
        serializers = UserMinimumSerializer(sso, many=True)

        return Response(
            {
                "success": True,
                "status": "success",
                "message": "SSO Manager's List",
                # "count": sso.count(),
                "results": serializers.data,
            }
        )

    def set_password(self, request, pk):

        user = self.get_object()
        if (
            user == request.user
            or request.user.role in ["admin", "user_manager"]
            and request.user.is_active
        ):
            user.set_password(request.data.get("password"))
            user.save()
            return Response(status=status.HTTP_200_OK)
        return Response(status=status.HTTP_401_UNAUTHORIZED)

    # def perform_create(self, serializer):
    #     serializer.save()

    # def list(self, serializer):
    #     serializer = UserSerializer(
    #         User.objects.all(), many=True
    #     )
    #     return Response(serializer.data)

    # def partial_update(self, request, pk):
    #     try:
    #         if (
    #             pk == request.user.id
    #             or request.user.role in ["admin", "user_manager", "sso_manager"]
    #         ) and request.user.is_active:
    #             user = User.objects.get(pk=pk)
    #             serializer = UserSerializer(user, data=request.data, partial=True)
    #             if serializer.is_valid():
    #                 prep_managers = request.data.get("prep_managers", [])
    #                 ops_managers = request.data.get("ops_managers", [])
    #                 sso_managers = request.data.get("sso_managers", [])

    #                 # Check for duplicate IDs
    #                 combined_ids = prep_managers + ops_managers + sso_managers
    #                 if len(set(combined_ids)) != len(combined_ids):
    #                     return Response(
    #                         {
    #                             "message": "Duplicate IDs found in prep_managers, ops_managers, or sso_managers"
    #                         },
    #                         status=status.HTTP_400_BAD_REQUEST,
    #                     )

    #                 # Update school relationship if school ID is provided
    #                 school_id = request.data.get("school", None)
    #                 if school_id:
    #                     try:
    #                         school = School.objects.get(pk=school_id)
    #                         user.school = school
    #                     except School.DoesNotExist:
    #                         return Response(
    #                             {"message": "Invalid school ID"},
    #                             status=status.HTTP_400_BAD_REQUEST,
    #                         )

    #                 serializer.save()
    #                 return Response(
    #                     {"message": "User updated successfully"},
    #                     status=status.HTTP_200_OK,
    #                 )
    #             return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    #         return Response(status=status.HTTP_403_FORBIDDEN)
    #     except Exception as e:
    #         capture_exception(e)
    #         return Response(
    #             {"message": "Something went wrong"}, status=status.HTTP_400_BAD_REQUEST
    #         )


class AllocateManagerViewSet(BaseViewset):
    def partial_update(self, request, pk):
        try:
            if request.user.is_active:
                user = User.objects.get(pk=pk)
                serializer = UserAllocateManagerSerializer(
                    user, data=request.data, partial=True
                )
                if serializer.is_valid():

                    prep_managers = request.data.get("prep_managers", [])
                    ops_managers = request.data.get("ops_managers", [])
                    sso_managers = request.data.get("sso_managers", [])

                    # Check for duplicate IDs
                    combined_ids = prep_managers + ops_managers + sso_managers
                    if len(set(combined_ids)) != len(combined_ids):
                        return Response(
                            {
                                "message": "Duplicate IDs found in prep_managers, ops_managers, or sso_managers"
                            },
                            status=status.HTTP_400_BAD_REQUEST,
                        )

                    serializer.save()

                    return Response(
                        {"message": "User updated successfully"},
                        status=status.HTTP_200_OK,
                    )
                return Response(
                    {"message": "Failed to allocate managers "},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            return Response(status=status.HTTP_401_UNAUTHORIZED)
        except Exception as e:
            print(e)
            capture_exception(e)
            return Response(
                {"message": "Something went wrong"}, status=status.HTTP_400_BAD_REQUEST
            )


class UserCustomFieldViewSet(viewsets.ModelViewSet):
    def list(self, serializer):
        serializer = UserMinimumSerializer(User.objects.all(), many=True)
        return Response(serializer.data)


class SchoolViewSet(BaseViewset):
    serializer_class = SchoolSerializer
    model = School

    def list(self, request):
        serializer = SchoolSerializer(School.objects.all(), many=True)
        return Response(serializer.data)

    def create(self, request):
        try:
            serializer = SchoolSerializer(data=request.data)

            if serializer.is_valid():
                print("serializer====>", serializer)
                serializer.save()
                return Response(
                    {"message": "School created successfully"},
                    status=status.HTTP_201_CREATED,
                )
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            print("Exception ====> ", e)
            return Response(
                {"success": False, "error": "Something went wrong"},
                status=status.HTTP_400_BAD_REQUEST,
            )


class CommentSerializer(BaseSerializer):
    class Meta:
        model = Comment
        fields = "__all__"


class CommentViewSet(BaseViewset):
    permission_classes = (AllowAny,)

    def create(self, request):
        try:
            student_id = request.data.get("StudentId")
            comment = request.data.get("comment")
            type = request.data.get("type")
            student = User.objects.get(pk=student_id)

            Comment.objects.create(
                user=student,
                comment=comment,
                type=type,
            )
            return Response(
                {"success": "Comment saved successfully"},
                status=status.HTTP_201_CREATED,
            )

        except Exception as e:
            print("Exception ====> ", e)
            return Response(
                {"success": False, "error": "Something went wrong"},
                status=status.HTTP_400_BAD_REQUEST,
            )

    def get_by_id(self, request, user_id):
        try:
            user = User.objects.get(pk=user_id)
            comments = Comment.objects.filter(user=user)
            serializer = CommentSerializer(comments, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Exception as e:
            print("Exception ====> ", e)
            return Response(
                {"success": False, "error": "Something went wrong"},
                status=status.HTTP_400_BAD_REQUEST,
            )


class TargetTestDateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Target_Test_Date
        fields = "__all__"


class TargetTestDateViewSet(BaseViewset):
    def get_target_test_dates(self, request):
        try:
            test_obj = Target_Test_Date.objects.filter(date__gt=date.today())
            serializer = TargetTestDateSerializer(test_obj, many=True)
            return Response(
                {
                    "success": True,
                    "status": status.HTTP_200_OK,
                    "payload": serializer.data,
                }
            )
        except Exception as e:
            return Response({"status": status.HTTP_404_NOT_FOUND, "error": str(e)})


class AllocateCounselorViewSet(BaseViewset):
    permission_classes = (IsPlatformAdmin,)

    def get(self, request, pk):
        try:
            counselor = User.objects.get(pk=pk)
        except Exception as e:
            raise APIException(e)

        if counselor.role == "counselor":
            users = User.objects.filter(counselors__in=[counselor.id])
            return Response(
                {
                    "message": "success",
                    "users": UserMinimumSerializer(users, many=True).data,
                }
            )
        raise APIException(
            "Selected user is not counselor anymore",
            status.HTTP_400_BAD_REQUEST,
        )

    def partial_update(self, request, pk):
        try:
            counselor = User.objects.get(pk=pk)
        except Exception as e:
            raise APIException(e)
        students = request.data.get("users", [])
        if counselor.role == "counselor":
            users = User.objects.filter(pk__in=students)
            for user in users:
                counselors = [c.id for c in user.counselors.all()]
                print("this is counselors", counselors)
                if not counselor.id in counselors:
                    counselors.append(counselor.id)

                print("this is counselor two", counselors)

                user.counselors.set(counselors)
                user.save()

            return Response(
                {"message": "Users Allocated to this counselor"},
                status=status.HTTP_200_OK,
            )
        raise APIException(
            "Selected user is not counselor anymore",
            status.HTTP_400_BAD_REQUEST,
        )

    def delete(self, request, pk, user):
        try:
            counselor = User.objects.get(pk=pk)
            user = User.objects.get(pk=user)
            user.counselors.remove(counselor)
            user.save()
            return Response({"message": "User removed"}, status=status.HTTP_200_OK)
        except Exception as e:
            raise APIException(e, status.HTTP_400_BAD_REQUEST)
