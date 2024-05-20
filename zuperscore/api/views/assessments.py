import uuid
import time
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from rest_framework import serializers
from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework import status
from zuperscore.api.views.subjects import SubjectNodeSerializer
from zuperscore.db.models import User
from zuperscore.db.models.assessments import (
    Option,
    Question,
    QuestionNode,
    SectionQuestion,
    UserAssessmentSession,
    Group,
    PracticeSet,
    GroupUser,
    PracticeSetAssessment,
    AssessmentTags,
    TestAllocationLogger,
    TestAllocationPracticeSetAssessment,
    TestAllocationGroupUser,
    WeeklyProgress,
)
from zuperscore.db.models import (
    AssessmentSection,
    Assessment,
)
from zuperscore.api.views.people import UserSerializer, UserMinimumSerializer
from zuperscore.db.models.subjects import SubjectNode
from zuperscore.utils.paginator import BasePaginator
from .base import BaseSerializer, BaseViewset
from rest_framework.views import APIView
from django_filters import rest_framework as filters
from rest_framework import filters as rest_filters
from django.db.models import Case, When
from django.utils import timezone
from datetime import timedelta
from datetime import datetime
from django.db.models import Q
from math import sqrt
from math import exp
from math import ceil
import random
from zuperscore.db.models.assessments import UserAttempt
from rest_framework.permissions import AllowAny
from zuperscore.bgtasks.migrate_from_pscale import migrate_from_pscale
import csv
from django.http.response import StreamingHttpResponse
from zuperscore.utils.csv_write import WriteToCSV
from zuperscore.db.models.library import (
    Domain,
    Topic,
    SubTopic,
    MegaDomain,
    ReasonForError,
    FileAsset,
)
from zuperscore.api.views.library import FileAssetSerializer

# from background_task import background
import os
from celery import shared_task  # need to install
from io import StringIO
import boto3
from django.core.files import File
from django.core.files.base import ContentFile
from zuperscore.api.permissions import *
from rest_framework import permissions


class AssessmentSectionSerializer(BaseSerializer):
    class Meta:
        model = AssessmentSection
        fields = (
            "id",
            "name",
            "description",
            "instructions",
            "is_timed",
            "time_limit",
            "tools",
            "pre_screen",
            "post_screen",
            "sequence",
            "layout",
            "data",
            "timers",
            "bubble_sheet_data",
            "bubble_sheet_questions",
            "bubble_sheet_answers",
            "switching_route",
            "type",
        )


class AssessmentSerializer(BaseSerializer):
    # assessment_sessions = FileAssetSerializer(many=True)
    class Meta:
        model = Assessment
        fields = "__all__"


class AssessmentMinimumSerializer(BaseSerializer):
    class Meta:
        model = Assessment
        fields = (
            "id",
            "name",
            "kind",
            "state",
        )


class AssessmentSectionMinimumSerializer(BaseSerializer):
    assessment = AssessmentMinimumSerializer(read_only=True)

    class Meta:
        model = AssessmentSection
        fields = (
            "id",
            "name",
            "type",
            "assessment",
        )


class OptionSerializer(BaseSerializer):
    class Meta:
        model = Option
        fields = "__all__"


class QuestionSerializer(BaseSerializer):
    options = OptionSerializer(many=True, read_only=True)

    class Meta:
        model = Question
        fields = (
            "id",
            "title",
            "type",
            "created_at",
            "updated_at",
            "data",
            "timers",
            "is_active",
            "feedback",
            "assets",
            "score",
            "files",
            "options",
            "passage",
            "explanation",
            "feedback",
            "approvers_difficulty",
            "statistical_difficulty",
            "used_in",
            "decision",
            "sourced_from",
            "remarks",
            "created_by",
            "irt_a",
            "irt_b",
            "irt_c",
            "blume_taxonomy",
            "created_by",
            # tagging
            "exam",
            "subject",
            "mega_domain",
            "domain",
            "topic",
            "sub_topic",
            "calculator",
        )


class QuestionReviewerSerializer(QuestionSerializer):
    section = serializers.SerializerMethodField()

    class Meta(QuestionSerializer.Meta):
        fields = QuestionSerializer.Meta.fields + ("section",)

    def get_section(self, obj):
        section_id = self.context.get("section_id")
        if section_id:
            try:
                section = AssessmentSection.objects.get(id=section_id)
                return AssessmentSectionMinimumSerializer(section).data
            except AssessmentSection.DoesNotExist:
                return None
        return None


class SectionQuestionSerializer(BaseSerializer):
    class Meta:
        model = SectionQuestion
        fields = "__all__"


class SectionWithQuestionSerializer(BaseSerializer):
    question = QuestionSerializer(read_only=True)

    class Meta:
        model = SectionQuestion
        fields = (
            "id",
            "question",
            "sequence",
            "layout",
            "data",
        )
        depth = 2


class AssessmentWithSectionsSerializer(BaseSerializer):
    assessment_sections = AssessmentSectionSerializer(many=True, read_only=True)

    class Meta:
        model = Assessment
        fields = (
            "id",
            "name",
            "description",
            "instructions",
            "cover_url",
            "link",
            "data",
            "kind",
            "state",
            "assessment_sections",
        )


class UserAssessmentSessionSerializer(serializers.ModelSerializer):
    assessment_detail = AssessmentSerializer(read_only=True, source="assessment")

    class Meta:
        model = UserAssessmentSession
        fields = (
            "id",
            "assessment",
            "user",
            "data",
            "is_submitted",
            "is_reviewed",
            "is_started",
            "started_at",
            "submitted_at",
            "reviewed_at",
            "total_time",
            "total_marks",
            "total_questions",
            "total_correct",
            "total_incorrect",
            "total_answered",
            "total_unanswered",
            "total_visited",
            "total_unvisited",
            "total_unattempted",
            "section_analysis_data",
            "total_correct_qids",
            "total_incorrect_qids",
            "total_unanswered_qids",
            "total_visited_qids",
            "total_unvisited_qids",
            "total_answered_qids",
            "is_pscale_success",
            "pscale_data",
            "section_question_data",
            "section_info_data",
            "section_time_data",
            "section_marks_data",
            "generated_by",
            "is_resume_enabled",
            "state",
            "scheduled_at",
            "assessment_detail",
            "created_at",
            "updated_at",
        )


class UserAssessmentSessionMinimumSerializer(BaseSerializer):
    assessment_detail = AssessmentMinimumSerializer(read_only=True, source="assessment")
    user_detail = UserMinimumSerializer(read_only=True, source="user")

    class Meta:
        model = UserAssessmentSession
        fields = (
            "id",
            "user_detail",
            "is_submitted",
            "is_reviewed",
            "is_started",
            "started_at",
            "submitted_at",
            "reviewed_at",
            "total_questions",
            "total_correct",
            "section_analysis_data",
            "state",
            "is_resume_enabled",
            "assessment_detail",
            "created_at",
            "updated_at",
        )


class AssessmentTagsSerializer(BaseSerializer):
    class Meta:
        model = AssessmentTags
        fields = "__all__"


class UserAttemptSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserAttempt
        fields = "__all__"

class GroupSerializer(BaseSerializer):
    class Meta:
        model = Group
        fields = "__all__"

class GroupUserSerializer(BaseSerializer):
    class Meta:
        model = GroupUser
        fields = "__all__"

class PracticeSetSerializer(BaseSerializer):
    class Meta:
        model = PracticeSet
        fields = "__all__"

class PracticeSetAssessmentSerializer(BaseSerializer):
    class Meta:
        model = PracticeSetAssessment
        fields = "__all__"

class TestAllocationLoggerSerializer(serializers.ModelSerializer):
    class Meta:
        model = TestAllocationLogger
        fields = "__all__"


class TestAllocationPracticeSetAssessmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = TestAllocationPracticeSetAssessment
        fields = "__all__"


class TestAllocationGroupUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = TestAllocationGroupUser
        fields = "__all__"



# Viewsets
class AssessmentSectionViewSet(BaseViewset):
    serializer_class = AssessmentSectionSerializer
    model = AssessmentSection

    def list(self, request):
        serializer = AssessmentSectionSerializer(
            AssessmentSection.objects.all(), many=True
        )
        return Response(serializer.data)


class AssessmentViewSet(BaseViewset, BasePaginator):
    permission_classes = (IsPlatformAdmin,)
    serializer_class = AssessmentSerializer
    model = Assessment

    def list(self, request):
        kind = request.GET.get("kind")
        archive = request.GET.get("archive", "")
        user = request.GET.get("user")
        subject = request.GET.get("subject", None)
        mega_domain = request.GET.get("mega_domain", None)
        minimum = True if request.GET.get("is_minimum", False) == "true" else False

        archive = True if archive.lower() == "true" else False

        if user:
            if not User.objects.filter(pk=user).exists():
                return Response(
                    {"message": "user not found"}, status=status.HTTP_404_NOT_FOUND
                )

        assessments = Assessment.objects.filter(
            state="ARCHIVED" if archive else "ACTIVE"
        ).order_by("name")

        if kind:
            assessments = assessments.filter(kind=kind)
        # if archive:
        #     assessments = assessments.filter(state="ARCHIVED")
        if subject and subject != "all":
            assessments = assessments.filter(subject__id=subject)
        if mega_domain and mega_domain != "all":
            assessments = assessments.filter(mega_domain__id=mega_domain)

        count = assessments.count()
        serializer = (
            AssessmentMinimumSerializer(assessments, many=True)
            if minimum
            else AssessmentSerializer(assessments, many=True)
        )

        # for assessment in serializer.data:
        #     if UserAssessmentSession.objects.filter(assessment__id=assessment['id'], user__id=user).count() > 0:
        #         assessment['assignment_state'] = "assigned"
        #     else:
        #         assessment['assignment_state'] = "unassigned"
        if user:
            user_assessment_sessions = UserAssessmentSession.objects.filter(
                assessment__id__in=[assessment["id"] for assessment in serializer.data],
                user__id=user,
            ).values("assessment__id")

            assigned_assessment_ids = {
                session["assessment__id"] for session in user_assessment_sessions
            }

            for assessment in serializer.data:
                if assessment["id"] in assigned_assessment_ids:
                    assessment["assignment_state"] = "assigned"
                else:
                    assessment["assignment_state"] = "unassigned"
        return Response(
            {"count": count, "assessments": serializer.data}, status=status.HTTP_200_OK
        )

    def get_assessment(self, request, pk):
        assessment = Assessment.objects.get(pk=pk)
        serializer = AssessmentSerializer(assessment).data
        tags = [
            AssessmentTagsSerializer(AssessmentTags.objects.get(id=tag_id)).data
            for tag_id in serializer.get("tags", None)
        ]
        serializer["tags"] = tags
        return Response(serializer)

    def with_sections(self, request, pk):
        sections = AssessmentSection.objects.filter(assessment_id=pk)
        section_serializer = AssessmentSectionSerializer(sections, many=True)
        serializer = AssessmentSerializer(Assessment.objects.get(id=pk))
        return Response(
            {
                "assessment": serializer.data,
                "sections": section_serializer.data,
            },
            status=status.HTTP_200_OK,
        )

    def create_section(self, request, pk):
        serializer = AssessmentSectionSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(assessment_id=pk)
            return Response(serializer.data)
        return Response(serializer.errors)

    def user_assessments_allots(self, request, pk):
        user_id = request.data.get("user_id", False)
        state = request.data.get("state", False)
        user_assessment_sessions = UserAssessmentSession.objects.filter(
            assessment_id=pk
        )
        if user_id:
            user_assessment_sessions = user_assessment_sessions.filter(user_id=user_id)
        if state:
            user_assessment_sessions = user_assessment_sessions.filter(state=state)
        return self.paginate(
            request=request,
            queryset=user_assessment_sessions,
            on_results=lambda user_assessment_sessions: UserAssessmentSessionSerializer(
                user_assessment_sessions, many=True
            ).data,
            extra_stats={"total_sessions": user_assessment_sessions.count()},
        )

    def user_list(self, request, pk):
        if request.user.role == "tutor":
            user_ids = UserAssessmentSession.objects.filter(
                Q(assessment_id=pk)
                & (
                    Q(user__english_tutor__in=[request.user])
                    | Q(user__math_tutor__in=[request.user])
                )
            ).values_list("user_id", flat=True)
        elif request.user.role in ["manager", "prep_manager", "sso_manager"]:
            user_ids = UserAssessmentSession.objects.filter(
                Q(assessment_id=pk)
                & (
                    Q(user__prep_managers__in=[request.user.id])
                    | Q(user__ops_managers__in=[request.user.id])
                    | Q(user__sso_managers__in=[request.user.id])
                )
            ).values_list("user_id", flat=True)

        else:
            user_ids = UserAssessmentSession.objects.filter(
                assessment_id=pk
            ).values_list("user_id", flat=True)

        users = User.objects.filter(id__in=user_ids)
        serializer = UserSerializer(users, many=True)
        return Response(serializer.data)

    def filter_queryset(self, queryset):
        for backend in list(self.filter_backends):
            queryset = backend().filter_queryset(self.request, queryset, self)
        return queryset

    def user_assessment_bool(self, request, pk, user_id):
        user = User.objects.get(id=request.user.id)
        if user.initial_assessments:
            initial_assessments = user.initial_assessments
            found = next(
                (item for item in initial_assessments if item["assessment_id"] == pk),
                None,
            )
            if found:
                return Response(
                    {"message": "success", "assessment": found},
                    status=status.HTTP_200_OK,
                )
            else:
                return Response(
                    {"message": "success", "assessment": None},
                    status=status.HTTP_200_OK,
                )
        else:
            return Response(
                {"message": "success", "assessment": None}, status=status.HTTP_200_OK
            )


class QuestionViewSet(BaseViewset):
    permission_classes = ~IsNotStudentOrGuest
    serializer_class = QuestionSerializer
    model = Question

    def list(self, request):
        serializer = QuestionSerializer(Question.objects.all(), many=True)
        return Response(serializer.data)


class FetchQuestionViewSet(BaseViewset):

    def questions_by_ids(self, request):
        question_ids = request.data.get("question_ids")
        preserved = Case(
            *[When(pk=pk, then=pos) for pos, pk in enumerate(question_ids)]
        )
        questions = (
            Question.objects.filter(pk__in=question_ids)
            .prefetch_related("options")
            .order_by(preserved)
        )
        serializer = QuestionSerializer(questions, many=True)
        return Response(
            {"message": "success", "questions": serializer.data},
            status=status.HTTP_200_OK,
        )


class AssessmentSectionQuestionViewSet(BaseViewset):

    serializer_class = SectionQuestionSerializer
    model = SectionQuestion

    def list(self, request):
        serializer = SectionQuestionSerializer(SectionQuestion.objects.all(), many=True)
        return Response(serializer.data)


class OptionViewSet(BaseViewset):
    permission_classes = (
        IsPlatformAdmin,
        IsTypist,
        read_only(IsUserManager),
        read_only(IsManager),
        read_only(IsTutor),
        read_only(IsCounselor),
        read_only(IsParent),
        read_only(IsStudent),
        read_only(IsGuest),
    )
    serializer_class = OptionSerializer
    model = Option

    def list(self, request):
        serializer = OptionSerializer(Option.objects.all(), many=True)
        return Response(serializer.data)


class SectionViewSet(BaseViewset):
    permission_classes = (
        IsPlatformAdmin,
        IsTypist,
        IsManager,
        IsTutor,
    )
    serializer_class = AssessmentSectionSerializer
    model = AssessmentSection

    def with_questions(self, request, pk):
        questions = SectionQuestion.objects.filter(section_id=pk)
        question_serializer = SectionWithQuestionSerializer(questions, many=True)
        serializer = AssessmentSectionSerializer(AssessmentSection.objects.get(id=pk))
        question_list = [
            next(
                question
                for question in question_serializer.data
                if question["question"]["id"] == q_id
            )
            for q_id in {
                question["question"]["id"] for question in question_serializer.data
            }
        ]
        return Response(
            {
                "section": serializer.data,
                "questions": question_list,
            },
            status=status.HTTP_200_OK,
        )

    def create_question(self, request, pk):
        serializer = QuestionSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
        else:
            return Response(serializer.errors)
        try:
            section_question = SectionQuestion(
                question_id=serializer.data["id"], section_id=pk
            )
            section_question.save()
            section_question_serializer = SectionWithQuestionSerializer(
                section_question
            )
            return Response(
                section_question_serializer.data, status=status.HTTP_201_CREATED
            )
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)


class SectionQuestionViewSet(BaseViewset):
    permission_classes = (
        IsPlatformAdmin,
        IsManager,
        IsTutor,
    )
    serializer_class = SectionQuestionSerializer
    model = SectionQuestion

    def list(self, request):
        section_question = SectionQuestion.objects.all()
        serializer = SectionQuestionSerializer(section_question, many=True)
        return Response(serializer.data)


class QuestionNodeSerializer(BaseSerializer):
    class Meta:
        model = QuestionNode
        fields = "__all__"


class QuestionNodeBridgeSerializer(BaseSerializer):
    question = QuestionSerializer(read_only=True)

    class Meta:
        model = QuestionNode
        fields = (
            "id",
            "question",
            "sequence",
            "data",
        )


class QuestionNodeViewset(BaseViewset, BasePaginator):
    permission_classes = (IsPlatformAdmin, IsTypist)
    serializer_class = QuestionNodeSerializer
    queryset = QuestionNode.objects.all()
    model = QuestionNode
    # filter_backends = (res.DjangoFilterBackend,)

    def create(self, request, question_id):
        question_tag = QuestionNode.objects.create(
            node_id=request.data["node_id"], question_id=question_id
        )
        serializer = QuestionNodeSerializer(question_tag)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def destroy(self, request, question_id, node_id):
        question_tag = QuestionNode.objects.get(
            question_id=question_id, node_id=node_id
        )
        question_tag.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    def partial_update(self, request, question_id, node_id):
        question_tag = QuestionNode.objects.get(
            question_id=question_id, node_id=node_id
        )
        serializer = QuestionNodeSerializer(
            question_tag, data=request.data, partial=True
        )
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def question_list(self, request, node_id):
        nodes = QuestionNode.objects.filter(node_id=node_id)
        serializer = QuestionNodeBridgeSerializer(nodes, many=True)
        return Response(serializer.data)

    # def question_list(self, request, node_id):
    #     question_ids = QuestionNode.objects.filter(node_id=node_id).values_list('question_id', flat=True)
    #     questions = Question.objects.filter(pk__in=question_ids)
    #     return self.paginate(
    #         request=request,
    #         queryset=questions,
    #         on_results=lambda users: QuestionSerializer(users, many=True).data,
    #         extra_stats={
    #             'total': questions.count(),
    #         }
    #     )


class GenerateQuestionForSection(APIView):
    permission_classes = (IsPlatformAdmin, IsTypist)

    def post(self, request):
        section_id = request.data.get("section_id")
        # number_of_quesions = request.data.get('number_of_quesions')
        # section = AssessmentSection.objects.get(id=section_id)
        # nodes = section.topics['data']
        # question_ids = .filter(node_id__in=nodes).values_list('question_id', flat=True)
        question_ids = request.data.get("questions")
        section_question = []
        sequence = 65535
        for question_id in question_ids:
            sequence = sequence + 65535
            section_question.append(
                SectionQuestion(
                    section_id=section_id,
                    question_id=question_id,
                    sequence=sequence,
                )
            )
        # print(len(section_question))
        SectionQuestion.objects.bulk_create(section_question, ignore_conflicts=True)
        return Response(status=status.HTTP_201_CREATED)


class ChildNodesEndpoint(APIView):
    permission_classes = (IsPlatformAdmin, IsTypist)

    def get(self, request, pk):
        try:
            node = SubjectNode.objects.get(id=pk)
            nodes = node.get_descendants()
            serializer = SubjectNodeSerializer(nodes, many=True)
            return Response(serializer.data)
        except:
            return Response(
                {"message": "node not found"}, status=status.HTTP_400_BAD_REQUEST
            )


class OneLevelChildNodesEndpoint(APIView):
    permission_classes = (IsPlatformAdmin, IsTypist)

    def get(self, request, pk):
        try:
            node = SubjectNode.objects.get(id=pk)
            nodes = node.get_children()
            serializer = SubjectNodeSerializer(nodes, many=True)
            return Response(serializer.data)
        except:
            return Response(
                {"message": "node not found"}, status=status.HTTP_400_BAD_REQUEST
            )


class SearchQuestionEndpoint(APIView, BasePaginator):
    permission_classes = (IsPlatformAdmin,)

    def post(self, request):
        query = request.data.get("query")
        nodes = request.data.get("nodes")
        # difficulty = request.data.get('difficulty')
        if nodes:
            question_ids = QuestionNode.objects.filter(node_id__in=nodes).values_list(
                "question_id", flat=True
            )
            questions = Question.objects.filter(
                title__icontains=query, pk__in=question_ids
            )
        else:
            questions = Question.objects.filter(title__icontains=query)
        # serializer = QuestionSerializer(questions, many=True)
        return self.paginate(
            request=request,
            queryset=questions,
            on_results=lambda data: QuestionSerializer(data, many=True).data,
        )


class UserAssessmentSessionViewSet(BaseViewset, BasePaginator):
    permission_classes = (
        IsPlatformAdmin,
        IsManager,
        IsTutor,
        read_only(IsStudent),
        read_only(IsGuest),
        read_only(IsParent),
        read_only(IsCounselor),
    )
    serializer_class = UserAssessmentSessionSerializer
    model = UserAssessmentSession

    filterset_fields = (
        "assessment",
        "user",
        "total_marks",
        "is_submitted",
        "is_reviewed",
        "scheduled_at",
        "state",
    )

    filter_backends = (filters.DjangoFilterBackend,)

    def student_assessment_sessions(self, request, user_id, assessment_id):
        user_assessment_sessions = UserAssessmentSession.objects.filter(
            user_id=user_id, assessment_id=assessment_id
        )
        serializer = UserAssessmentSessionSerializer(
            user_assessment_sessions, many=True
        )
        return Response(
            {"user_assessment_sessions": serializer.data}, status=status.HTTP_200_OK
        )

    def retrieve(self, request, pk):
        try:
            user_assessment_session = UserAssessmentSession.objects.get(pk=pk)
            serializer = UserAssessmentSessionSerializer(user_assessment_session)
            assessment_serializer = AssessmentWithSectionsSerializer(
                Assessment.objects.get(pk=user_assessment_session.assessment.id)
            )
            return Response(
                {
                    "user_assessment_session": serializer.data,
                    "assessment": assessment_serializer.data,
                },
                status=status.HTTP_200_OK,
            )
        except Exception:
            return Response(
                {"message": "not found"}, status=status.HTTP_400_BAD_REQUEST
            )

    def filter_queryset(self, queryset):
        for backend in list(self.filter_backends):
            queryset = backend().filter_queryset(self.request, queryset, self)
        return queryset

    def list(self, request):
        order_by = request.GET.get("order_by")
        kind = request.GET.get("kind", None)
        subject = request.GET.get("subject", None)
        mega_domain = request.GET.get("mega_domain", False)

        user_assessment_sessions = UserAssessmentSession.objects.all()

        if kind:
            user_assessment_sessions = user_assessment_sessions.filter(
                assessment__kind=kind
            )
            if subject:
                user_assessment_sessions = user_assessment_sessions.filter(
                    assessment__subject=subject
                )
            if mega_domain:
                # print("inside the mega domain")
                user_assessment_sessions = user_assessment_sessions.filter(
                    assessment__mega_domain=mega_domain
                )

        if order_by == "submitted_at":
            user_assessment_sessions = user_assessment_sessions.exclude(
                submitted_at__isnull=True
            ).order_by("-submitted_at")
        elif order_by == "scheduled_at":
            user_assessment_sessions = user_assessment_sessions.exclude(
                scheduled_at__isnull=True
            ).order_by("-scheduled_at")
        elif order_by == "in_progress":
            user_assessment_sessions = user_assessment_sessions.filter(
                state="IN_PROGRESS"
            ).order_by("-created_at")
        elif order_by == "unscheduled":
            user_assessment_sessions = user_assessment_sessions.exclude(
                scheduled_at__isnull=False
            ).order_by("-created_at")
        else:
            user_assessment_sessions = user_assessment_sessions.extra(
                select={"is_null": "submitted_at IS NULL"},
                order_by=["is_null", "-submitted_at", "-is_submitted"],
            )

        if request.user.role == "tutor":
            user_assessment_sessions = user_assessment_sessions.filter(
                Q(user__english_tutors__in=[request.user.id])
                | Q(user__math_tutors__in=[request.user.id])
            ).distinct()
        elif request.user.role == "manager":
            user_assessment_sessions = user_assessment_sessions.filter(
                Q(user__prep_managers__in=[request.user.id])
                | Q(user__ops_managers__in=[request.user.id])
                | Q(user__sso_managers__in=[request.user.id])
            ).distinct()
        elif request.user.role == "parent":
            user_assessment_sessions = user_assessment_sessions.filter(
                Q(user__parents__in=[request.user.id])
            ).distinct()
        elif request.user.role == "counselor":
            user_assessment_sessions = user_assessment_sessions.filter(
                Q(user__counselors__in=[request.user.id])
            ).distinct()

        return self.paginate(
            request=request,
            queryset=self.filter_queryset(user_assessment_sessions),
            on_results=lambda user_assessment_sessions: UserAssessmentSessionSerializer(
                user_assessment_sessions, many=True
            ).data,
            # extra_stats={
            #     'total_sessions': user_assessment_sessions.count(),
            #     # 'result_test' : UserAssessmentSessionSerializer(user_assessment_sessions, many=True).data,
            # },
        )


class DownloadUserAssessment(BaseViewset):
    permission_classes = (~IsUserManager, ~IsGuest, ~IsTypist)

    def get_section_analysis_data(self, section_analysis, index):
        try:
            return (
                str(section_analysis[index]["results"]["correct_answers"])
                + " out of "
                + str(section_analysis[index]["results"]["total_no_of_questions"])
            )
        except Exception as e:
            return "-"

    def list(self, request):
        order_by = request.GET.get("order_by")
        assessment = request.GET.get("assessment", None)
        user = request.GET.get("user", None)

        if assessment and user:
            if order_by == "submitted_at":
                user_assessment_sessions = (
                    UserAssessmentSession.objects.filter(
                        assessment__id=assessment, user__id=user
                    )
                    .exclude(submitted_at__isnull=True)
                    .order_by("-submitted_at", "-is_submitted")
                )
            elif order_by == "scheduled_at":
                user_assessment_sessions = (
                    UserAssessmentSession.objects.filter(
                        assessment__id=assessment, user__id=user
                    )
                    .exclude(scheduled_at__isnull=True)
                    .order_by("-scheduled_at", "-scheduled_at")
                )
            elif order_by == "in_progress":
                user_assessment_sessions = user_assessment_sessions.filter(
                    state="IN_PROGRESS"
                ).order_by("-created_at")
            elif order_by == "unscheduled":
                user_assessment_sessions = user_assessment_sessions.exclude(
                    scheduled_at__isnull=False
                ).order_by("-created_at")
            else:
                user_assessment_sessions = UserAssessmentSession.objects.filter(
                    assessment__id=assessment, user__id=user
                ).extra(
                    select={"is_null": "submitted_at IS NULL"},
                    order_by=["is_null", "-submitted_at", "-is_submitted"],
                )

        elif assessment:
            if order_by == "submitted_at":
                user_assessment_sessions = (
                    UserAssessmentSession.objects.filter(assessment__id=assessment)
                    .exclude(submitted_at__isnull=True)
                    .order_by("-submitted_at", "-is_submitted")
                )
            elif order_by == "scheduled_at":
                user_assessment_sessions = (
                    UserAssessmentSession.objects.filter(assessment__id=assessment)
                    .exclude(scheduled_at__isnull=True)
                    .order_by("-scheduled_at", "-scheduled_at")
                )
            else:
                user_assessment_sessions = UserAssessmentSession.objects.filter(
                    assessment__id=assessment
                ).extra(
                    select={"is_null": "submitted_at IS NULL"},
                    order_by=["is_null", "-submitted_at", "-is_submitted"],
                )

        elif user:
            if order_by == "submitted_at":
                user_assessment_sessions = (
                    UserAssessmentSession.objects.filter(user__id=user)
                    .exclude(submitted_at__isnull=True)
                    .order_by("-submitted_at", "-is_submitted")
                )
            elif order_by == "scheduled_at":
                user_assessment_sessions = (
                    UserAssessmentSession.objects.filter(user__id=user)
                    .exclude(scheduled_at__isnull=True)
                    .order_by("-scheduled_at", "-scheduled_at")
                )
            else:
                user_assessment_sessions = UserAssessmentSession.objects.filter(
                    user__id=user
                ).extra(
                    select={"is_null": "submitted_at IS NULL"},
                    order_by=["is_null", "-submitted_at", "-is_submitted"],
                )

        else:
            return Response(
                {"message": "Please specify assessment id  or user id"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        user_assessment_sessions = user_assessment_sessions.values(
            "id",
            "user__id",
            "user__first_name",
            "user__last_name",
            "assessment__id",
            "assessment__name",
            "assessment__kind",
            "total_questions",
            "total_correct",
            "is_submitted",
            "is_reviewed",
            "reviewed_at",
            "submitted_at",
            "started_at",
            "state",
            "scheduled_at",
            "section_analysis_data",
        )

        if len(user_assessment_sessions) > 0:
            row_one = [
                "id",
                "user id",
                "name",
                "assessment id",
                "assessment name",
                "assessment kind",
                "started at",
                "submitted at",
                "analysis",
                "analyzed at",
                "read & write module 1",
                "read & write module 2",
                "math & module 1",
                "math & module 2",
                "scaled score rw",
                "scaled score math",
                "total score",
            ]
            row_two = []
            for session in user_assessment_sessions:
                row_two.append(
                    [
                        session["id"],
                        session["user__id"],
                        session["user__first_name"] + " " + session["user__last_name"],
                        session["assessment__id"],
                        session["assessment__name"],
                        session["assessment__kind"],
                        session["started_at"],
                        session["submitted_at"],
                        "analyzed" if session["is_reviewed"] else "not analyzed",
                        session["reviewed_at"],
                        self.get_section_analysis_data(
                            session["section_analysis_data"], 0
                        ),
                        self.get_section_analysis_data(
                            session["section_analysis_data"], 1
                        ),
                        self.get_section_analysis_data(
                            session["section_analysis_data"], 2
                        ),
                        self.get_section_analysis_data(
                            session["section_analysis_data"], 3
                        ),
                        "-",
                        "-",
                        str(session["total_correct"])
                        + " out of "
                        + str(session["total_questions"]),
                    ]
                )

            rows = [row_one] + list(row_two)
            pseudo_buffer = WriteToCSV()
            writer = csv.writer(pseudo_buffer)
            response = StreamingHttpResponse(
                (writer.writerow(row) for row in rows), content_type="text/csv"
            )
            filename = f"test-report_{int(time.time())}"
            response["Content-Disposition"] = f'attachment; filename="{filename}.csv"'
            return response
        else:
            return Response(
                {"message": "Response is empty"}, status=status.HTTP_404_NOT_FOUND
            )


class GenerateAssessmentSessionView(APIView):
    permission_classes = (IsPlatformAdmin, IsTutor, IsManager, IsUserManager)

    def post(self, request):
        user_id = request.data.get("user")
        assessment_id = request.data.get("assessment")
        schedule_at = request.data.get("scheduled_at", None)
        schedule_at = (
            datetime.strptime(schedule_at, "%Y-%m-%dT%H:%M:%S.%f%z")
            if schedule_at
            else None
        )
        try:
            _ = Assessment.objects.get(pk=assessment_id)
        except Assessment.DoesNotExist:
            return Response(
                {"message": "assessment not found"}, status=status.HTTP_404_NOT_FOUND
            )

        try:
            assessment_sections = AssessmentSection.objects.filter(
                assessment_id=assessment_id
            ).values_list(
                "id",
                "name",
                "description",
                "type",
                "data",
                "time_limit",
                "timers",
                "instructions",
            )
            section_question_data = {}
            section_info_data = {}
            for (
                section_id,
                name,
                description,
                type,
                data,
                time_limit,
                timers,
                instruction,
            ) in assessment_sections:
                sqs = (
                    SectionQuestion.objects.filter(section_id=section_id)
                    .values_list("question_id", "sequence")
                    .order_by("sequence")
                )
                info = {
                    "name": name,
                    "description": description,
                    "instructions": instruction,
                    "data": data,
                    "time_limit": time_limit,
                    "timers": timers,
                    "type": type,
                }
                question_ids = (
                    SectionQuestion.objects.filter(section_id=section_id)
                    .values_list("question_id", flat=True)
                    .order_by("sequence")
                )
                section_question_data[section_id] = list(question_ids)
                section_info_data[section_id] = info
            # You can do this by pusblishing the assessment and then using the published assessment
            user_assessment_session = UserAssessmentSession.objects.create(
                user_id=user_id,
                assessment_id=assessment_id,
                section_question_data=section_question_data,
                section_info_data=section_info_data,
                scheduled_at=schedule_at,
            )

            serializer = UserAssessmentSessionSerializer(user_assessment_session)
            return Response(
                {"message": "success", "user_assessment_session": serializer.data},
                status=status.HTTP_200_OK,
            )
        except Exception as e:
            print(e)
            return Response({"message": "failed"}, status=status.HTTP_400_BAD_REQUEST)


class GenerateBulkAssessmentSessionView(APIView):
    permission_classes = (IsPlatformAdmin, IsTutor, IsManager, IsUserManager)

    def post(self, request, pk):
        if request.user.is_active and request.user.role not in [
            "parent",
            "user",
            "couselor",
        ]:
            bulk_assessment_data = request.data
            session_list = []
            for assessment in bulk_assessment_data:
                if Assessment.objects.filter(id=assessment["assessment_id"]).exists():
                    try:
                        assessment_sections = AssessmentSection.objects.filter(
                            assessment_id=assessment["assessment_id"]
                        ).values_list(
                            "id",
                            "name",
                            "description",
                            "type",
                            "data",
                            "time_limit",
                            "timers",
                            "instructions",
                        )
                        section_question_data = {}
                        section_info_data = {}
                        for (
                            section_id,
                            name,
                            description,
                            type,
                            data,
                            time_limit,
                            timers,
                            instruction,
                        ) in assessment_sections:
                            info = {
                                "name": name,
                                "description": description,
                                "instructions": instruction,
                                "data": data,
                                "time_limit": time_limit,
                                "timers": timers,
                                "type": type,
                            }
                            question_ids = (
                                SectionQuestion.objects.filter(section_id=section_id)
                                .values_list("question_id", flat=True)
                                .order_by("sequence")
                            )
                            section_question_data[section_id] = list(question_ids)
                            section_info_data[section_id] = info
                        user_assessment_session = UserAssessmentSession.objects.create(
                            user_id=pk,
                            assessment_id=assessment["assessment_id"],
                            section_question_data=section_question_data,
                            section_info_data=section_info_data,
                            scheduled_at=(
                                datetime.strptime(
                                    assessment["scheduled_at"], "%Y-%m-%dT%H:%M:%S.%f%z"
                                )
                                if assessment["scheduled_at"]
                                else None
                            ),
                        )
                        session_list.append(user_assessment_session)
                    except Exception as e:
                        print(e)
                        return Response(
                            {"message": "failed"}, status=status.HTTP_400_BAD_REQUEST
                        )

            serializer = UserAssessmentSessionSerializer(session_list, many=True)
            return Response(
                {"message": "success", "user_assessment_session": serializer.data},
                status=status.HTTP_200_OK,
            )

        return Response(
            {"message": "Unauthorized action"}, status=status.HTTP_401_UNAUTHORIZED
        )


class RenderAssessmentSessionView(APIView):
    permission_classes = (~IsCounselor, ~IsParent, ~IsTypist)

    def post(self, request):
        user_assessment_session_id = request.data.get("uas_id")
        assessment_section_id = str(request.data.get("section_id"))
        try:
            user_assessment_session = UserAssessmentSession.objects.get(
                pk=user_assessment_session_id
            )
            assessment_section = AssessmentSection.objects.get(pk=assessment_section_id)
            if assessment_section.type == "ADAPTIVE":
                previous_section_id = request.data.get("previous_section_id")
                # print("adaptive")
                previous_section_id = str(previous_section_id)
                prev_section_score = user_assessment_session.section_marks_data.get(
                    previous_section_id
                )
                score_switcher = assessment_section.switching_route
                # print("prev section score", prev_section_score)
                # put it in the matching bucket.
                # print("score switcher", score_switcher)
                for rule in score_switcher:
                    min = rule["min"]
                    max = rule["max"]
                    folder = rule["folder_id"]
                    if min <= prev_section_score <= max:
                        folder_id = folder
                qids = (
                    QuestionNode.objects.filter(node_id=folder_id)
                    .values_list("question_id", flat=True)
                    .order_by("sequence")
                )
                # print("i pick", folder_id, "qids", qids)
                section_questions_data = user_assessment_session.section_question_data
                section_questions_data.update({assessment_section_id: list(qids)})
                user_assessment_session.section_question_data = section_questions_data
                user_assessment_session.save()
            else:
                qids = user_assessment_session.section_question_data.get(
                    assessment_section_id, []
                )
            if not qids:
                return Response(
                    {"message": "no questions available"},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            preserved = Case(*[When(pk=pk, then=pos) for pos, pk in enumerate(qids)])
            questions = (
                Question.objects.filter(pk__in=qids)
                .prefetch_related("options")
                .order_by(preserved)
            )
            serializer = QuestionSerializer(questions, many=True)
            assessment_section_serializer = AssessmentSectionSerializer(
                assessment_section
            )
            return Response(
                {
                    "message": "success",
                    "section": assessment_section_serializer.data,
                    "questions": serializer.data,
                },
                status=status.HTTP_200_OK,
            )
        except UserAssessmentSession.DoesNotExist:
            return Response(
                {"message": "user assessment session not found"},
                status=status.HTTP_404_NOT_FOUND,
            )
        except Exception as e:
            print(e)
            return Response({"message": e}, status=status.HTTP_400_BAD_REQUEST)


class UserAssessmentSessionSectionQuestionsView(APIView):
    permission_classes = (~IsTypist, ~IsParent, ~IsCounselor)

    def post(self, request):
        uas_id = request.data.get("uas_id")
        section_id = str(request.data.get("section_id"))
        try:
            user_assessment_session = UserAssessmentSession.objects.get(pk=uas_id)
            section_question_data = user_assessment_session.section_question_data
            qids = section_question_data[section_id]
            preserved = Case(*[When(pk=pk, then=pos) for pos, pk in enumerate(qids)])
            questions = (
                Question.objects.filter(pk__in=qids)
                .prefetch_related("options")
                .order_by(preserved)
            )
            serializer = QuestionSerializer(questions, many=True)
            assessment_section_serializer = AssessmentSectionSerializer(
                AssessmentSection.objects.get(pk=section_id)
            )
            return Response(
                {
                    "message": "success",
                    "section": assessment_section_serializer.data,
                    "questions": serializer.data,
                },
                status=status.HTTP_200_OK,
            )
        except Exception as e:
            print(e)
            return Response({"message": "failed"}, status=status.HTTP_400_BAD_REQUEST)


class UserAllocatedAssessmentsEndpoint(APIView, BasePaginator):
    permission_classes = (IsNotStudentOrGuest, ~IsParent, ~IsGuest)

    def get(self, request, pk):
        kind = request.GET.get("kind", "MOCK")
        assessment_id = request.GET.get("assessment_id", False)
        subject = request.GET.get("subject", False)
        mega_domain = request.GET.get("mega_domain", False)

        user_assessment_sessions = UserAssessmentSession.objects.filter(
            user=pk
        ).order_by("-created_at")
        if assessment_id:
            user_assessment_sessions = user_assessment_sessions.filter(
                assessment_id=assessment_id
            )

        if kind:
            user_assessment_sessions = user_assessment_sessions.filter(
                assessment__kind=kind
            )

        if subject:
            user_assessment_sessions = user_assessment_sessions.filter(
                assessment__subject__id=subject
            )

        if mega_domain:
            user_assessment_sessions = user_assessment_sessions.filter(
                assessment__mega_domain__id=mega_domain
            )

        return self.paginate(
            request=request,
            queryset=user_assessment_sessions,
            on_results=lambda user_assessment_sessions: UserAssessmentSessionSerializer(
                user_assessment_sessions, many=True
            ).data,
            extra_stats={"total_sessions": user_assessment_sessions.count()},
        )


class UserAllocatedAssessmentsDashboardEndpoint(APIView):
    permission_classes = (IsPlatformAdmin, ~IsNotStudentOrGuest)

    def get(self, request):
        now = timezone.now()
        assessment_id = request.GET.get("assessment_id", False)
        if assessment_id:
            sessions = UserAssessmentSession.objects.filter(
                user=request.user, assessment_id=assessment_id
            ).order_by("-created_at")
        else:
            sessions = UserAssessmentSession.objects.filter(
                user=request.user, scheduled_at__gte=now
            ).order_by("-created_at")[:5]
        serializer = UserAssessmentSessionSerializer(sessions, many=True)
        return Response(
            {"message": "success", "sessions": serializer.data},
            status=status.HTTP_200_OK,
        )


class UserAllocatedAssessmentCheckEndpoint(APIView):
    permission_classes = (~IsTypist, ~IsParent, ~IsCounselor, ~IsGuest)

    def get(self, request):
        assessment_id = request.GET.get("assessment_id", False)
        nowm5 = timezone.now() - timedelta(minutes=5)  # 855
        nowp5 = timezone.now() + timedelta(minutes=5)  # 905
        sessions = UserAssessmentSession.objects.filter(
            user=request.user,
            assessment_id=assessment_id,
            scheduled_at__gte=nowm5,
            scheduled_at__lte=nowp5,
        ).order_by("-created_at")[:5]
        if sessions:
            serializer = UserAssessmentSessionSerializer(sessions, many=True)
            return Response(
                {"message": "success", "state": True, "sessions": serializer.data},
                status=status.HTTP_200_OK,
            )
        else:
            return Response(
                {"message": "success", "state": False}, status=status.HTTP_200_OK
            )


class UserAllocatedAssessmentMistakesEndpoint(APIView):
    permission_class = (
        ~IsTypist,
        ~IsGuest,
    )

    def get(self, request):
        all_sessions = UserAssessmentSession.objects.filter(
            user=request.user
        ).values_list("assessment_id", "pscale_data")
        return Response(
            {"message": "success", "all_sessions": all_sessions},
            status=status.HTTP_200_OK,
        )


class UserAssessmentSessionByDateEndpoint(APIView):
    permission_classes = (IsPlatformAdmin,)

    def get(self, request):
        date = request.GET.get("date", False)
        today = timezone.now()
        if date:
            # 01-01-2020 format
            date = datetime.strptime(date, "%d-%m-%Y").date()
            sessions = UserAssessmentSession.objects.filter(
                user=request.user, scheduled_at__date=date
            ).order_by("-created_at")
            serializer = UserAssessmentSessionSerializer(sessions, many=True)
            return Response(
                {"message": "success", "sessions": serializer.data},
                status=status.HTTP_200_OK,
            )
        else:
            sessions = UserAssessmentSession.objects.filter(
                user=request.user, scheduled_at__gte=today
            ).order_by("-created_at")
            serializer = UserAssessmentSessionSerializer(sessions, many=True)
            return Response(
                {"message": "success", "sessions": serializer.data},
                status=status.HTTP_200_OK,
            )


class UserAssessmentsEndpoint(APIView, BasePaginator):
    permmission_classes = (IsStudent, IsGuest, IsManager, IsTutor)

    search_fields = ("assessment__name",)

    filter_backends = (
        filters.DjangoFilterBackend,
        rest_filters.SearchFilter,
    )

    def filter_queryset(self, queryset):
        for backend in list(self.filter_backends):
            queryset = backend().filter_queryset(self.request, queryset, self)
        return queryset

    def get(self, request):
        upcoming = request.GET.get("upcoming", False)
        unscheduled = request.GET.get("unscheduled", False)
        taken = request.GET.get("taken", False)
        in_progress = request.GET.get("in_progress", False)
        kind = request.GET.get("kind", False)
        user_id = request.user.id
        subject = request.GET.get("subject", False)
        mega_domain = request.GET.get("mega_domain", False)

        user_assessment_sessions = UserAssessmentSession.objects.filter(
            user_id=user_id, assessment__kind=kind
        ).order_by("-created_at")
        # print("im comming here only")
        if subject:
            user_assessment_sessions = user_assessment_sessions.filter(
                assessment__subject__id=subject
            )
        if mega_domain:
            user_assessment_sessions = user_assessment_sessions.filter(
                assessment__mega_domain__id=mega_domain
            )
        if upcoming:
            nowm5 = timezone.now() - timedelta(minutes=15)  # 855
            user_assessment_sessions = user_assessment_sessions.filter(
                user_id=user_id,
                scheduled_at__gte=nowm5,
                assessment__kind=kind,
                state="UNTOUCHED",
            ).order_by("scheduled_at")
        if unscheduled:
            user_assessment_sessions = user_assessment_sessions.filter(
                user_id=user_id,
                scheduled_at=None,
                assessment__kind=kind,
                state="UNTOUCHED",
            ).order_by("-created_at")
        if in_progress:
            user_assessment_sessions = user_assessment_sessions.filter(
                user_id=user_id,
                assessment__kind=kind,
                state__in=["STARTED", "IN_PROGRESS"],
            ).order_by("-created_at")
        if taken:
            user_assessment_sessions = user_assessment_sessions.filter(
                Q(user_id=user_id),
                Q(state__in=["COMPLETED", "ANALYSED"]),
                Q(assessment__kind=kind),
            ).order_by("-created_at")

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
            queryset=self.filter_queryset(user_assessment_sessions),
            on_results=lambda user_assessment_sessions: UserAssessmentSessionSerializer(
                user_assessment_sessions, many=True
            ).data,
            extra_stats={"total_sessions": user_assessment_sessions.count()},
        )


# create a list of 1601 zeros
# This is an array of theta (z-scores) from -4.0 to +4.0 at decimal place to 0.01, so there are 1601 values [-4.000, -3.999, … 3.999, 4.000].
# This is the array that will be used to calculate the likelihood of the examinee’s response vector for each theta value.
# The theta_array is used to calculate the likelihood of the examinee’s response vector for each theta value.


theta_array = [0] * 800
p_array = [0] * 800
scored_p_array = [0] * 800

# create a 801 element list ranging from -4.0 to 4.0   Note that Python is zero-referenced index

for i in range(800):
    theta_array[i] = -4.0 + (i * 0.01)
# print(theta_array)


def item_response_function(theta_array, irt_a, irt_b, irt_c, scored_response_vector):

    # create a list with random values of 1 and 0 of length 40

    # scored_response_vector =  random.choices([0, 1], k=40)
    # print(scored_response_vector)
    number_items = len(scored_response_vector)

    # Initialize LikeArray and BayesArray for this examinee
    sigma = 1.0  # double, this is a constant
    mu = 0.0  # double, this is a constant

    like_array = [1] * 800
    bayes_array = [
        exp(-((theta_array[column] - mu) * (theta_array[column] - mu) / (2 * sigma)))
        / sqrt(2 * 3.141529 * sigma)
        for column in range(800)
    ]

    # print(bayes_array)

    # Determine if NonMixed = true

    non_mixed = False  # default
    raw_score = sum(scored_response_vector)

    if raw_score == 0 or raw_score == number_items:
        non_mixed = True
        max_like_column = 0  # default value for non_mixed case
    else:
        max_like_column = None

    # Calculate the LikeArray and BayesArray
    # print("number of items: ", number_items)  # for QA
    for item in range(0, number_items):

        # print("Item: ", item, "   Response", scored_response_vector[item])  # for QA
        for theta_column in range(0, 800):
            # print(irt_c[item])

            p = irt_c[item] + (1 - irt_c[item]) * (
                (exp(1.702 * irt_a[item] * (theta_array[theta_column] - irt_b[item])))
                / (
                    1
                    + exp(
                        1.702 * irt_a[item] * (theta_array[theta_column] - irt_b[item])
                    )
                )
            )
            p_array[theta_column] = p
            # like_array[theta_column] *= p
            scored_p_array[theta_column] = p
            if scored_response_vector[item] == 0:
                scored_p_array[theta_column] = 1 - p  # turn into Q
            like_array[theta_column] *= scored_p_array[theta_column]
            bayes_array[theta_column] *= scored_p_array[theta_column]

        # print(p_array)  # for QA
        # print(scored_p_array)  # for QA

    # Find the value of Theta which has the highest likelihood (MaxLike)
    # print(theta_array)  # for QA
    # print(like_array)  # for QA
    max_like = 0

    for theta_column in range(0, 800):

        if not non_mixed:
            if like_array[theta_column] > max_like:
                max_like = like_array[theta_column]
                max_like_column = theta_column
            else:
                if bayes_array[theta_column] > max_like:
                    max_like = bayes_array[theta_column]
                    max_like_column = theta_column
        else:
            if bayes_array[theta_column] > max_like:
                max_like = bayes_array[theta_column]
                max_like_column = (
                    max_like_column  # use default value for non_mixed case
                )

    current_theta = max_like_column / 100 - 4.01  # Finds theta value from -4 to +4
    # print("Max like column", max_like_column)
    # print("Current Theta: ", current_theta)
    return current_theta


class ComputeScaledScoreEndpoint(APIView):
    permission_classes = (IsNotStudentOrGuest, ~IsParent, ~IsCounselor, ~IsTypist)

    def post(self, request):
        assessment = Assessment.objects.get(pk=request.data.get("assessment_id"))
        english_sigma = assessment.english_sigma if assessment.english_sigma else 1
        english_xbar = assessment.english_xbar if assessment.english_xbar else 0
        math_sigma = assessment.math_sigma if assessment.math_sigma else 1
        math_xbar = assessment.math_xbar if assessment.math_xbar else 0
        english = request.data.get("english")
        math = request.data.get("math")

        english_items = list(english.keys())
        math_items = list(math.keys())

        # print("english items", english_items)
        # print("math items", math_items)

        english_answers = list(english.values())
        math_answers = list(math.values())

        # print("english answers", english_answers)
        # print("math answers", math_answers)

        math_preserved = Case(
            *[When(pk=pk, then=pos) for pos, pk in enumerate(math_items)]
        )
        english_preserved = Case(
            *[When(pk=pk, then=pos) for pos, pk in enumerate(english_items)]
        )

        m_irt_a = list(
            Question.objects.filter(pk__in=math_items)
            .values_list("irt_a", flat=True)
            .order_by(math_preserved)
        )
        m_irt_b = list(
            Question.objects.filter(pk__in=math_items)
            .values_list("irt_b", flat=True)
            .order_by(math_preserved)
        )
        m_irt_c = list(
            Question.objects.filter(pk__in=math_items)
            .values_list("irt_c", flat=True)
            .order_by(math_preserved)
        )

        e_irt_a = list(
            Question.objects.filter(pk__in=english_items)
            .values_list("irt_a", flat=True)
            .order_by(english_preserved)
        )
        e_irt_b = list(
            Question.objects.filter(pk__in=english_items)
            .values_list("irt_b", flat=True)
            .order_by(english_preserved)
        )
        e_irt_c = list(
            Question.objects.filter(pk__in=english_items)
            .values_list("irt_c", flat=True)
            .order_by(english_preserved)
        )

        # print("e_irt", e_irt_a, e_irt_b, e_irt_c)
        # print("m_irt", m_irt_a, m_irt_b, m_irt_c)

        e_theta = item_response_function(
            theta_array, e_irt_a, e_irt_b, e_irt_c, english_answers
        )
        english_scaled_score = e_theta * english_sigma + english_xbar

        m_theta = item_response_function(
            theta_array, m_irt_a, m_irt_b, m_irt_c, math_answers
        )
        math_scaled_score = m_theta * math_sigma + math_xbar
        english_scaled_score = round(english_scaled_score, -1)
        math_scaled_score = round(math_scaled_score, -1)
        if math_scaled_score > 800:
            math_scaled_score = 800
        if english_scaled_score > 800:
            english_scaled_score = 800
        return Response(
            {
                "status": "success",
                "message": "Scaled scores computed successfully.",
                "english_items": english_items,
                "math_items": math_items,
                "english_answers": english_answers,
                "math_answers": math_answers,
                "m_irt_a": m_irt_a,
                "m_irt_b": m_irt_b,
                "m_irt_c": m_irt_c,
                "e_irt_a": e_irt_a,
                "e_irt_b": e_irt_b,
                "e_irt_c": e_irt_c,
                "e_theta": e_theta,
                "m_theta": m_theta,
                "english": english_scaled_score,
                "math": math_scaled_score,
                "total": math_scaled_score + english_scaled_score,
            }
        )


class UserAssessmentAttemptEndpoint(BaseViewset):
    permission_classes = (
        ~IsTypist,
        read_only(IsParent),
        read_only(IsCounselor),
        read_only(IsUserManager),
    )
    serializer_class = UserAttemptSerializer

    def list(self, request, pk):
        queryset = UserAttempt.objects.filter(session_id=pk)
        serializer = UserAttemptSerializer(queryset, many=True)
        return Response(serializer.data)

    def post(self, request, pk):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid(raise_exception=True):
            user_attempt_saved = serializer.save(session_id=pk)
        return Response(
            {
                "status": "success",
                "message": "User attempt saved successfully.",
                "user_attempt": UserAttemptSerializer(user_attempt_saved).data,
            }
        )


class UserAssessmentAttemptViewSet(BaseViewset):
    permission_classes = (
        ~IsTypist,
        read_only(IsParent),
        read_only(IsCounselor),
        read_only(IsUserManager),
    )
    serializer_class = UserAttemptSerializer
    model = UserAttempt

    def list(self, request):
        serializer = UserAttemptSerializer(UserAttempt.objects.all(), many=True)
        return Response(serializer.data)


class AllAssessmentSessionEndpoint(APIView):
    permission_classes = (IsPlatformAdmin,)

    def get(self, request):
        assessment_id = request.GET.get("assessment_id")
        values = (
            UserAssessmentSession.objects.filter(assessment_id=assessment_id)
            .filter(pscale_data__isnull=False)
            .filter(Q(state="IN_PROGRESS") | Q(state="ANALYSED") | Q(state="COMPLETED"))
            .values("id", "pscale_data", "assessment", "user")
        )
        return Response({"data": values}, status=status.HTTP_200_OK)


class CreateUserAttemptBulk(APIView):
    permission_classes = (AllowAny,)

    def post(self, request):
        assessment_id = request.data.get("assessment_id")
        data = request.data.get("attempts")
        migration_type = request.data.get("migration_type")

        if migration_type != "DESKTOP":
            UserAttempt.objects.filter(
                assessment_id=assessment_id, stat="MIGRATED"
            ).delete()
        else:
            migration_type = "MIGRATED"

        user_attempt_objects = []
        for attempt in data:
            obj = UserAttempt(
                session_id=attempt["session"],
                user_id=attempt["user"],
                section_id=attempt["section"],
                question_id=attempt["question"],
                type=attempt["type"],
                is_bookmark=attempt["is_bookmark"],
                data=attempt["data"],
                extra=attempt["extra"],
                info=attempt["info"],
                time_taken=attempt["time_taken"],
                assessment_id=attempt["assessment"],
                is_visited=attempt["is_visited"],
                masked_options=attempt["masked_options"],
                is_answered=attempt["is_answered"],
                analysis_data=attempt["analysis_data"],
                stat=migration_type,
            )
            user_attempt_objects.append(obj)
        UserAttempt.objects.bulk_create(user_attempt_objects, batch_size=10000)
        return Response({"data": "success"}, status=status.HTTP_200_OK)


def flatten_list(lst):
    result = []
    for item in lst:
        if isinstance(item, list):
            result.extend(flatten_list(item))
        else:
            result.append(item)
    return result


class MistakeAnalyserEndpoint(BasePaginator, APIView):
    permission_class = (~IsTypist, ~IsGuest)
    # def add_attempts(self, results, request):
    #     question_ids = []
    #     for result in results:
    #         question_ids.append(result.get("id"))
    #     attempts = UserAttemptSerializer(
    #         UserAttempt.objects.filter(id__in=question_ids, user=request.user), many=True
    #     ).data
    #     for question in results:
    #         # Find all attempts for the question
    #         question_attempts = [
    #             attempt
    #             for attempt in attempts
    #             if attempt.get("question") == question.get("id")
    #         ]
    #         question["attempts"] = question_attempts

    #     return results

    def find_section_id(self, data, qid):
        for entry in data:
            for item in entry:
                if qid in item["qid"]:
                    return item["section_id"]
        return None

    def SerializerQuestion(self, questions, data):
        data_list = []
        for quest in questions:

            data_list.append(
                QuestionReviewerSerializer(
                    quest, context={"section_id": self.find_section_id(data, quest.id)}
                ).data
            )

        return data_list

    def post(self, request):
        user = request.data.get("user")
        strategy = request.data.get("strategy")
        view = request.data.get("view", 1)

        user = user if user else request.user

        if strategy == "all":
            sessions = (
                UserAssessmentSession.objects.filter(assessment__kind="MOCK", user=user)
                .filter(Q(state="ANALYSED") | Q(state="COMPLETED"))
                .order_by("-created_at")
            )
        elif strategy == "last_five":
            sessions = (
                UserAssessmentSession.objects.filter(assessment__kind="MOCK", user=user)
                .filter(Q(state="ANALYSED") | Q(state="COMPLETED"))
                .order_by("-created_at")[:5]
            )
        elif strategy == "last_two":
            sessions = (
                UserAssessmentSession.objects.filter(assessment__kind="MOCK", user=user)
                .filter(Q(state="ANALYSED") | Q(state="COMPLETED"))
                .order_by("-created_at")[:2]
            )
        elif strategy == "last_eight":
            sessions = (
                UserAssessmentSession.objects.filter(assessment__kind="MOCK", user=user)
                .filter(Q(state="ANALYSED") | Q(state="COMPLETED"))
                .order_by("-created_at")[:8]
            )
        else:
            assessment_id = request.data.get("assessment_id")
            sessions = (
                UserAssessmentSession.objects.filter(
                    assessment_id=assessment_id, user=user
                )
                .filter(Q(state="ANALYSED") | Q(state="COMPLETED"))
                .order_by("-created_at")
            )

        total_incorrect_qids_list = sessions.values_list(
            "total_incorrect_qids", flat=True
        )
        total_unanswered_qids_list = sessions.values_list(
            "total_unanswered_qids", flat=True
        )
        total_correct_qid_list = sessions.values_list("total_correct_qids", flat=True)
        total_visited_qids_list = sessions.values_list("total_visited_qids", flat=True)
        total_unvisited_qids_list = sessions.values_list(
            "total_unvisited_qids", flat=True
        )
        total_answered_qids_list = sessions.values_list(
            "total_answered_qids", flat=True
        )
        sessions_ids = sessions.values_list("id", flat=True)
        # print('session ids', sessions_ids)

        qids = []
        if view == 3:
            total_sessions = (
                list(total_unanswered_qids_list)
                + list(total_answered_qids_list)
                + list(total_unvisited_qids_list)
                + list(total_visited_qids_list)
            )
        elif view == 2:
            total_sessions = list(total_correct_qid_list)
        else:
            total_sessions = list(total_incorrect_qids_list) + list(
                total_unanswered_qids_list
            )

        for session in total_sessions:
            if isinstance(session, list) and len(session) > 0:
                session_qids = [d["qid"] for d in session]
                # print('this is session', session)
                qids.append(session_qids)

        all_qids = list(set(flatten_list(qids)))

        questions_filterset = {}
        questions_filterset["id__in"] = all_qids
        if request.data.get("exam"):
            questions_filterset["exam"] = request.data.get("exam")
        if request.data.get("subject"):
            questions_filterset["subject"] = request.data.get("subject")
        if request.data.get("mega_domain"):
            questions_filterset["mega_domain"] = request.data.get("mega_domain")
        if request.data.get("domain"):
            questions_filterset["domain"] = request.data.get("domain")
        if request.data.get("topic"):
            questions_filterset["topic"] = request.data.get("topic")
        if request.data.get("subtopic"):
            questions_filterset["sub_topic"] = request.data.get("subtopic")
        if request.data.get("difficulty"):
            questions_filterset["approvers_difficulty"] = request.data.get("difficulty")

        questions = Question.objects.filter(**questions_filterset)
        question_ids = list(questions.values_list("id", flat=True))
        attempts = UserAttempt.objects.filter(
            user=user,
            question_id__in=question_ids,
            session_id__in=sessions_ids,
        )

        return self.paginate(
            request=request,
            queryset=questions,
            on_results=lambda questions: self.SerializerQuestion(
                questions, total_sessions
            ),
            extra_stats={
                "attempts": UserAttemptSerializer(attempts, many=True).data,
                "total_questions": questions.count(),
            },
            # controller=lambda questions: self.add_attempts(questions, request)
        )


class CreateUserAttemptBulkAsync(APIView):
    permission_classes = IsPlatformAdmin

    def post(self, request):
        assessment_id = request.data.get("assessment_id")
        data = request.data.get("attempts")
        migrate_from_pscale.delay(assessment_id, data)
        return Response({"data": "success"}, status=status.HTTP_200_OK)


class AssessmentSessionCSCDownloadEndpoint(APIView):
    permission_classes = (IsPlatformAdmin,)

    def get(self, request):
        assessment_id = request.GET.get("assessment_id")
        sessions = (
            UserAssessmentSession.objects.filter(assessment_id=assessment_id)
            .filter(Q(state="ANALYSED") | Q(state="COMPLETED"))
            .order_by("-created_at")
        )
        serializer = UserAssessmentSessionSerializer(sessions, many=True)
        return Response(
            {"message": "success", "sessions": serializer.data},
            status=status.HTTP_200_OK,
        )


# student performance
def find_object_in_list(value, list_value):
    return_value = False
    for x in list_value:
        if x["question_id"] == value["question_id"]:
            return_value = True
            break
    return return_value


def flatten_list_with_object(lst):
    result = []
    for item in lst:
        if isinstance(item, list):
            result.extend(flatten_list_with_object(item))
        elif item not in result:  # Check if the item is not already in the result
            result.append(item)
    return result


class StudentMyPerformanceAnalyticsEndpoint(APIView):
    permission_classes = (~IsTypist, ~IsGuest)
    def post(self, request):
        user = request.data.get("user")
        strategy = request.data.get("strategy")
        subject = request.data.get("subject")  # reading_and_writing or math
        output = request.data.get("output")  # topic or difficulty or time_taken
        topic = request.data.get("topic")
        difficulty = request.data.get("difficulty")
        time_taken = request.data.get("time_taken")
        reason_for_error = request.data.get("reason_for_error")

        user = user if user else request.user
        strategy_limits = {
            "all": None,
            "last_five": 5,
            "last_two": 2,
            "last_eight": 8,
        }

        if strategy and subject and output:
            limit = strategy_limits.get(strategy)
            sessions = UserAssessmentSession.objects.filter(
                assessment__kind="MOCK", user=user
            )
            sessions = sessions.filter(
                Q(state="ANALYSED") | Q(state="COMPLETED")
            ).order_by("-created_at")

            if limit is not None:
                sessions = sessions[:limit]

            all_questions = []
            correct_questions = []
            wrong_questions = []
            un_answered_questions = []
            un_visited_questions = []
            all_question_attempts = []

            for session in sessions:
                if session.section_info_data:
                    # all questions
                    section_question_data = session.section_question_data
                    # correct questions
                    total_correct_qids = session.total_correct_qids
                    # wrong questions
                    total_incorrect_qids = session.total_incorrect_qids
                    # un answered questions
                    total_unanswered_qids = session.total_unanswered_qids
                    # un visited questions
                    total_unvisited_qids = session.total_unvisited_qids
                    # analysis
                    section_analysis_data = session.section_analysis_data

                    for section in session.section_info_data:
                        section_id = section
                        section_detail = session.section_info_data[section_id]
                        if (
                            section_detail
                            and section_detail.get("data", None)
                            and section_detail["data"]["group_by"]
                        ):
                            # section_group_by = section_detail['data']['group_by']
                            # if section_group_by == subject:
                            # handling all questions
                            if section_question_data:
                                for section_questions in section_question_data:
                                    if section_id == section_questions:
                                        question_ids = [
                                            question
                                            for question in section_question_data[
                                                section_questions
                                            ]
                                        ]
                                        is_correct = False
                                        is_wrong = False
                                        is_attempted = False
                                        is_visited = True
                                        all_questions.append(
                                            [
                                                {
                                                    "session": session.id,
                                                    "assessment_id": session.assessment,
                                                    "section": int(section_id),
                                                    "question_id": question,
                                                    "is_correct": is_correct,
                                                    "is_wrong": is_wrong,
                                                    "is_attempted": is_attempted,
                                                    "is_visited": is_visited,
                                                    "attempt_id": None,
                                                    "time_taken": 0,
                                                    "analysis_data_type": None,
                                                }
                                                for question in question_ids
                                            ]
                                        )

                            # handling all correct questions in an section
                            if (
                                total_correct_qids
                                and isinstance(total_correct_qids, list)
                                and len(total_correct_qids) > 0
                            ):
                                for section in total_correct_qids:
                                    if section_id == section.get("section_id", None):
                                        question_ids = [
                                            question for question in section["qid"]
                                        ]
                                        correct_questions.append(
                                            [
                                                {
                                                    "session": session.id,
                                                    "section": int(section_id),
                                                    "question_id": question,
                                                }
                                                for question in question_ids
                                            ]
                                        )

                            # handling all wrong questions in an section
                            if (
                                total_incorrect_qids
                                and isinstance(total_incorrect_qids, list)
                                and len(total_incorrect_qids) > 0
                            ):
                                for section in total_incorrect_qids:
                                    if section_id == section.get("section_id", None):
                                        question_ids = [
                                            question for question in section["qid"]
                                        ]
                                        wrong_questions.append(
                                            [
                                                {
                                                    "session": session.id,
                                                    "section": int(section_id),
                                                    "question_id": question,
                                                }
                                                for question in question_ids
                                            ]
                                        )

                            # handling all unanswered questions in an section
                            if (
                                total_unanswered_qids
                                and isinstance(total_unanswered_qids, list)
                                and len(total_unanswered_qids) > 0
                            ):
                                for section in total_unanswered_qids:
                                    if section_id == section.get("section_id", None):
                                        question_ids = [
                                            question for question in section["qid"]
                                        ]
                                        un_answered_questions.append(
                                            [
                                                {
                                                    "session": session.id,
                                                    "section": int(section_id),
                                                    "question_id": question,
                                                }
                                                for question in question_ids
                                            ]
                                        )

                            # handling all unvisited questions in an section
                            if (
                                total_unvisited_qids
                                and isinstance(total_unvisited_qids, list)
                                and len(total_unvisited_qids) > 0
                            ):
                                for section in total_unvisited_qids:
                                    if section_id == section.get("section_id", None):
                                        question_ids = [
                                            question for question in section["qid"]
                                        ]
                                        un_visited_questions.append(
                                            [
                                                {
                                                    "session": session.id,
                                                    "section": int(section_id),
                                                    "question_id": question,
                                                }
                                                for question in question_ids
                                            ]
                                        )

                            # handling all correct questions attempts
                            if section_analysis_data:
                                for analysis_data in section_analysis_data:
                                    if int(section_id) == int(analysis_data["id"]):
                                        question_attempts = [
                                            question
                                            for question in analysis_data["results"][
                                                "attempts"
                                            ]
                                        ]
                                        all_question_attempts.append(
                                            [
                                                {
                                                    "session": session.id,
                                                    "section": int(section_id),
                                                    "question_id": attempt["id"],
                                                    "attempt_id": (
                                                        attempt["attempt_id"]
                                                        if "attempt_id" in attempt
                                                        else None
                                                    ),
                                                    "time_taken": attempt["result"][
                                                        "time_taken"
                                                    ]["total_time"],
                                                }
                                                for attempt in question_attempts
                                            ]
                                        )
            all_questions = flatten_list_with_object(all_questions)
            correct_questions = flatten_list_with_object(correct_questions)
            wrong_questions = flatten_list_with_object(wrong_questions)
            un_answered_questions = flatten_list_with_object(un_answered_questions)
            un_visited_questions = flatten_list_with_object(un_visited_questions)
            all_question_attempts = flatten_list_with_object(all_question_attempts)

            for question in all_questions:
                question_stat = {
                    "is_correct": False,
                    "is_wrong": False,
                    "is_attempted": False,
                }
                if any(
                    (
                        x["question_id"] == question["question_id"]
                        and x["session"] == question["session"]
                        and x["section"] == question["section"]
                    )
                    for x in correct_questions
                ):
                    question_stat["is_correct"] = True
                if any(
                    (
                        x["question_id"] == question["question_id"]
                        and x["session"] == question["session"]
                        and x["section"] == question["section"]
                    )
                    for x in wrong_questions
                ):
                    question_stat["is_wrong"] = True
                if any(
                    (
                        x["question_id"] == question["question_id"]
                        and x["session"] == question["session"]
                        and x["section"] == question["section"]
                    )
                    for x in un_answered_questions
                ):
                    question_stat["is_attempted"] = True
                if any(
                    (
                        x["question_id"] == question["question_id"]
                        and x["session"] == question["session"]
                        and x["section"] == question["section"]
                    )
                    for x in un_visited_questions
                ):
                    question_stat["is_visited"] = False
                question.update(question_stat)

            for question in all_questions:
                current_attempt = [
                    attempt
                    for attempt in all_question_attempts
                    if attempt["question_id"] == question["question_id"]
                    and attempt["session"] == question["session"]
                    and attempt["section"] == question["section"]
                    and (
                        question["is_correct"] == True
                        or question["is_wrong"] == True
                        or question["is_attempted"] == True
                    )
                ]
                if current_attempt and len(current_attempt) > 0:
                    question.update(
                        {
                            "time_taken": ceil(current_attempt[0]["time_taken"]),
                            "attempt_id": current_attempt[0]["attempt_id"],
                        }
                    )

            # fetching all questions for topic and difficulty
            all_question_ids = [question["question_id"] for question in all_questions]
            all_question_details = Question.objects.filter(
                id__in=all_question_ids
            ).values("id", "subject", "topic", "approvers_difficulty")
            # print(all_question_details)
            # all_question_details_serializer = QuestionSerializer(all_question_details, many=True).data
            all_question_details_mapping = {
                question["id"]: question for question in all_question_details
            }
            for question in all_questions:
                current_question = all_question_details_mapping.get(
                    question["question_id"]
                )
                if current_question:
                    question.update(
                        {
                            "subject": current_question.get("subject", None),
                            "topic": current_question.get("topic", None),
                            "difficulty": current_question.get(
                                "approvers_difficulty", None
                            ),
                        }
                    )

            # filtering all questions via subject
            # for question in all_questions:
            #     print('question -> ', question['question_id'], ' -> ', question['subject'], ' -> ', question['assessment_id'])

            all_subject_questions = [
                question
                for question in all_questions
                if question.get("subject", None) == int(subject)
            ]
            all_subject_questions_ids = [
                question["question_id"] for question in all_subject_questions
            ]
            all_questions = [
                q
                for q in all_questions
                if any(
                    int(question) == int(q["question_id"])
                    for question in all_subject_questions_ids
                )
            ]
            correct_questions = [
                q
                for q in correct_questions
                if any(
                    int(question) == int(q["question_id"])
                    for question in all_subject_questions_ids
                )
            ]
            wrong_questions = [
                q
                for q in wrong_questions
                if any(
                    int(question) == int(q["question_id"])
                    for question in all_subject_questions_ids
                )
            ]
            un_answered_questions = [
                q
                for q in un_answered_questions
                if any(
                    int(question) == int(q["question_id"])
                    for question in all_subject_questions_ids
                )
            ]
            un_visited_questions = [
                q
                for q in un_visited_questions
                if any(
                    int(question) == int(q["question_id"])
                    for question in all_subject_questions_ids
                )
            ]
            all_question_attempts = [
                q
                for q in all_question_attempts
                if any(
                    int(question) == int(q["question_id"])
                    for question in all_subject_questions_ids
                )
            ]
            # fetching all attempts for reason for error
            all_attempt_ids = [
                question["attempt_id"]
                for question in all_questions
                if question["attempt_id"] != None
            ]
            all_attempt_details = UserAttempt.objects.filter(id__in=all_attempt_ids)
            all_attempt_details_serializer = UserAttemptSerializer(
                all_attempt_details, many=True
            )
            all_attempt_details_serializer = all_attempt_details_serializer.data
            for question in all_questions:
                current_attempt = [
                    q
                    for q in all_attempt_details_serializer
                    if question["attempt_id"] != None
                    and q["id"] == question["attempt_id"]
                ]
                if current_attempt and current_attempt[0]["analysis_data"]:
                    question.update(
                        {
                            "analysis_data_type": current_attempt[0]["analysis_data"][
                                "type"
                            ]
                        }
                    )

            result_total_questions = all_questions
            result_correct_questions = correct_questions
            result_wrong_questions = wrong_questions
            result_un_answered_questions = un_answered_questions
            result_un_visited_questions = un_visited_questions
            if topic:
                result_total_questions = [
                    q
                    for q in result_total_questions
                    if int(q.get("topic", -1)) == int(topic)
                ]
                result_correct_questions = [
                    q for q in result_total_questions if q["is_correct"] == True
                ]
                result_wrong_questions = [
                    q for q in result_total_questions if q["is_wrong"] == True
                ]
                result_un_answered_questions = [
                    q for q in result_total_questions if q["is_attempted"] == True
                ]
                result_un_visited_questions = [
                    q for q in result_total_questions if q["is_visited"] == False
                ]

            if difficulty:
                result_total_questions = [
                    q
                    for q in result_total_questions
                    if q.get("difficulty", None)
                    and (int(q["difficulty"]) == int(difficulty))
                ]
                result_correct_questions = [
                    q for q in result_total_questions if q["is_correct"] == True
                ]
                result_wrong_questions = [
                    q for q in result_total_questions if q["is_wrong"] == True
                ]
                result_un_answered_questions = [
                    q for q in result_total_questions if q["is_attempted"] == True
                ]
                result_un_visited_questions = [
                    q for q in result_total_questions if q["is_visited"] == False
                ]

            if time_taken:
                time_split = time_taken.split("_")
                min = float(time_split[0])
                max = float(time_split[1])
                result_total_questions = [
                    q
                    for q in result_total_questions
                    if int(q["time_taken"]) >= min and int(q["time_taken"]) < max
                ]
                result_correct_questions = [
                    q for q in result_total_questions if q["is_correct"] == True
                ]
                result_wrong_questions = [
                    q for q in result_total_questions if q["is_wrong"] == True
                ]
                result_un_answered_questions = [
                    q for q in result_total_questions if q["is_attempted"] == True
                ]
                result_un_visited_questions = [
                    q for q in result_total_questions if q["is_visited"] == False
                ]

            if reason_for_error:
                result_total_questions = [
                    q
                    for q in result_total_questions
                    if q["analysis_data_type"] == reason_for_error
                ]
                result_correct_questions = [
                    q for q in result_total_questions if q["is_correct"] == True
                ]
                result_wrong_questions = [
                    q for q in result_total_questions if q["is_wrong"] == True
                ]
                result_un_answered_questions = [
                    q for q in result_total_questions if q["is_attempted"] == True
                ]
                result_un_visited_questions = [
                    q for q in result_total_questions if q["is_visited"] == False
                ]

            performanceData = {
                "total_questions": len(result_total_questions),
                "correct_questions": len(result_correct_questions),
                "wrong_questions": len(result_wrong_questions),
                "un_answered_questions": len(result_un_answered_questions),
                "un_visited_questions": len(result_un_visited_questions),
                "total_sessions": len(sessions),
            }

            if output == "topic":

                topic_ids = [question["topic"] for question in all_questions]
                topic_ids = list(set(topic_ids))
                topic_ids = [topic for topic in topic_ids if topic != None]
                performanceData["topics"] = topic_ids
                topic_detail = []
                for topic in topic_ids:
                    topic_all_questions = [
                        q for q in all_questions if q.get("topic", None) == topic
                    ]
                    topic_correct_questions = [
                        q for q in topic_all_questions if q["is_correct"] == True
                    ]
                    topic_wrong_questions = [
                        q for q in topic_all_questions if q["is_wrong"] == True
                    ]
                    topic_un_answered_questions = [
                        q for q in topic_all_questions if q["is_attempted"] == True
                    ]
                    topic_un_visited_questions = [
                        q for q in topic_all_questions if q["is_visited"] == False
                    ]
                    # difficulty
                    if difficulty:
                        topic_all_questions = [
                            q
                            for q in topic_all_questions
                            if int(q.get("difficulty", -1)) == int(difficulty)
                        ]
                        topic_correct_questions = [
                            q
                            for q in topic_correct_questions
                            if int(q.get("difficulty", -1)) == int(difficulty)
                        ]
                        topic_wrong_questions = [
                            q
                            for q in topic_wrong_questions
                            if int(q.get("difficulty", -1)) == int(difficulty)
                        ]
                        topic_un_answered_questions = [
                            q
                            for q in topic_un_answered_questions
                            if int(q.get("difficulty", -1)) == int(difficulty)
                        ]
                        topic_un_visited_questions = [
                            q
                            for q in topic_un_visited_questions
                            if int(q.get("difficulty", -1)) == int(difficulty)
                        ]
                    # time taken
                    if time_taken:
                        time_split = time_taken.split("_")
                        min = float(time_split[0])
                        max = float(time_split[1])
                        topic_all_questions = [
                            q
                            for q in topic_all_questions
                            if int(q["time_taken"]) >= min
                            and int(q["time_taken"]) < max
                        ]
                        topic_correct_questions = [
                            q
                            for q in topic_correct_questions
                            if int(q["time_taken"]) >= min
                            and int(q["time_taken"]) < max
                        ]
                        topic_wrong_questions = [
                            q
                            for q in topic_wrong_questions
                            if int(q["time_taken"]) >= min
                            and int(q["time_taken"]) < max
                        ]
                        topic_un_answered_questions = [
                            q
                            for q in topic_un_answered_questions
                            if int(q["time_taken"]) >= min
                            and int(q["time_taken"]) < max
                        ]
                        topic_un_visited_questions = [
                            q
                            for q in topic_un_visited_questions
                            if int(q["time_taken"]) >= min
                            and int(q["time_taken"]) < max
                        ]
                    # reason for error
                    if reason_for_error:
                        topic_all_questions = [
                            q
                            for q in topic_all_questions
                            if q["analysis_data_type"] == reason_for_error
                        ]
                        topic_correct_questions = [
                            q
                            for q in topic_all_questions
                            if q["analysis_data_type"] == reason_for_error
                        ]
                        topic_wrong_questions = [
                            q
                            for q in topic_all_questions
                            if q["analysis_data_type"] == reason_for_error
                        ]
                        topic_un_answered_questions = [
                            q
                            for q in topic_all_questions
                            if q["analysis_data_type"] == reason_for_error
                        ]
                        topic_un_visited_questions = [
                            q
                            for q in topic_all_questions
                            if q["analysis_data_type"] == reason_for_error
                        ]
                    topic_payload = {
                        "topic": topic,
                        "total_questions": len(topic_all_questions),
                        "correct_questions": len(topic_correct_questions),
                        "wrong_questions": len(topic_wrong_questions),
                        "un_answered_questions": len(topic_un_answered_questions),
                        "un_visited_questions": len(topic_un_visited_questions),
                    }
                    topic_detail.append(topic_payload)
                performanceData["data"] = topic_detail

            if output == "difficulty":
                difficulty_ids = [
                    question.get("difficulty", -1) for question in all_questions
                ]
                difficulty_ids = list(set(difficulty_ids))
                difficulty_detail = []
                for difficulty in difficulty_ids:
                    difficulty_all_questions = [
                        q
                        for q in all_questions
                        if q.get("difficulty", -1) == difficulty
                    ]
                    difficulty_correct_questions = [
                        q for q in difficulty_all_questions if q["is_correct"] == True
                    ]
                    difficulty_wrong_questions = [
                        q for q in difficulty_all_questions if q["is_wrong"] == True
                    ]
                    difficulty_un_answered_questions = [
                        q for q in difficulty_all_questions if q["is_attempted"] == True
                    ]
                    difficulty_un_visited_questions = [
                        q for q in difficulty_all_questions if q["is_visited"] == False
                    ]
                    # topic
                    if topic:
                        difficulty_all_questions = [
                            q
                            for q in difficulty_all_questions
                            if int(q.get("topic", -1)) == int(topic)
                        ]
                        difficulty_correct_questions = [
                            q
                            for q in difficulty_correct_questions
                            if int(q.get("topic", -1)) == int(topic)
                        ]
                        difficulty_wrong_questions = [
                            q
                            for q in difficulty_wrong_questions
                            if int(q.get("topic", -1)) == int(topic)
                        ]
                        difficulty_un_answered_questions = [
                            q
                            for q in difficulty_un_answered_questions
                            if int(q.get("topic", -1)) == int(topic)
                        ]
                        difficulty_un_visited_questions = [
                            q
                            for q in difficulty_un_visited_questions
                            if int(q.get("topic", -1)) == int(topic)
                        ]
                    # time_taken
                    if time_taken:
                        time_split = time_taken.split("_")
                        min = float(time_split[0])
                        max = float(time_split[1])
                        difficulty_all_questions = [
                            q
                            for q in difficulty_all_questions
                            if int(q["time_taken"]) >= min
                            and int(q["time_taken"]) < max
                        ]
                        difficulty_correct_questions = [
                            q
                            for q in difficulty_correct_questions
                            if int(q["time_taken"]) >= min
                            and int(q["time_taken"]) < max
                        ]
                        difficulty_wrong_questions = [
                            q
                            for q in difficulty_wrong_questions
                            if int(q["time_taken"]) >= min
                            and int(q["time_taken"]) < max
                        ]
                        difficulty_un_answered_questions = [
                            q
                            for q in difficulty_un_answered_questions
                            if int(q["time_taken"]) >= min
                            and int(q["time_taken"]) < max
                        ]
                        difficulty_un_visited_questions = [
                            q
                            for q in difficulty_un_visited_questions
                            if int(q["time_taken"]) >= min
                            and int(q["time_taken"]) < max
                        ]
                    # reason for error
                    if reason_for_error:
                        difficulty_all_questions = [
                            q
                            for q in difficulty_all_questions
                            if q["analysis_data_type"] == reason_for_error
                        ]
                        difficulty_correct_questions = [
                            q
                            for q in difficulty_all_questions
                            if q["analysis_data_type"] == reason_for_error
                        ]
                        difficulty_wrong_questions = [
                            q
                            for q in difficulty_all_questions
                            if q["analysis_data_type"] == reason_for_error
                        ]
                        difficulty_un_answered_questions = [
                            q
                            for q in difficulty_all_questions
                            if q["analysis_data_type"] == reason_for_error
                        ]
                        difficulty_un_visited_questions = [
                            q
                            for q in difficulty_all_questions
                            if q["analysis_data_type"] == reason_for_error
                        ]
                    difficulty_payload = {
                        "difficulty": difficulty,
                        "total_questions": len(difficulty_all_questions),
                        "correct_questions": len(difficulty_correct_questions),
                        "wrong_questions": len(difficulty_wrong_questions),
                        "un_answered_questions": len(difficulty_un_answered_questions),
                        "un_visited_questions": len(difficulty_un_visited_questions),
                    }
                    difficulty_detail.append(difficulty_payload)
                performanceData["data"] = difficulty_detail

            if output == "time_taken":
                time_taken_ids = ["0_30", "30_60", "60_10000"]
                time_taken_detail = []
                for time_taken in time_taken_ids:
                    time_split = time_taken.split("_")
                    min = float(time_split[0])
                    max = float(time_split[1])
                    time_taken_all_questions = [
                        q
                        for q in all_questions
                        if int(q["time_taken"]) >= min and int(q["time_taken"]) < max
                    ]
                    time_taken_correct_questions = [
                        q for q in time_taken_all_questions if q["is_correct"] == True
                    ]
                    time_taken_wrong_questions = [
                        q for q in time_taken_all_questions if q["is_wrong"] == True
                    ]
                    time_taken_un_answered_questions = [
                        q for q in time_taken_all_questions if q["is_attempted"] == True
                    ]
                    time_taken_un_visited_questions = [
                        q for q in time_taken_all_questions if q["is_visited"] == False
                    ]
                    # topic
                    if topic:
                        time_taken_all_questions = [
                            q
                            for q in time_taken_all_questions
                            if q.get("topic", None) and int(q["topic"]) == int(topic)
                        ]
                        time_taken_correct_questions = [
                            q
                            for q in time_taken_correct_questions
                            if q.get("topic", None) and int(q["topic"]) == int(topic)
                        ]
                        time_taken_wrong_questions = [
                            q
                            for q in time_taken_wrong_questions
                            if q.get("topic", None) and int(q["topic"]) == int(topic)
                        ]
                        time_taken_un_answered_questions = [
                            q
                            for q in time_taken_un_answered_questions
                            if q.get("topic", None) and int(q["topic"]) == int(topic)
                        ]
                        time_taken_un_visited_questions = [
                            q
                            for q in time_taken_un_visited_questions
                            if q.get("topic", None) and int(q["topic"]) == int(topic)
                        ]
                    # difficulty
                    if difficulty:
                        time_taken_all_questions = [
                            q
                            for q in time_taken_all_questions
                            if int(q.get("difficulty", -1)) == int(difficulty)
                        ]
                        time_taken_correct_questions = [
                            q
                            for q in time_taken_correct_questions
                            if int(q.get("difficulty", -1)) == int(difficulty)
                        ]
                        time_taken_wrong_questions = [
                            q
                            for q in time_taken_wrong_questions
                            if int(q.get("difficulty", -1)) == int(difficulty)
                        ]
                        time_taken_un_answered_questions = [
                            q
                            for q in time_taken_un_answered_questions
                            if int(q.get("difficulty", -1)) == int(difficulty)
                        ]
                        time_taken_un_visited_questions = [
                            q
                            for q in time_taken_un_visited_questions
                            if int(q.get("difficulty", -1)) == int(difficulty)
                        ]
                    # reason for error
                    if reason_for_error:
                        time_taken_all_questions = [
                            q
                            for q in time_taken_all_questions
                            if q["analysis_data_type"] == reason_for_error
                        ]
                        time_taken_correct_questions = [
                            q
                            for q in time_taken_all_questions
                            if q["analysis_data_type"] == reason_for_error
                        ]
                        time_taken_wrong_questions = [
                            q
                            for q in time_taken_all_questions
                            if q["analysis_data_type"] == reason_for_error
                        ]
                        time_taken_un_answered_questions = [
                            q
                            for q in time_taken_all_questions
                            if q["analysis_data_type"] == reason_for_error
                        ]
                        time_taken_un_visited_questions = [
                            q
                            for q in time_taken_all_questions
                            if q["analysis_data_type"] == reason_for_error
                        ]
                    time_taken_payload = {
                        "time_taken": time_taken,
                        "total_questions": len(time_taken_all_questions),
                        "correct_questions": len(time_taken_correct_questions),
                        "wrong_questions": len(time_taken_wrong_questions),
                        "un_answered_questions": len(time_taken_un_answered_questions),
                        "un_visited_questions": len(time_taken_un_visited_questions),
                    }
                    time_taken_detail.append(time_taken_payload)
                performanceData["data"] = time_taken_detail

            if output == "reason_for_error":
                reading_and_writing_error_types = [
                    "clicking_error",
                    "not_read_all_options",
                    "not_follow_correct_steps",
                    "did_not_identify_question_type",
                    "could_not_choose_between_two_options",
                    "did_not_notice_a_trap",
                    "not_read_all_keywords_of_the_question",
                ]
                math_error_types = [
                    "conceptual_error ",
                    "calculation_error ",
                    "reading_error",
                    "graph_based_error",
                ]
                reason_for_error_ids = (
                    reading_and_writing_error_types
                    if subject == "2"
                    else math_error_types
                )
                reason_for_error_detail = []
                for analysis_data_type in reason_for_error_ids:
                    reason_for_error_all_questions = [
                        q
                        for q in all_questions
                        if q["analysis_data_type"] == analysis_data_type
                    ]
                    reason_for_error_correct_questions = [
                        q
                        for q in reason_for_error_all_questions
                        if q["is_correct"] == True
                    ]
                    reason_for_error_wrong_questions = [
                        q
                        for q in reason_for_error_all_questions
                        if q["is_wrong"] == True
                    ]
                    reason_for_error_un_answered_questions = [
                        q
                        for q in reason_for_error_all_questions
                        if q["is_attempted"] == True
                    ]
                    reason_for_error_un_visited_questions = [
                        q
                        for q in reason_for_error_all_questions
                        if q["is_visited"] == False
                    ]
                    # topic
                    if topic:
                        reason_for_error_all_questions = [
                            q
                            for q in reason_for_error_all_questions
                            if q.get("topic", None) and int(q["topic"]) == int(topic)
                        ]
                        reason_for_error_correct_questions = [
                            q
                            for q in reason_for_error_correct_questions
                            if q.get("topic", None) and int(q["topic"]) == int(topic)
                        ]
                        reason_for_error_wrong_questions = [
                            q
                            for q in reason_for_error_wrong_questions
                            if q.get("topic", None) and int(q["topic"]) == int(topic)
                        ]
                        reason_for_error_un_answered_questions = [
                            q
                            for q in reason_for_error_un_answered_questions
                            if q.get("topic", None) and int(q["topic"]) == int(topic)
                        ]
                        reason_for_error_un_visited_questions = [
                            q
                            for q in reason_for_error_un_visited_questions
                            if q.get("topic", None) and int(q["topic"]) == int(topic)
                        ]
                    # difficulty
                    if difficulty:
                        reason_for_error_all_questions = [
                            q
                            for q in reason_for_error_all_questions
                            if int(q.get("difficulty", None)) == int(difficulty)
                        ]
                        reason_for_error_correct_questions = [
                            q
                            for q in reason_for_error_correct_questions
                            if int(q.get("difficulty", None)) == int(difficulty)
                        ]
                        reason_for_error_wrong_questions = [
                            q
                            for q in reason_for_error_wrong_questions
                            if int(q.get("difficulty", None)) == int(difficulty)
                        ]
                        reason_for_error_un_answered_questions = [
                            q
                            for q in reason_for_error_un_answered_questions
                            if int(q.get("difficulty", None)) == int(difficulty)
                        ]
                        reason_for_error_un_visited_questions = [
                            q
                            for q in reason_for_error_un_visited_questions
                            if int(q.get("difficulty", None)) == int(difficulty)
                        ]
                    # time taken
                    if time_taken:
                        time_split = time_taken.split("_")
                        min = int(time_split[0])
                        max = int(time_split[1])
                        reason_for_error_all_questions = [
                            q
                            for q in reason_for_error_all_questions
                            if int(q["time_taken"]) >= min
                            and int(q["time_taken"]) < max
                        ]
                        reason_for_error_correct_questions = [
                            q
                            for q in reason_for_error_correct_questions
                            if int(q["time_taken"]) >= min
                            and int(q["time_taken"]) < max
                        ]
                        reason_for_error_wrong_questions = [
                            q
                            for q in reason_for_error_wrong_questions
                            if int(q["time_taken"]) >= min
                            and int(q["time_taken"]) < max
                        ]
                        reason_for_error_un_answered_questions = [
                            q
                            for q in reason_for_error_un_answered_questions
                            if int(q["time_taken"]) >= min
                            and int(q["time_taken"]) < max
                        ]
                        reason_for_error_un_visited_questions = [
                            q
                            for q in reason_for_error_un_visited_questions
                            if int(q["time_taken"]) >= min
                            and int(q["time_taken"]) < max
                        ]
                    reason_for_error_payload = {
                        "reason_for_error": analysis_data_type.replace(" ", ""),
                        "total_questions": len(reason_for_error_all_questions),
                        "correct_questions": len(reason_for_error_correct_questions),
                        "wrong_questions": len(reason_for_error_wrong_questions),
                        "un_answered_questions": len(
                            reason_for_error_un_answered_questions
                        ),
                        "un_visited_questions": len(
                            reason_for_error_un_visited_questions
                        ),
                    }
                    reason_for_error_detail.append(reason_for_error_payload)
                performanceData["data"] = reason_for_error_detail
            return Response(
                {
                    "message": "success",
                    "data": (
                        performanceData
                        if performanceData["total_questions"] > 0
                        else []
                    ),
                    "now": datetime.now(),
                },
                status=status.HTTP_200_OK,
            )
        else:
            return Response(
                {"message": "error", "message": "parameters missing."},
                status=status.HTTP_400_BAD_REQUEST,
            )


@shared_task
def download_assessment_csv(assessment_id):
    # print('sadfsadf')
    # print('inside the download operation')

    try:
        assessmentObj = Assessment.objects.get(id=assessment_id)
    except Exception as e:
        print("download assessment error", e)

    csv_question_payload = []
    assessment_sections = AssessmentSection.objects.filter(assessment_id=assessment_id)
    counter = 1
    for section in assessment_sections:
        if section.type == "STANDARD":
            section_questions = SectionQuestion.objects.filter(
                section__id=int(section.id)
            ).values_list("question", flat=True)
            csv_question_payload.append(
                [
                    {
                        "section_id": section.id,
                        "question_id": question_id,
                        "question_title": f"S{counter}_{question_id}_({section.type})({section.data['group_by']})",
                    }
                    for question_id in section_questions
                ]
            )
            counter = counter + 1
        else:
            if section.switching_route and list(section.switching_route):
                for section_folder in list(section.switching_route):
                    subject_questions = QuestionNode.objects.filter(
                        node__id=section_folder["folder_id"]
                    ).values_list("question", flat=True)
                    csv_question_payload.append(
                        [
                            {
                                "section_id": section.id,
                                "question_id": question_id,
                                "question_title": f"S{counter}_{question_id}_({section.type})({section.data['group_by']})",
                            }
                            for question_id in subject_questions
                        ]
                    )
                    counter = counter + 1
    csv_question_payload = [
        obj for questions in csv_question_payload for obj in questions
    ]

    user_session = (
        UserAssessmentSession.objects.filter(assessment_id=assessment_id)
        .filter(Q(state="ANALYSED") | Q(state="COMPLETED"))
        .order_by("-created_at")
        .values(
            "user__id",
            "user__first_name",
            "user__last_name",
            "user__email",
            "id",
            "total_correct",
            "section_analysis_data",
            "section_info_data",
            "submitted_at",
        )
    )

    # total and sectional score
    row_zero = [
        " ",
        " ",
        " ",
        " ",
        " ",
    ]
    row_one = ["Id", "Name", "Email", "Session Id", "Total Score", "Test Taken Date"]
    results = []

    header_toggle = True
    for row in user_session:
        if header_toggle:
            if row["section_analysis_data"] and len(row["section_analysis_data"]) > 0:
                for index, section in enumerate(row["section_analysis_data"]):
                    if len(row["section_analysis_data"]) == index + 1:
                        row_zero.append("Question Id's")
                    else:
                        row_zero.append(" ")
                    row_one.append(f"S{index+1} Score")
            header_toggle = False

        payload = [
            row["user__id"],
            f"{row['user__first_name']} {row['user__last_name']}",
            row["user__email"],
            row["id"],
            row["total_correct"],
            row["submitted_at"].date(),
        ]

        all_attempted_questions = []
        for index, _ in enumerate(row["section_analysis_data"]):
            payload.append(
                row["section_analysis_data"][index]["results"]["correct_answers"]
            )
            if (
                row["section_analysis_data"][index]["results"]["attempts"]
                and len(row["section_analysis_data"][index]["results"]["attempts"]) > 0
            ):
                for question in row["section_analysis_data"][index]["results"][
                    "attempts"
                ]:
                    all_attempted_questions.append(question)

        for question in csv_question_payload:
            answersStatus = "-"
            current_question = [
                q
                for q in all_attempted_questions
                if int(q["id"]) == int(question["question_id"])
            ]
            if current_question and len(current_question) > 0:
                answersStatus = "O"
                if current_question[0]["result"]["is_visited"]:
                    if current_question[0]["result"]["is_correct"]:
                        answersStatus = "1"
                    else:
                        answersStatus = "0"
            payload.append(answersStatus)
        results.append(payload)

    for question in csv_question_payload:
        row_zero.append(question["question_id"])
        row_one.append(question["question_title"])

    rows = [row_zero] + [row_one] + list(results)

    # Create a pseudo buffer to write CSV data
    pseudo_buffer = StringIO()
    writer = csv.writer(pseudo_buffer)

    # Write rows to the CSV file
    for row in rows:
        writer.writerow(row)

    filename = f"{assessmentObj.name}_{int(time.time())}.csv"
    csv_data = pseudo_buffer.getvalue()
    django_file = ContentFile(csv_data)

    file_asset = FileAsset(context="sessions")
    file_asset.asset.save(filename, django_file)
    file_asset.save()
    file_data = FileAssetSerializer(file_asset).data
    assessmentObj.assessment_sessions = file_data.get("asset", None)
    assessmentObj.save()

    # print(f'{filename} generated and stored successfully')
    # print('assessment serializer', AssessmentSerializer(assessmentObj).data)


class UserSessionResultCSVEndpoint(BasePaginator, APIView):
    permission_classes = (IsPlatformAdmin, IsTutor, IsManager)
    # Using this decorator to disable csrf.
    @method_decorator(csrf_exempt)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)

    def get(self, request):
        assessment_id = request.GET.get("assessment_id")
        if Assessment.objects.filter(id=assessment_id).exists():

            result = download_assessment_csv.delay(assessment_id)
            # download_assessment_csv(assessment_id)
            return Response(
                {
                    "message": "Generating downloadable link. Please check after some time"
                },
                status=status.HTTP_200_OK,
            )
        return Response(
            {"message": "Assessment not found"}, status=status.HTTP_404_NOT_FOUND
        )


# group
class GroupViewSet(BaseViewset):
    permission_classes = (IsPlatformAdmin, IsManager, IsTutor, IsUserManager)
    serializer_class = GroupSerializer
    model = Group

    def list(self, request):
        groups = Group.objects.all()
        for group in groups:
            group.count = GroupUser.objects.filter(group=group).count()

        payload = [
            {
                "id": group.id,
                "name": group.name,
                "count": group.count,
                "target_date": group.target_date,
                "status": group.status,
                "data": group.data,
            }
            for group in groups
        ]

        return Response(payload)

    def get_group_users(self, request, pk):
        group_users = GroupUser.objects.filter(group=pk)
        group_user = Group.objects.get(id=pk)
        user_ids = [group_user.user_id for group_user in group_users]
        users = User.objects.filter(id__in=user_ids)
        user_map = {
            user.id: {"id": user.id, "name": user.first_name + " " + user.last_name}
            for user in users
        }
        payload = {
            "id": group_user.id,
            "name": group_user.name,
            "target_date": group_user.target_date,
            "status": group_user.status,
            "data": group_user.data,
            "users": [user_map[group_user.user_id] for group_user in group_users],
        }
        return Response(payload)

    def update_group_users(self, request, pk):
        group_user = Group.objects.get(pk=pk)
        name = request.data.get("name")
        status = request.data.get("status")
        target_date = request.data.get("target_date")
        group_user_ids = request.data.get("users", [])
        existing_users = GroupUser.objects.filter(group=pk)

        existing_user_ids = set(existing_users.values_list("user", flat=True))
        new_user_ids = [
            user_id for user_id in group_user_ids if user_id not in existing_user_ids
        ]

        users_to_delete = existing_users.exclude(user__in=group_user_ids)
        users_to_delete.delete()

        new_users = [
            GroupUser(group_id=pk, user_id=user_id) for user_id in new_user_ids
        ]
        GroupUser.objects.bulk_create(new_users)

        if name:
            group_user.name = name
        if status is not None and status != group_user.status:
            group_user.status = status
        if target_date:
            group_user.target_date = target_date
        group_user.save()

        return Response({"message": "success"})

    def delete_group(self, request, pk):
        groups_to_delete = GroupUser.objects.filter(group=pk)
        groups_to_delete.delete()

        group_to_delete = Group.objects.get(pk=pk)
        group_to_delete.delete()

        return Response({"message": f"All groups with id {pk} have been deleted"})


# group_user
class GroupUserViewSet(BaseViewset):
    permission_classes = (IsPlatformAdmin, IsManager, IsTutor, IsUserManager)
    serializer_class = GroupUserSerializer
    model = GroupUser

    def create_group_users(self, request):
        group_id = request.data.get("group")
        user_ids = request.data.get("users", [])
        try:
            group_check = GroupUser.objects.filter(group_id=group_id).first()
            if group_check:
                return Response(
                    {"error": "Group already exists"},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            else:
                group = Group.objects.get(id=group_id)
                new_group_users = []
                for user_id in user_ids:
                    user = User.objects.get(id=user_id)
                    new_group_users.append(GroupUser(group=group, user=user))

                GroupUser.objects.bulk_create(new_group_users)
                return Response({"success": True}, status=status.HTTP_201_CREATED)
        except Group.DoesNotExist:
            return Response(
                {"error": "Group does not exist"}, status=status.HTTP_404_NOT_FOUND
            )
        except User.DoesNotExist:
            return Response(
                {"error": "User does not exist"}, status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            return Response(
                {"error": "Something went wrong"}, status=status.HTTP_400_BAD_REQUEST
            )


# practice_set
class PracticeSetViewSet(BaseViewset):
    permission_classes = (IsPlatformAdmin, IsManager, IsTutor, IsUserManager)
    serializer_class = PracticeSetSerializer
    model = PracticeSet

    def list(self, request):
        practice_sets = PracticeSet.objects.all()
        for practice_set in practice_sets:
            practice_set.count = PracticeSetAssessment.objects.filter(
                practice_set=practice_set
            ).count()

        payload = [
            {
                "id": practice_set.id,
                "name": practice_set.name,
                "count": practice_set.count,
                "status": practice_set.status,
                "data": practice_set.data,
            }
            for practice_set in practice_sets
        ]
        return Response(payload)

    def get_set_assessment(self, request, pk):
        set_list = PracticeSetAssessment.objects.filter(practice_set=pk)
        set = PracticeSet.objects.get(id=pk)
        assessment_ids = [set.assessment_id for set in set_list]
        assessments = Assessment.objects.filter(id__in=assessment_ids)
        assessment_map = {
            assessment.id: {"id": assessment.id, "name": assessment.name}
            for assessment in assessments
        }
        payload = {
            "id": set.id,
            "name": set.name,
            "status": set.status,
            "data": set.data,
            "assessments": [assessment_map[set.assessment_id] for set in set_list],
        }
        return Response(payload)

    def update_set_assessments(self, request, pk):
        practice_set = PracticeSet.objects.get(pk=pk)
        name = request.data.get("name")
        status = request.data.get("status")
        set_assessment_ids = request.data.get("assessments", [])

        if set_assessment_ids:
            existing_assessments = PracticeSetAssessment.objects.filter(practice_set=pk)
            existing_assessment_ids = set(
                existing_assessments.values_list("assessment", flat=True)
            )
            new_assessment_ids = [
                assessment_id
                for assessment_id in set_assessment_ids
                if assessment_id not in existing_assessment_ids
            ]

            assessments_to_delete = existing_assessments.exclude(
                assessment__in=set_assessment_ids
            )
            assessments_to_delete.delete()

            new_assessments = [
                PracticeSetAssessment(practice_set_id=pk, assessment_id=assessment_id)
                for assessment_id in new_assessment_ids
            ]
            PracticeSetAssessment.objects.bulk_create(new_assessments)

        if name:
            practice_set.name = name
        if status is not None and status != practice_set.status:
            practice_set.status = status
        practice_set.save()

        return Response({"message": "success"})

    def delete_set(self, request, pk):
        assessments_to_delete = PracticeSetAssessment.objects.filter(practice_set=pk)
        assessments_to_delete.delete()

        practice_set_to_delete = PracticeSet.objects.get(pk=pk)
        practice_set_to_delete.delete()

        return Response({"message": f"All set with id {pk} have been deleted"})


# practice_set_assessment

class PracticeSetAssessmentViewSet(BaseViewset):
    permission_classes = (IsPlatformAdmin, IsManager, IsTutor, IsUserManager)
    serializer_class = PracticeSetAssessmentSerializer
    model = PracticeSetAssessment

    def create_set_assessments(self, request):
        practice_set_id = request.data.get("practice_set")
        assessment_ids = request.data.get("assessments", [])
        try:
            set_check = PracticeSetAssessment.objects.filter(
                practice_set=practice_set_id
            ).first()
            if set_check:
                return Response(
                    {"error": "Set already exists"}, status=status.HTTP_400_BAD_REQUEST
                )
            else:
                new_set_assessments = []
                for assessment_id in assessment_ids:
                    practice_set = PracticeSet.objects.get(id=practice_set_id)
                    assessment = Assessment.objects.get(id=assessment_id)
                    new_set_assessments.append(
                        PracticeSetAssessment(
                            practice_set=practice_set, assessment=assessment
                        )
                    )
                PracticeSetAssessment.objects.bulk_create(new_set_assessments)
                return Response({"success": True}, status=status.HTTP_201_CREATED)
        except PracticeSet.DoesNotExist:
            return Response(
                {"error": "Practice Set does not exist"},
                status=status.HTTP_404_NOT_FOUND,
            )
        except Assessment.DoesNotExist:
            return Response(
                {"error": "Assessment does not exist"}, status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            return Response(
                {"error": "Something went wrong"}, status=status.HTTP_400_BAD_REQUEST
            )


class AssessmentTagsViewSet(viewsets.ModelViewSet):
    permission_classes = (IsPlatformAdmin, IsManager, IsTutor, IsTypist)
    serializer_class = AssessmentTagsSerializer
    queryset = AssessmentTags.objects.all()

# test allocation
class TestAllocationPracticeSetAssessmentViewSet(viewsets.ModelViewSet):
    permission_classes = (IsPlatformAdmin, IsManager, IsTutor, IsUserManager)
    serializer_class = TestAllocationPracticeSetAssessmentSerializer
    queryset = TestAllocationPracticeSetAssessment.objects.all()


class TestAllocationGroupUserViewSet(viewsets.ModelViewSet):
    permission_classes = (IsPlatformAdmin, IsManager, IsTutor, IsUserManager)
    serializer_class = TestAllocationGroupUserSerializer
    queryset = TestAllocationGroupUser.objects.all()


class TestAllocationLoggerViewSet(viewsets.ModelViewSet):
    permission_classes = (IsPlatformAdmin, IsManager, IsTutor, IsUserManager)
    serializer_class = TestAllocationLoggerSerializer
    queryset = TestAllocationLogger.objects.all()

    def list_log(self, request):
        test_allocation_loggers = TestAllocationLoggerSerializer(
            TestAllocationLogger.objects.all().order_by("-created_at"), many=True
        ).data

        for test_allocation_log in test_allocation_loggers:

            if test_allocation_log.get("kind") == "PRACTICE_SHEET":
                practice_set_list = TestAllocationPracticeSetAssessmentSerializer(
                    TestAllocationPracticeSetAssessment.objects.filter(
                        test_allocation=test_allocation_log.get("id")
                    ),
                    many=True,
                ).data
                if len(practice_set_list) > 0:
                    practice_set = PracticeSetSerializer(
                        PracticeSet.objects.get(
                            id=practice_set_list[0].get("practice_set")
                        )
                    ).data
                    assessment_ids = [
                        set.get("assessment") for set in practice_set_list
                    ]
                    assessments = Assessment.objects.filter(id__in=assessment_ids)
                    assessment_map = [
                        {"id": assessment.id, "name": assessment.name}
                        for assessment in assessments
                    ]

                    test_allocation_log["practice_set"] = {
                        "practice_set": practice_set,
                        "assessment": assessment_map,
                    }

            elif test_allocation_log.get("assessment"):
                test_allocation_log["assessment"] = AssessmentSerializer(
                    Assessment.objects.get(id=test_allocation_log.get("assessment"))
                ).data

            # groups
            group_user_list = TestAllocationGroupUserSerializer(
                TestAllocationGroupUser.objects.filter(
                    test_allocation=test_allocation_log.get("id")
                ),
                many=True,
            ).data

            groups = []
            users = []

            # print('this is group list', group_user_list)

            for group in group_user_list:
                group_id = group.get("group")
                groups.append(group_id)
                users.append(
                    [
                        group.get("user")
                        for group in group_user_list
                        if group_id == group.get("group")
                    ]
                )
                # break

            groups = list(dict.fromkeys(groups))
            users = [list(i) for i in set(frozenset(i) for i in users)]

            main_group_list = []
            for i in range(len(groups)):
                main_group_list.append(
                    {
                        "group": GroupSerializer(Group.objects.get(id=groups[i])).data,
                        "users": [
                            UserMinimumSerializer(User.objects.get(id=user_id)).data
                            for user_id in users[i]
                        ],
                    }
                )
            test_allocation_log["group"] = main_group_list

        return Response(test_allocation_loggers)

    def retrieve_log(self, request, pk):
        try:
            test_allocation_log = TestAllocationLoggerSerializer(
                TestAllocationLogger.objects.get(pk=pk)
            ).data
            if test_allocation_log.get("kind") == "PRACTICE_SHEET":
                practice_set_list = TestAllocationPracticeSetAssessmentSerializer(
                    TestAllocationPracticeSetAssessment.objects.filter(
                        test_allocation=test_allocation_log.get("id")
                    ),
                    many=True,
                ).data
                if len(practice_set_list) > 0:
                    practice_set = PracticeSetSerializer(
                        PracticeSet.objects.get(
                            id=practice_set_list[0].get("practice_set")
                        )
                    ).data
                    assessment_ids = [
                        set.get("assessment") for set in practice_set_list
                    ]
                    assessments = Assessment.objects.filter(id__in=assessment_ids)
                    assessment_map = [
                        {"id": assessment.id, "name": assessment.name}
                        for assessment in assessments
                    ]

                    test_allocation_log["practice_set"] = {
                        "practice_set": practice_set,
                        "assessment": assessment_map,
                    }

            elif test_allocation_log.get("assessment"):
                test_allocation_log["assessment"] = AssessmentSerializer(
                    Assessment.objects.get(id=test_allocation_log.get("assessment"))
                ).data

            # groups
            group_user_list = TestAllocationGroupUserSerializer(
                TestAllocationGroupUser.objects.filter(
                    test_allocation=test_allocation_log.get("id")
                ),
                many=True,
            ).data

            groups = []
            users = []
            for group in group_user_list:
                group_id = group.get("group")
                groups.append(group_id)
                users.append(
                    [
                        group.get("user")
                        for group in group_user_list
                        if group_id == group.get("group")
                    ]
                )

            groups = list(dict.fromkeys(groups))
            users = [list(i) for i in set(frozenset(i) for i in users)]

            main_group_list = []
            for i in range(len(groups)):
                main_group_list.append(
                    {
                        "group": GroupSerializer(Group.objects.get(id=groups[i])).data,
                        "users": [
                            UserMinimumSerializer(User.objects.get(id=user_id)).data
                            for user_id in users[i]
                        ],
                    }
                )
            test_allocation_log["group"] = main_group_list
            return Response(test_allocation_log)
        except TestAllocationLogger.DoesNotExist:
            return Response(
                {"error": "Test allocation does not exist"},
                status=status.HTTP_404_BAD_REQUEST,
            )

    def create_test_logger(self, request):
        kind = request.data.get("kind", None)
        scheduled_at = request.data.get("scheduled_at", None)
        create_assessment_instance = GenerateAssessmentSessionView()
        group_list = request.data.get("groups", [])
        practice_set_list = request.data.get("practice_sets", [])
        set_ids = [p_set.get("practice_set_id") for p_set in practice_set_list]

        allotment = []
        if len(practice_set_list) > 0:
            assessment_lst = [
                x
                for practice_set in practice_set_list
                for x in practice_set["assessments"]
            ]
        else:
            assessment_lst = request.data.get("assessments", [])

        user_list = [x for group in group_list for x in group["users"]]

        for assessment_id in assessment_lst:
            allot = {"assessment": assessment_id, "users": []}
            userSessions = set(
                session["user"]
                for session in UserAssessmentSession.objects.filter(
                    assessment=assessment_id, user__in=user_list
                ).values("user")
            )
            allot["users"] = [user for user in user_list if not user in userSessions]
            allotment.append(allot)

        try:
            scheduled_at = (
                datetime.strptime(scheduled_at, "%Y-%m-%dT%H:%M:%S.%f%z")
                if scheduled_at
                else None
            )
        except Exception as e:
            return Response(
                {"error": "Something went wrong with scheduled_at field"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if kind is None or not kind in ["MICRO", "PRACTICE_SHEET", "MOCK", "SECTIONAL"]:
            return Response(
                {"error": "Mention the valid kind of allocation"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if (
            kind in ["MICRO", "MOCK", "SECTIONAL"]
            and len(request.data.get("assessments", [])) <= 0
        ):
            return Response(
                {"error": "Assessment list is not found"},
                status=status.HTTP_404_NOT_FOUND,
            )

        assessments = Assessment.objects.filter(
            id__in=list(
                dict.fromkeys(
                    request.data.get(
                        "assessments",
                        [
                            assessment
                            for p_set in practice_set_list
                            for assessment in p_set.get("assessments", [])
                        ],
                    )
                )
            )
        )
        test_allocation_log = TestAllocationLogger.objects.create(
            kind=kind, scheduled_at=scheduled_at
        )

        if not kind == "PRACTICE_SHEET":
            test_allocation_log.assessment.set(assessments)

        if kind == "PRACTICE_SHEET":
            if len(practice_set_list) > 0:
                practice_sets = PracticeSet.objects.filter(id__in=set_ids)
                for practice_set in practice_sets:
                    TestAllocationPracticeSetAssessment.objects.bulk_create(
                        [
                            TestAllocationPracticeSetAssessment(
                                test_allocation=test_allocation_log,
                                practice_set=practice_set,
                                assessment=next(
                                    obj for obj in assessments if obj.id == assessment
                                ),
                            )
                            for assessment in next(
                                obj
                                for obj in practice_set_list
                                if obj["practice_set_id"] == practice_set.id
                            ).get("assessments")
                        ]
                    )
            else:
                return Response(
                    {"error": "Practice set list is not found"},
                    status=status.HTTP_404_NOT_FOUND,
                )

        try:
            for group in group_list:
                TestAllocationGroupUser.objects.bulk_create(
                    [
                        TestAllocationGroupUser(
                            test_allocation=test_allocation_log,
                            group=Group.objects.get(id=group["group_id"]),
                            user=User.objects.get(id=user_id),
                        )
                        for user_id in group["users"]
                    ]
                )
        except Group.DoesNotExist:
            return Response(
                {"error": "Group does not exist"}, status=status.HTTP_404_NOT_FOUND
            )
        except User.DoesNotExist:
            return Response(
                {"error": "User does not exist"}, status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            print("this is error on group user", e)
            return Response(
                {"error": "Something went wrong"}, status=status.HTTP_400_BAD_REQUEST
            )

        # allocating tests

        try:
            for allot in allotment:
                for user in allot["users"]:
                    request.data["user"] = user
                    request.data["assessment"] = allot["assessment"]
                    create_assessment_instance.post(request)

        except Exception as e:
            return Response(
                {"error": "Something went wrong"}, status=status.HTTP_400_BAD_REQUEST
            )

        return Response({"success": True}, status=status.HTTP_201_CREATED)

    def update_logger(self, request, pk):
        try:
            existing_log = TestAllocationLogger.objects.get(id=pk)
            existing_log_data = TestAllocationLoggerSerializer(existing_log).data
            kind = request.data.get("kind", None)
            scheduled_at = request.data.get("scheduled_at", False)
            try:
                scheduled_at = (
                    datetime.strptime(scheduled_at, "%Y-%m-%dT%H:%M:%S.%f%z")
                    if scheduled_at
                    else existing_log_data.get("scheduled_at")
                )
            except Exception as e:
                return Response(
                    {"error": "Something went wrong with scheduled_at field"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            assessment = request.data.get("assessment", None)
            practice_set_dict = request.data.get("practice_set", None)
            group_list = request.data.get("groups", None)

            if not kind == None:
                if (
                    not kind == existing_log_data.get("kind")
                    and kind == "PRACTICE_SHEET"
                ):
                    try:
                        practice_set = PracticeSet.objects.get(
                            id=practice_set_dict.get("practice_set_id", None)
                        )
                        if practice_set:
                            TestAllocationLogger.objects.filter(id=pk).update(
                                kind=kind, scheduled_at=None, assessment=None
                            )
                            TestAllocationPracticeSetAssessment.objects.bulk_create(
                                [
                                    TestAllocationPracticeSetAssessment(
                                        test_allocation=TestAllocationLogger.objects.get(
                                            id=pk
                                        ),
                                        practice_set=practice_set,
                                        assessment=Assessment.objects.get(
                                            id=assessment
                                        ),
                                    )
                                    for assessment in practice_set_dict.get(
                                        "assessment", []
                                    )
                                ]
                            )

                    except PracticeSet.DoesNotExist:
                        return Response(
                            {"error": "Practice Set does not exist"},
                            status=status.HTTP_404_NOT_FOUND,
                        )
                    except Assessment.DoesNotExist:
                        return Response(
                            {"error": "Assessment does not exist"},
                            status=status.HTTP_404_NOT_FOUND,
                        )
                    except Exception as e:
                        print("this is error on practice set", e)
                        return Response(
                            {"error": "Something went wrong"},
                            status=status.HTTP_400_BAD_REQUEST,
                        )

                elif (
                    not kind == existing_log_data.get("kind")
                    and existing_log_data.get("kind") == "PRACTICE_SHEET"
                ):
                    try:
                        assessmentObj = Assessment.objects.get(
                            id=request.data.get("assessment")
                        )
                    except Assessment.DoesNotExist:
                        return Response(
                            {"error": "Assessment does not exist"},
                            status=status.HTTP_404_NOT_FOUND,
                        )
                    # deleting existing sets
                    existing_practice_set = (
                        TestAllocationPracticeSetAssessment.objects.filter(
                            test_allocation=pk
                        )
                    )
                    existing_practice_set.delete()
                    TestAllocationLogger.objects.filter(id=pk).update(
                        kind=kind, scheduled_at=scheduled_at, assessment=assessmentObj
                    )
                elif not kind == existing_log_data.get("kind"):
                    TestAllocationLogger.objects.filter(id=pk).update(kind=kind)

            if assessment is not None and not assessment == existing_log_data.get(
                "assessment"
            ):
                TestAllocationLogger.objects.filter(id=pk).update(
                    assessment=Assessment.objects.get(pk=assessment)
                )

            if (
                practice_set_dict is not None
                and TestAllocationLoggerSerializer(
                    TestAllocationLogger.objects.get(id=pk)
                ).data.get("kind")
                == "PRACTICE_SHEET"
            ):
                try:
                    practice_set = PracticeSet.objects.get(
                        id=practice_set_dict.get("practice_set_id")
                    )
                    if practice_set:
                        # deleting older sets
                        existing_practice_set = (
                            TestAllocationPracticeSetAssessment.objects.filter(
                                test_allocation=pk
                            )
                        )
                        existing_practice_set.delete()
                        # creating new sets
                        TestAllocationPracticeSetAssessment.objects.bulk_create(
                            [
                                TestAllocationPracticeSetAssessment(
                                    test_allocation=existing_log,
                                    practice_set=practice_set,
                                    assessment=Assessment.objects.get(id=assessment),
                                )
                                for assessment in practice_set_dict.get("assessment")
                            ]
                        )

                except PracticeSet.DoesNotExist:
                    return Response(
                        {"error": "Practice Set does not exist"},
                        status=status.HTTP_404_NOT_FOUND,
                    )
                except Assessment.DoesNotExist:
                    return Response(
                        {"error": "Assessment does not exist"},
                        status=status.HTTP_404_NOT_FOUND,
                    )
                except Exception as e:
                    print("this is error on practice set", e)
                    return Response(
                        {"error": "Something went wrong"},
                        status=status.HTTP_400_BAD_REQUEST,
                    )

            if group_list is not None:
                try:
                    existing_group_user = TestAllocationGroupUser.objects.filter(
                        test_allocation=pk
                    )
                    existing_group_user.delete()
                    for group_dict in group_list:
                        TestAllocationGroupUser.objects.bulk_create(
                            [
                                TestAllocationGroupUser(
                                    test_allocation=existing_log,
                                    group=Group.objects.get(id=group_dict["group_id"]),
                                    user=User.objects.get(id=user_id),
                                )
                                for user_id in group_dict.get("users")
                            ]
                        )
                except Group.DoesNotExist:
                    return Response(
                        {"error": "Group does not exist"},
                        status=status.HTTP_404_NOT_FOUND,
                    )
                except User.DoesNotExist:
                    return Response(
                        {"error": "User does not exist"},
                        status=status.HTTP_404_NOT_FOUND,
                    )
                except Exception as e:
                    print("this is error on group user", e)
                    return Response(
                        {"error": "Something went wrong"},
                        status=status.HTTP_400_BAD_REQUEST,
                    )

            return Response({"message": "success"})
        except TestAllocationLogger.DoesNotExist:
            return Response(
                {"error": "Test allocation does not exist"},
                status=status.HTTP_404_BAD_REQUEST,
            )


class DownloadAssessmentAnalysis(BaseViewset):
    permission_classes = (IsPlatformAdmin, IsManager, IsTutor, IsUserManager)
    def download_assessment_analysis(self, request):
        session_id = request.GET.get("session_id")
        user_assessment_session = UserAssessmentSession.objects.get(pk=session_id)
        section_question_data = user_assessment_session.section_question_data
        section_analysis_data = user_assessment_session.section_analysis_data
        user_attempts = UserAttempt.objects.filter(session_id=session_id)

        if section_question_data:
            rows = []
            for section_id, question_ids in section_question_data.items():
                section_info = user_assessment_session.section_info_data.get(section_id)
                section_name = section_info.get("name") if section_info else ""
                rows.append([section_name])

                preserved = Case(
                    *[When(pk=pk, then=pos) for pos, pk in enumerate(question_ids)]
                )
                questions = Question.objects.filter(pk__in=question_ids).order_by(
                    preserved
                )

                if questions.exists():
                    questions = questions.values(
                        "id",
                        "approvers_difficulty",
                        "sub_topic",
                        "domain",
                        "topic",
                    )

                    if len(questions) > 0:
                        row_one = [
                            "Q Number",
                            "Domain",
                            "Topic",
                            "Sub Topic",
                            "Difficulty",
                            "Time Taken",
                        ]
                        if user_assessment_session.is_reviewed:
                            row_one.extend(["Reason for Error", "Comments"])

                        row_two = []
                        section_analysis = next(
                            (
                                section["results"]["attempts"]
                                for section in section_analysis_data
                                if str(section["id"]) == section_id
                            ),
                            [],
                        )
                        for index, question in enumerate(questions):
                            attempt = next(
                                (
                                    attempt
                                    for attempt in user_attempts
                                    if attempt.question
                                    and str(attempt.question.id) == str(question["id"])
                                ),
                                None,
                            )

                            if attempt and section_analysis:
                                section_result = section_analysis[index]["result"]
                                if section_result["is_correct"] is False:
                                    domain_id = question["domain"]
                                    domain_name = (
                                        Domain.objects.get(id=domain_id).name
                                        if domain_id
                                        else "None"
                                    )
                                    topic_id = question["topic"]
                                    topic_name = (
                                        Topic.objects.get(id=topic_id).name
                                        if topic_id
                                        else "None"
                                    )
                                    sub_topic_id = question["sub_topic"]
                                    sub_topic_name = (
                                        SubTopic.objects.get(id=sub_topic_id).name
                                        if sub_topic_id
                                        else "None"
                                    )

                                    row_data = [
                                        index + 1,
                                        domain_name,
                                        topic_name,
                                        sub_topic_name,
                                        (
                                            question["approvers_difficulty"]
                                            if question["approvers_difficulty"]
                                            is not None
                                            else "None"
                                        ),
                                        (
                                            section_result["time_taken"]["total_time"]
                                            if index < len(section_analysis)
                                            else "None"
                                        ),
                                    ]

                                    if (
                                        user_assessment_session.is_reviewed
                                        and attempt.analysis_data
                                    ):
                                        type_str = attempt.analysis_data.get(
                                            "type", None
                                        )
                                        if type(type_str) == int:
                                            type_str = ReasonForError.objects.get(
                                                pk=type_str
                                            ).name
                                        formatted_type = type_str.replace(
                                            "_", " "
                                        ).capitalize()
                                        row_data.extend(
                                            [
                                                formatted_type,
                                                attempt.analysis_data.get(
                                                    "message", None
                                                ),
                                            ]
                                        )

                                    row_two.append(row_data)
                        rows.append(row_one)
                        rows.extend(row_two)
                        rows.append([])

                    else:
                        return Response(
                            {"message": "Response is empty"},
                            status=status.HTTP_404_NOT_FOUND,
                        )
                else:
                    return Response(
                        {"message": "Response is empty"},
                        status=status.HTTP_404_NOT_FOUND,
                    )

            pseudo_buffer = WriteToCSV()
            writer = csv.writer(pseudo_buffer)
            response = StreamingHttpResponse(
                (writer.writerow(row) for row in rows), content_type="text/csv"
            )
            filename = f"test-report-analysis_{int(time.time())}"
            response["Content-Disposition"] = f'attachment; filename="{filename}.csv"'
            return response
        else:
            return Response(
                {"message": "section_question_data is empty"},
                status=status.HTTP_404_NOT_FOUND,
            )


# weekly progress
class WeeklyProgressSerializer(serializers.ModelSerializer):
    class Meta:
        model = WeeklyProgress
        fields = "__all__"


class WeeklyProgressViewSet(BaseViewset):
    def create_weekly_progress(self, request, pk):
        start_date = request.data.get("start_date")
        end_date = request.data.get("end_date")
        progress = request.data.get("progress", [])
        core_class = request.data.get("core_class", 0)
        doubts_class = request.data.get("doubts_class", 0)
        strategy_class = request.data.get("strategy_class", 0)
        sectional_class = request.data.get("sectional_class", 0)
        reading_articles = request.data.get("reading_articles", 0)
        mock_tests = request.data.get("mock_tests", 0)
        practice_sheet = request.data.get("practice_sheet", 0)
        analyse = request.data.get("analyse", 0)

        try:
            user = User.objects.get(pk=pk)
        except User.DoesNotExist:
            return Response(
                {"error": "User not found."}, status=status.HTTP_404_NOT_FOUND
            )

        if (
            WeeklyProgress.objects.filter(user=user)
            .filter(Q(start_date=start_date) | Q(end_date=end_date))
            .exists()
        ):
            return Response(
                {"error": "Weekly progress for this date range already exists."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        weekly_progress = WeeklyProgress.objects.create(
            user=user,
            start_date=start_date,
            end_date=end_date,
            progress=progress,
            core_class=core_class,
            doubts_class=doubts_class,
            strategy_class=strategy_class,
            sectional_class=sectional_class,
            reading_articles=reading_articles,
            mock_tests=mock_tests,
            practice_sheet=practice_sheet,
            analyse=analyse,
        )

        serializer = WeeklyProgressSerializer(weekly_progress)
        return Response(
            {
                "success": "Weekly progress created successfully.",
                "data": serializer.data,
            },
            status=status.HTTP_201_CREATED,
        )

    def list(self, request, pk):
        try:
            all_weekly_progress = WeeklyProgress.objects.filter(user_id=pk).order_by(
                "-start_date"
            )
            serializer = WeeklyProgressSerializer(all_weekly_progress, many=True)
            return Response(
                {
                    "success": "Weekly progress updated successfully.",
                    "weekly_progress": serializer.data,
                },
                status=status.HTTP_200_OK,
            )
        except WeeklyProgress.DoesNotExist:
            return Response(
                {"error": "Weekly progress not found."},
                status=status.HTTP_404_NOT_FOUND,
            )

    def update_weekly_progress(self, request, pk=None):
        try:
            weekly_progress = WeeklyProgress.objects.get(id=pk)
        except WeeklyProgress.DoesNotExist:
            return Response(
                {"error": "Weekly progress not found."},
                status=status.HTTP_404_NOT_FOUND,
            )

        progress = request.data.get("progress", None)

        if progress is not None:
            duration_by_name = {}
            for item in progress:
                name = item["name"]
                duration = item["duration"]
                if name in duration_by_name:
                    duration_by_name[name] += int(duration)
                else:
                    duration_by_name[name] = int(duration)

            weekly_progress.progress = progress

        fields_to_update = [
            "core_class",
            "doubts_class",
            "strategy_class",
            "sectional_class",
            "reading_articles",
            "mock_tests",
            "practice_sheet",
            "analyse",
        ]
        for field in fields_to_update:
            value = request.data.get(field)
            if value is not None:
                setattr(weekly_progress, field, value)

        weekly_progress.save()
        serializer = WeeklyProgressSerializer(weekly_progress)
        return Response(
            {
                "success": "Weekly progress updated successfully.",
                "weekly_progress": serializer.data,
            },
            status=status.HTTP_200_OK,
        )


class TestIRTQuestionViewSet(BaseViewset):
    permission_classes = (IsPlatformAdmin, IsTypist)
    def get(self, request, pk):
        try:
            if request.user.role not in ["admin", "typist"]:
                return Response(
                    {"Unauthorize access"}, status=status.HTTP_403_FORBIDDEN
                )
            assessment = Assessment.objects.get(pk=pk)
            assessment_sections = AssessmentSection.objects.filter(assessment_id=pk)
            assessment_questions = []

            for section in assessment_sections:
                section_id = section.id

                if section.type == "STANDARD":
                    section_questions = SectionQuestion.objects.filter(
                        section_id=section_id
                    )
                    for idx, question in enumerate(section_questions):
                        question_id = question.question_id
                        q = Question.objects.filter(pk=question_id)
                        if q:
                            assessment_questions.append(
                                {
                                    "section": section_id,
                                    "type": section.type,
                                    "name": section.name,
                                    "question": q[0].id,
                                    "irt_a": q[0].irt_a,
                                    "irt_b": q[0].irt_b,
                                    "irt_c": q[0].irt_c,
                                    "no": (
                                        f"MA {idx+1}"
                                        if q[0].subject.id == 1
                                        else f"A {idx+1}"
                                    ),
                                }
                            )
                else:
                    eng_alpha = ["B", "C"]
                    math_alpha = ["MB", "MC"]
                    for idx, switch in enumerate(section.switching_route):
                        folder_id = switch["folder_id"]
                        questions = QuestionNode.objects.filter(
                            node_id=folder_id
                        ).values_list("question_id", flat=True)
                        questions = Question.objects.filter(pk__in=questions)
                        for qidx, question in enumerate(questions):
                            if question:
                                assessment_questions.append(
                                    {
                                        "section": section_id,
                                        "type": section.type,
                                        "name": section.name,
                                        "question": question.id,
                                        "irt_a": question.irt_a,
                                        "irt_b": question.irt_b,
                                        "irt_c": question.irt_c,
                                        "no": (
                                            math_alpha[idx] + " " + str(qidx + 1)
                                            if q[0].subject.id == 1
                                            else eng_alpha[idx] + " " + str(qidx + 1)
                                        ),
                                    }
                                )

            return Response(
                {
                    "assessment": AssessmentSerializer(assessment).data,
                    "questions": assessment_questions,
                },
                status=status.HTTP_200_OK,
            )

        except Exception as e:
            return Response({"message": e}, status=status.HTTP_400_BAD_REQUEST)

    def post(self, request, pk):
        try:
            if request.user.role not in ["admin", "typist"]:
                return Response(
                    {"Unauthorize access"}, status=status.HTTP_403_FORBIDDEN
                )
            assessment = Assessment.objects.get(pk=pk)
            english = request.data.get("english", None)
            math = request.data.get("math", None)
            question_data = request.data.get("tableData", [])

            if english:
                assessment.english_sigma = english.get("sigma", 0.0)
                assessment.english_xbar = english.get("xBar", 0.0)

            if math:
                assessment.math_sigma = math.get("sigma", 0.0)
                assessment.math_xbar = math.get("xBar", 0.0)

            assessment.save()

            for question in question_data:
                Question.objects.filter(id=question["question"]).update(
                    irt_a=question["irt_a"],
                    irt_b=question["irt_b"],
                    irt_c=question["irt_c"],
                )

            return Response(
                {"message": "Assessment Table Updated"}, status=status.HTTP_200_OK
            )

        except Exception as e:
            return Response({"message": e}, status=status.HTTP_400_BAD_REQUEST)
