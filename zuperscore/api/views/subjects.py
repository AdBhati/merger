from django.forms import ValidationError
from django.http import Http404
from rest_framework.response import Response
from rest_framework import status
from rest_framework.views import APIView
from rest_framework import serializers
from rest_framework import filters as rest_filters
from rest_framework.permissions import AllowAny
from django.db.models import Q
from django.db.models import F
from django.db import models
from collections import defaultdict
from django.core.paginator import Paginator
from django.db.models import Prefetch
from rest_framework.pagination import PageNumberPagination
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.forms.models import model_to_dict
from rest_framework import pagination
from django.shortcuts import get_object_or_404
from django_filters import rest_framework as filters
from rest_framework import filters as rest_filters
from operator import itemgetter
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models.functions import Length

# import date module by suresh
from datetime import date, datetime
from zuperscore.db.models.base import EnglishCategory, MathCategory, User
from zuperscore.db.models.subjects import SubjectNode
from zuperscore.db.models.library import (
    Exam,
    Subject,
    MegaDomain,
    Module,
    Domain,
    Topic,
    SubTopic,
    Molecule,
    MoleculeTopicSubtopic,
    SessionPlan,
    Assignment,
    AssignmentQuestion,
    QuestionOption,
    ReasonForError,
    MotherSessionMolecule,
)
from zuperscore.db.models.conduct import (
    # StudentCategory,
    StudentSessionPlan,
    StudentModule,
    StudentDomain,
    StudentTopic,
    StudentSubTopic,
    StudentAssignment,
    StudentAssignmentQuestion,
    StudentQuestionOption,
    Appointments,
    Attendee,
)

from zuperscore.db.models.base import (
    StudentCategory,
)


from .base import BaseSerializer, BaseViewset
from zuperscore.utils.paginator import BasePaginator
from zuperscore.api.permissions import *
from rest_framework import viewsets
import json


class SubjectNodeSerializer(BaseSerializer):
    class Meta:
        model = SubjectNode
        fields = "__all__"


class TreeMixin:
    def get_node(self, node_id):
        try:
            return SubjectNode.objects.get(pk=node_id)
        except:
            raise Http404


class CreateSubjectTree(TreeMixin, APIView):
    permission_classes = ((IsPlatformAdmin | IsTypist | IsManager),)

    def post(self, request):
        title = request.data.get("title")
        kind = request.data.get("kind", "ROOT")

        root = SubjectNode.add_root(title=title, kind=kind)
        serializer = SubjectNodeSerializer(root)
        return Response({"tree": serializer.data})


class SubjectTreeByNodeView(TreeMixin, APIView):
    permission_classes = ((IsPlatformAdmin | IsTypist | IsManager),)

    def get(self, request, node_id):
        # print(request.user.role)
        root = self.get_node(node_id)
        tree = SubjectNode.dump_bulk(parent=root)
        return Response({"tree": tree}, status=status.HTTP_200_OK)


class SubjectNodeViewset(viewsets.ModelViewSet):
    permission_classes = ((IsPlatformAdmin | IsTypist | IsManager),)
    serializer_class = SubjectNodeSerializer
    queryset = SubjectNode.objects.all()


class AllSubjectRoots(APIView):
    permission_classes = (
        ~IsParent,
        ~IsCounselor,
        ~IsGuest,
    )

    def get(self, request):
        state = request.GET.get("state")
        nodes = SubjectNode.get_root_nodes()

        if state:
            nodes = nodes.filter(state=state)

        serializer = SubjectNodeSerializer(nodes, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class SubjectNodeActions(TreeMixin, APIView):
    permission_classes = ((IsPlatformAdmin | IsTypist | IsManager),)

    def post(self, request):

        operation = request.data.get("operation", False)

        title = request.data.get("title", False)
        description = request.data.get("description", "")
        data = request.data.get("data", "")
        is_active = request.data.get("is_required", True)
        kind = request.data.get("kind")
        props = request.data.get("props")

        node_id = request.data.get("node_id", False)

        if operation == "append":
            # block = get_block(block_id) # can be extra
            position = request.data.get("position", False)
            node = self.get_node(node_id)

            new_node = SubjectNode(
                title=title,
                description=description,
                is_active=is_active,
                data=data,
                kind=kind,
                props=props,
            )

            try:
                node.add_sibling(position, instance=new_node)
                serializer = SubjectNodeSerializer(new_node)

                return Response({"message": "success", "new_node": serializer.data})
            except Exception as e:
                print(e)
                return Response({"message": "failed"})

        if operation == "move":
            position = request.data.get("position", False)
            target_id = request.data.get("target_id", False)

            node = self.get_node(node_id)
            target_node = self.get_node(target_id)
            try:
                node.move(target_node, pos=position)
                serializer = SubjectNodeSerializer(node)
                return Response({"message": "success", "node": serializer.data})
            except Exception as e:
                print(e)
                return Response({"message": "failed"})

        if operation == "delete":
            node = self.get_node(node_id)

            try:
                node.delete()
                return Response({"message": "success"})
            except:
                return Response({"message": "failed"})

        if operation == "add":
            node = self.get_node(node_id)
            new_node = SubjectNode(
                title=title,
                description=description,
                is_active=is_active,
                data=data,
                kind=kind,
            )
            try:
                node.add_child(instance=new_node)
                serializer = SubjectNodeSerializer(new_node)
                return Response({"message": "success", "new_node": serializer.data})
            except Exception as e:
                print(e)
                return Response({"message": "failed"})

        return Response({"message", "operation invalid"}, status=400)


# exam
class ExamSerializer(BaseSerializer):
    class Meta:
        model = Exam
        fields = "__all__"


class ExamViewSet(BaseViewset):
    permission_classes = (~IsGuest,)
    serializer_class = ExamSerializer
    model = Exam

    def list(self, request):
        serializer = ExamSerializer(Exam.objects.all(), many=True)
        return Response(serializer.data)


# subject
class SubjectSerializer(BaseSerializer):
    class Meta:
        model = Subject
        fields = "__all__"


class SubjectViewSet(BaseViewset):
    permission_classes = (
        (
            read_only(IsGuest)
            | read_only(IsStudent)
            | read_only(IsParent)
            | read_only(IsCounselor)
            | read_only(IsUserManager)
            | IsPlatformAdmin
            | IsTutor
            | ~IsTypist
            | IsManager
        ),
    )
    serializer_class = SubjectSerializer
    model = Subject

    def list(self, request):
        exam = request.GET.get("exam")
        if exam:
            serializer = SubjectSerializer(Subject.objects.filter(exam=exam), many=True)
        else:
            serializer = SubjectSerializer(Subject.objects.all(), many=True)
        return Response(serializer.data)

    def get_by_id(self, request, pk):
        try:
            existing_subject = Subject.objects.get(pk=pk)
            serializer = SubjectSerializer(existing_subject)

            return Response(
                {
                    "success": True,
                    "status": "success",
                    "message": "",
                    "results": [serializer.data],
                }
            )
        except Subject.DoesNotExist:
            return Response(
                {"success": False, "error": "Subject not found"},
                status=status.HTTP_404_NOT_FOUND,
            )
        except Exception as e:
            print("Exception ====> ", e)
            return Response(
                {"success": False, "error": "Something went wrong"},
                status=status.HTTP_400_BAD_REQUEST,
            )


# mega domain
class MegaDomainSerializer(BaseSerializer):

    class Meta:
        model = MegaDomain
        fields = "__all__"


class MegaDomainGetSerializer(BaseSerializer):

    subject = SubjectSerializer(read_only=True)

    class Meta:
        model = MegaDomain
        fields = ["id", "name", "description", "sequence", "subject"]
        # fields = ["id", "name", "description", "sequence"]


class MegaDomainViewSet(BaseViewset):
    permission_classes = (
        (
            read_only(IsStudent)
            | read_only(IsParent)
            | read_only(IsCounselor)
            | read_only(IsUserManager)
            | IsPlatformAdmin
            | IsTutor
            | IsManager
        ),
    )
    serializer_class = MegaDomainSerializer
    model = MegaDomain

    # def list(self, request):

    #     subject = request.GET.get("subject")

    #     if subject:
    #         serializer = MegaDomainGetSerializer(
    #             MegaDomain.objects.filter(subject=subject).order_by("-created_at"),
    #             many=True,
    #         )
    #     else:
    #         serializer = MegaDomainGetSerializer(
    #             MegaDomain.objects.all().order_by("-created_at"), many=True
    #         )
    #     return Response(
    #         {
    #             "success": True,
    #             "status": "success",
    #             "message": "",
    #             "results": serializer.data,
    #         }
    #     )

    def list(self, request):

        name_filter = request.GET.get("name", None)
        subject_filter = request.GET.get("subject", None)
        megadomain_queryset = MegaDomain.objects.filter(is_active=True)

        if subject_filter:
            megadomain_queryset = megadomain_queryset.filter(
                Q(subject__name__icontains=subject_filter) | Q(subject=subject_filter)
            )

        if name_filter:
            megadomain_queryset = megadomain_queryset.filter(
                name__icontains=name_filter
            )

        megadomain_queryset = megadomain_queryset.order_by("-created_at")
        serializer = MegaDomainGetSerializer(megadomain_queryset, many=True)

        # Return the response
        return Response(
            {
                "success": True,
                "status": "success",
                "message": "",
                "results": serializer.data,
            }
        )

    def get_by_id(self, request, pk):
        try:
            existing_megadomain = MegaDomain.objects.get(pk=pk, is_active=True)
            serializer = MegaDomainGetSerializer(existing_megadomain)

            return Response(
                {
                    "success": True,
                    "status": "success",
                    "message": "",
                    "results": [serializer.data],
                }
            )
        except MegaDomain.DoesNotExist:
            return Response(
                {"success": False, "error": "MegaDomain not found"},
                status=status.HTTP_404_NOT_FOUND,
            )
        except Exception as e:
            print("Exception ====> ", e)
            return Response(
                {"success": False, "error": "Something went wrong"},
                status=status.HTTP_400_BAD_REQUEST,
            )

    def create(self, request):
        try:
            name = request.data.get("name")
            existing_megadomain = MegaDomain.objects.filter(name__iexact=name)
            if existing_megadomain.exists():
                return Response(
                    {"success": False, "error": "Megadomain already exists"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            serializer = MegaDomainSerializer(data=request.data)
            if serializer.is_valid(raise_exception=True):
                serializer.save()

            return Response(
                {
                    "success": True,
                    "status": "success",
                    "message": "Megadomain saved successfully.",
                    "results": serializer.data,
                }
            )
        except Exception as e:
            print("Exception ====> ", e)
            return Response(
                {"success": False, "error": "Something went wrong"},
                status=status.HTTP_400_BAD_REQUEST,
            )

    def update(self, request, pk):
        try:
            existing_megadomain = MegaDomain.objects.get(pk=pk)
            name = request.data.get("name")

            if existing_megadomain.name != name:
                if MegaDomain.objects.filter(name=name).exists():
                    return Response(
                        {"success": False, "error": "MegaDomain already exists"},
                        status=status.HTTP_400_BAD_REQUEST,
                    )
                existing_megadomain.name = name

            description = request.data.get("description")
            if existing_megadomain.description != description:
                existing_megadomain.description = description

            sequence = request.data.get("sequence")
            if existing_megadomain.sequence != sequence:
                existing_megadomain.sequence = sequence

            subject = request.data.get("subject")
            if subject and subject != existing_megadomain.subject:
                change_subject = Subject.objects.get(pk=subject)
                existing_megadomain.subject = change_subject

            existing_megadomain.save()
            serializer = MegaDomainGetSerializer(existing_megadomain)

            return Response(
                {
                    "success": True,
                    "status": "success",
                    "message": "MegaDomain updated successfully",
                    "results": [serializer.data],
                }
            )
        except Exception as e:
            print("Exception ====> ", e)
            return Response(
                {"success": False, "error": "Something went wrong"},
                status=status.HTTP_400_BAD_REQUEST,
            )


# Module
class ModuleSerializer(BaseSerializer):
    class Meta:
        model = Module
        fields = "__all__"


class ModuleGetSerializer(BaseSerializer):
    mega_domain = MegaDomainGetSerializer(read_only=True)

    class Meta:
        model = Module
        fields = ["id", "name", "description", "sequence", "mega_domain"]


class ModuleTreeSerializer(BaseSerializer):
    mega_domain = MegaDomainGetSerializer(read_only=True)

    class Meta:
        model = Module
        fields = ["id", "name", "description", "sequence", "mega_domain"]


class ModuleViewSet(BaseViewset):
    permission_classes = (IsPlatformAdmin,)
    serializer_class = ModuleSerializer
    model = Module
    # fields = ["id", "name", "description", "sequence"]

    def list(self, request):
        mega_domain = request.GET.get("meag_domain")
        print("mega_domain is:", mega_domain)
        if mega_domain:
            serializer = ModuleGetSerializer(
                Module.objects.filter(mega_domain=mega_domain).order_by("-created_at"),
                many=True,
            )
        else:
            serializer = ModuleGetSerializer(
                Module.objects.all().order_by("-created_at"), many=True
            )
        return Response(
            {
                "success": True,
                "status": "success",
                "message": "",
                "results": serializer.data,
            }
        )

    def get_by_id(self, request, pk):
        try:
            existing_module = Module.objects.get(pk=pk)
            serializer = ModuleGetSerializer(existing_module)

            return Response(
                {
                    "success": True,
                    "status": "success",
                    "message": "",
                    "results": [serializer.data],
                }
            )
        except Module.DoesNotExist:
            return Response(
                {"success": False, "error": "Module not found"},
                status=status.HTTP_404_NOT_FOUND,
            )
        except Exception as e:
            print("Exception ====> ", e)
            return Response(
                {"success": False, "error": "Something went wrong"},
                status=status.HTTP_400_BAD_REQUEST,
            )

    def create(self, request):
        try:
            name = request.data.get("name")
            existing_module = Module.objects.filter(name=name)
            if existing_module:
                return Response(
                    {"success": False, "error": "Module already exists"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            serializer = ModuleSerializer(data=request.data)
            if serializer.is_valid(raise_exception=True):
                serializer.save()

            return Response(
                {
                    "success": True,
                    "status": "success",
                    "message": "Module saved successfully.",
                    "results": serializer.data,
                }
            )
        except Exception as e:
            print("Exception ====> ", e)
            return Response(
                {"success": False, "error": "Something went wrong"},
                status=status.HTTP_400_BAD_REQUEST,
            )

    def update(self, request, pk):
        try:
            existing_module = Module.objects.get(pk=pk)
            name = request.data.get("name")

            if existing_module.name != name:
                if Module.objects.filter(name=name).exists():
                    return Response(
                        {"success": False, "error": "Module already exists"},
                        status=status.HTTP_400_BAD_REQUEST,
                    )
                existing_module.name = name

            description = request.data.get("description")
            if existing_module.description != description:
                existing_module.description = description

            sequence = request.data.get("sequence")
            if existing_module.sequence != sequence:
                existing_module.sequence = sequence

            mega_domain = request.data.get("mega_domain")
            if mega_domain and mega_domain != existing_module.mega_domain:
                change_megadomain = MegaDomain.objects.get(pk=mega_domain)
                existing_module.mega_domain = change_megadomain

            existing_module.save()
            serializer = DomainGetSerializer(existing_module)

            return Response(
                {
                    "success": True,
                    "status": "success",
                    "message": "Module updated successfully",
                    "results": [serializer.data],
                }
            )
        except Exception as e:
            print("Exception ====> ", e)
            return Response(
                {"success": False, "error": "Something went wrong"},
                status=status.HTTP_400_BAD_REQUEST,
            )


# domain
class DomainSerializer(BaseSerializer):

    class Meta:
        model = Domain
        fields = "__all__"


class DomainGetSerializer(BaseSerializer):
    # module = ModuleGetSerializer(read_only=True)
    mega_domain = MegaDomainSerializer()
    subject = SubjectSerializer()

    class Meta:
        model = Domain
        fields = [
            "id",
            "name",
            "description",
            "is_active",
            "sequence",
            "mega_domain",
            "subject",
        ]


class DomainViewSet(BaseViewset):

    permission_classes = (
        (
            read_only(IsStudent)
            | read_only(IsParent)
            | read_only(IsCounselor)
            | read_only(IsUserManager)
            | IsPlatformAdmin
            | IsTutor
            | IsManager
        ),
    )

    serializer_class = DomainSerializer
    model = Domain

    # def list(self, request):
    #     module = request.GET.get("module")
    #     if module:
    #         serializer = DomainGetSerializer(
    #             Domain.objects.filter(module=module, is_active=True).order_by(
    #                 "-created_at"
    #             ),
    #             many=True,
    #         )
    #     else:
    #         serializer = DomainGetSerializer(
    #             Domain.objects.all().order_by("-created_at"), many=True
    #         )
    #     return Response(
    #         {
    #             "success": True,
    #             "status": "success",
    #             "message": "",
    #             "results": serializer.data,
    #         }
    #     )

    def list(self, request):

        name_filter = request.GET.get("name")
        subject_filter = request.GET.get("subject")
        module = request.GET.get("module")

        domain_queryset = Domain.objects.filter(is_active=True)

        if name_filter:
            domain_queryset = domain_queryset.filter(name__icontains=name_filter)

        if subject_filter:
            domain_queryset = domain_queryset.filter(
                subject__name__icontains=subject_filter
            )

        if module:
            domain_queryset = domain_queryset.filter(module=module)

        domain_queryset = domain_queryset.order_by("-created_at")

        serializer = DomainGetSerializer(domain_queryset, many=True)

        return Response(
            {
                "success": True,
                "status": "success",
                "message": "",
                "results": serializer.data,
            }
        )

    def get_by_id(self, request, pk):
        try:
            existing_domain = Domain.objects.get(pk=pk, is_active=True)
            serializer = DomainGetSerializer(existing_domain)

            return Response(
                {
                    "success": True,
                    "status": "success",
                    "message": "",
                    "results": [serializer.data],
                }
            )
        except Domain.DoesNotExist:
            return Response(
                {"success": False, "error": "Domain not found"},
                status=status.HTTP_404_NOT_FOUND,
            )
        except Exception as e:
            print("Exception ====> ", e)
            return Response(
                {"success": False, "error": "Something went wrong"},
                status=status.HTTP_400_BAD_REQUEST,
            )

    def create(self, request):
        name = request.data.get("name")
        if Domain.objects.filter(name__iexact=name).exists():
            return Response(
                {"success": False, "error": "Domain already exists"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        serializer = DomainSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            serializer.save()

        return Response(
            {
                "success": True,
                "status": "success",
                "message": "Domain saved successfully.",
                "results": [serializer.data],
            }
        )

    def update(self, request, pk):
        try:
            existing_domain = Domain.objects.get(pk=pk)
            name = request.data.get("name")

            if existing_domain.name != name:
                if Domain.objects.filter(name=name).exists():
                    return Response(
                        {"success": False, "error": "Domain already exists"},
                        status=status.HTTP_400_BAD_REQUEST,
                    )
                existing_domain.name = name

            is_active = request.data.get("is_active")
            if is_active is not None and is_active != existing_domain.is_active:
                existing_domain.is_active = is_active

            description = request.data.get("description")
            if existing_domain.description != description:
                existing_domain.description = description

            sequence = request.data.get("sequence")
            if existing_domain.sequence != sequence:
                existing_domain.sequence = sequence

            subject = request.data.get("subject")
            if subject and subject != existing_domain.subject:
                change_subject = Subject.objects.get(pk=subject)
                existing_domain.subject = change_subject

            mega_domain = request.data.get("mega_domain")
            if mega_domain and mega_domain != existing_domain.mega_domain:
                change_mega_domain = MegaDomain.objects.get(pk=mega_domain)
                existing_domain.mega_domain = change_mega_domain

            existing_domain.save()
            serializer = DomainSerializer(existing_domain)

            return Response(
                {
                    "success": True,
                    "status": "success",
                    "message": "Domain updated successfully",
                    "results": [serializer.data],
                }
            )
        except Exception as e:
            print("Exception ====> ", e)
            return Response(
                {"success": False, "error": "Something went wrong"},
                status=status.HTTP_400_BAD_REQUEST,
            )


# topic
class TopicSerializer(BaseSerializer):
    class Meta:
        model = Topic
        fields = "__all__"


# class DomainGetSerializer(BaseSerializer):
#     topic = TopicSerializer(read_only=True)

#     class Meta:
#         model = Domain


class TopicGetSerializer(BaseSerializer):
    domain = DomainGetSerializer(read_only=True)

    class Meta:
        model = Topic
        fields = ["id", "name", "description", "sequence", "domain"]


class TopicViewSet(BaseViewset):
    permission_classes = (
        (
             read_only(IsStudent)
            | read_only(IsParent)
            | read_only(IsCounselor)
            | read_only(IsUserManager)
            | IsPlatformAdmin
            | IsTutor
            | IsManager
        ),
    )
    serializer_class = TopicSerializer
    model = Topic

    def list(self, request):
        try:
            topics = Topic.objects.all().order_by("id")
            domain = request.GET.get("domain")
            name = request.GET.get("name")
            total_records = None

            if domain:
                serializer = TopicGetSerializer(
                    Topic.objects.filter(domain=domain).order_by("-created_at"),
                    many=True,
                )

            elif name:
                topics = topics.filter(Q(name__icontains=name))
                serializer = TopicGetSerializer(topics, many=True)
                total_records = topics.count()

            else:
                pass

            page = request.GET.get("page")
            page_size = request.GET.get("page_size", 10)
            paginator = PageNumberPagination()
            paginator.page_size = page_size

            if page:
                print("page", page)
                paginated_topics = paginator.paginate_queryset(topics, request)
                serializer = TopicGetSerializer(paginated_topics, many=True)
                total_records = topics.count()
            else:
                # paginated_subtopics = paginator.paginate_queryset(topics, request)
                serializer = TopicGetSerializer(topics, many=True)
                total_records = topics.count()

            return Response(
                {
                    "success": True,
                    "status": "success",
                    "message": "",
                    "Total_records": total_records,
                    "results": serializer.data,
                }
            )
        except Exception as e:
            print("Exception ====> ", e)
            return Response(
                {"success": False, "error": "Something went wrong"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # else:
        #     serializer = TopicGetSerializer(
        #         Topic.objects.all().order_by("-created_at"), many=True
        #     )

        # paginator = PageNumberPagination()
        # paginator.page_size = request.GET.get('page_size', 10)
        # paginated_assignments = paginator.paginate_queryset(topic, self.request)

        # serializer = TopicGetSerializer(paginated_assignments, many=True)

        # total_records = topic.count()
        # return Response(
        #     {
        #         "success": True,
        #         "status": "success",
        #         "message": "",
        #         "Total_records":total_records,
        #         "results": serializer.data,
        #     }
        # )

    def get_by_id(self, request, pk):
        try:
            existing_topic = Topic.objects.get(pk=pk)
            serializer = TopicGetSerializer(existing_topic)

            return Response(
                {
                    "success": True,
                    "status": "success",
                    "message": "",
                    "results": [serializer.data],
                }
            )
        except Domain.DoesNotExist:
            return Response(
                {"success": False, "error": "Topic not found"},
                status=status.HTTP_404_NOT_FOUND,
            )
        except Exception as e:
            print("Exception ====> ", e)
            return Response(
                {"success": False, "error": "Something went wrong"},
                status=status.HTTP_400_BAD_REQUEST,
            )

    def create(self, request):
        name = request.data.get("name")
        if Topic.objects.filter(name__iexact=name).exists():
            return Response(
                {"success": False, "error": "Topic already exists"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        serializer = TopicSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            serializer.save()

        return Response(
            {
                "success": True,
                "status": "success",
                "message": "Topic saved successfully.",
                "results": [serializer.data],
            }
        )

    def update(self, request, pk):
        try:
            existing_topic = Topic.objects.get(pk=pk)
            name = request.data.get("name")

            if existing_topic.name != name:
                if Topic.objects.filter(name=name).exists():
                    return Response(
                        {"success": False, "error": "Topic already exists"},
                        status=status.HTTP_400_BAD_REQUEST,
                    )
                existing_topic.name = name

            is_active = request.data.get("is_active")
            if is_active is not None and is_active != existing_topic.is_active:
                existing_topic.is_active = is_active

            description = request.data.get("description")
            if existing_topic.description != description:
                existing_topic.description = description

            sequence = request.data.get("sequence")
            if existing_topic.sequence != sequence:
                existing_topic.sequence = sequence

            domain = request.data.get("domain")
            if domain and domain != existing_topic.domain:
                change_domain = Domain.objects.get(pk=domain)
                existing_topic.domain = change_domain

            # mega_domain = request.data.get("mega_domain")
            # if mega_domain and mega_domain != existing_topic.mega_domain:
            #     change_mega_domain = MegaDomain.objects.get(pk=mega_domain)
            #     existing_topic.mega_domain = change_mega_domain

            existing_topic.save()
            serializer = TopicSerializer(existing_topic)

            return Response(
                {
                    "success": True,
                    "status": "success",
                    "message": "Topic updated successfully",
                    "results": [serializer.data],
                }
            )
        except Exception as e:
            print("Exception ====> ", e)
            return Response(
                {"success": False, "error": "Something went wrong"},
                status=status.HTTP_400_BAD_REQUEST,
            )


# sub topic
class SubTopicSerializer(BaseSerializer):
    # topic = TopicSerializer()

    class Meta:
        model = SubTopic
        fields = "__all__"


class SubTopicGetSerializer(BaseSerializer):
    topic = TopicGetSerializer(read_only=True)

    class Meta:
        model = SubTopic
        fields = [
            "id",
            "name",
            "description",
            "practice_sheet",
            "sequence",
            "topic",
        ]


class SubTopicViewSet(BaseViewset):
    permission_classes = (
        (
             read_only(IsStudent)
            | read_only(IsParent)
            | read_only(IsCounselor)
            | read_only(IsUserManager)
            | IsPlatformAdmin
            | IsTutor
            | IsManager
        ),
    )
    serializer_class = SubTopicSerializer
    model = SubTopic

    def list(self, request):
        try:
            subtopics = SubTopic.objects.all().order_by("id")
            domain_id = request.GET.get("domain_id")
            name = request.GET.get("name")
            topic = request.GET.get("topic")
            total_records = None

            if topic:
                subtopics = SubTopic.objects.filter(topic=topic).order_by("-created_at")
                serializer = SubTopicGetSerializer(subtopics, many=True)
            if domain_id:
                subtopics = SubTopic.objects.filter(
                    topic__domain__id=domain_id
                ).order_by("-created_at")
                serializer = SubTopicGetSerializer(subtopics, many=True)

            elif name:
                subtopics = subtopics.filter(Q(name__icontains=name))
                serializer = SubTopicGetSerializer(subtopics, many=True)
                total_records = subtopics.count()

            else:
                pass

            page = request.GET.get("page")
            page_size = request.GET.get("page_size", 10)
            paginator = PageNumberPagination()
            paginator.page_size = page_size

            if page:
                paginated_subtopics = paginator.paginate_queryset(subtopics, request)
                serializer = SubTopicGetSerializer(paginated_subtopics, many=True)
                total_records = subtopics.count()

            else:
                serializer = SubTopicGetSerializer(subtopics, many=True)
                total_records = subtopics.count()

            return Response(
                {
                    "success": True,
                    "status": "success",
                    "message": "",
                    "Total_records": total_records,
                    "results": serializer.data,
                }
            )
        except Exception as e:
            print("Exception=====>", e)
            return Response(
                {"success": False, "error": "Something went wrong"},
                status=status.HTTP_400_BAD_REQUEST,
            )

    def get_by_id(self, request, pk):
        try:
            existing_subtopic = SubTopic.objects.get(pk=pk)
            serializer = SubTopicGetSerializer(existing_subtopic)

            return Response(
                {
                    "success": True,
                    "status": "success",
                    "message": "",
                    "results": [serializer.data],
                }
            )
        except Domain.DoesNotExist:
            return Response(
                {"success": False, "error": "SubTopic not found"},
                status=status.HTTP_404_NOT_FOUND,
            )
        except Exception as e:
            print("Exception ====> ", e)
            return Response(
                {"success": False, "error": "Something went wrong"},
                status=status.HTTP_400_BAD_REQUEST,
            )

    def get_by_topicId(self, request, topic_id):
        try:
            sub_topics = SubTopic.objects.filter(topic_id=topic_id)
            serializer = SubTopicGetSerializer(sub_topics, many=True)

            return Response(
                {
                    "success": True,
                    "status": "success",
                    "message": "",
                    "results": [serializer.data],
                }
            )
        except Domain.DoesNotExist:
            return Response(
                {"success": False, "error": "SubTopic not found"},
                status=status.HTTP_404_NOT_FOUND,
            )
        except Exception as e:
            print("Exception ====> ", e)
            return Response(
                {"success": False, "error": "Something went wrong"},
                status=status.HTTP_400_BAD_REQUEST,
            )

    def create(self, request):

        name = request.data.get("name")
        if SubTopic.objects.filter(name__iexact=name).exists():
            return Response(
                {"success": False, "error": "SubTopic already exists"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        serializer = SubTopicSerializer(data=request.data)

        if serializer.is_valid(raise_exception=True):
            serializer.save()

        return Response(
            {
                "success": True,
                "status": "success",
                "message": "SubTopic saved successfully.",
                "results": [serializer.data],
            }
        )

    def update(self, request, pk):
        try:
            existing_subtopic = SubTopic.objects.get(pk=pk)
            name = request.data.get("name")

            if name and existing_subtopic.name != name:
                if SubTopic.objects.filter(name=name).exists():
                    return Response(
                        {"success": False, "error": "SubTopic already exists"},
                        status=status.HTTP_400_BAD_REQUEST,
                    )
                existing_subtopic.name = name

            is_active = request.data.get("is_active")
            if is_active is not None and is_active != existing_subtopic.is_active:
                existing_subtopic.is_active = is_active

            description = request.data.get("description")
            if description and existing_subtopic.description != description:
                existing_subtopic.description = description

            sequence = request.data.get("sequence")
            if sequence and existing_subtopic.sequence != sequence:
                existing_subtopic.sequence = sequence

            topic = request.data.get("topic")
            if topic and topic != existing_subtopic.topic:
                change_topic = Topic.objects.get(pk=topic)
                existing_subtopic.topic = change_topic

            practice_sheet = request.data.get("practice_sheet")
            if practice_sheet:
                existing_subtopic.practice_sheet = practice_sheet

            existing_subtopic.save()
            serializer = SubTopicGetSerializer(existing_subtopic)

            return Response(
                {
                    "success": True,
                    "status": "success",
                    "message": "SubTopic updated successfully",
                    "results": [serializer.data],
                }
            )
        except Exception as e:
            print("Exception ====> ", e)
            return Response(
                {"success": False, "error": "Something went wrong"},
                status=status.HTTP_400_BAD_REQUEST,
            )


# mother session plan
class SessionPlanSerializer(BaseSerializer):
    class Meta:
        model = SessionPlan
        fields = "__all__"


class GetSessionPlanSerializer(serializers.ModelSerializer):
    subject = SubjectSerializer()
    mega_domain = MegaDomainSerializer()
    topics = TopicSerializer(many=True, read_only=True)

    class Meta:
        model = SessionPlan
        fields = "__all__"


class SessionPlanGetSerializer(BaseSerializer):
    # subject = SubjectSerializer(read_only=True)
    mega_domain = MegaDomainGetSerializer(read_only=True)
    domain = DomainGetSerializer(read_only=True)

    class Meta:
        model = SessionPlan
        fields = [
            "id",
            "name",
            "description",
            "is_active",
            "sequence",
            "mega_domain",
            "domain",
        ]


class TopicTreeSerializer(BaseSerializer):
    sub_topics = SubTopicSerializer(many=True, source="subtopics.all")

    class Meta:
        model = Module
        fields = ["id", "name", "description", "sequence", "is_active", "sub_topics"]


class DomainTreeSerializer(BaseSerializer):
    topics = TopicTreeSerializer(many=True, source="topics.all")

    class Meta:
        model = Module
        fields = ["id", "name", "description", "sequence", "is_active", "topics"]


class ModuleTreeSerializer(BaseSerializer):
    domains = DomainTreeSerializer(many=True, source="domains.all")

    class Meta:
        model = Module
        fields = ["id", "name", "description", "sequence", "is_active", "domains"]


class SessionTreeSerializer(BaseSerializer):
    subject = SubjectSerializer(read_only=True)
    mega_domain = MegaDomainSerializer(read_only=True)
    modules = ModuleTreeSerializer(many=True, source="modules.all")

    class Meta:
        model = SessionPlan
        fields = [
            "id",
            "name",
            "description",
            "is_active",
            "sequence",
            "subject",
            "mega_domain",
            "modules",
        ]


class SessionPlanViewSet(BaseViewset):
    permission_classes = (IsPlatformAdmin,)
    serializer_class = SessionPlanSerializer
    model = SessionPlan

    def list(self, request):
        subject = request.GET.get("subject")
        if subject:
            serializer = SessionPlanGetSerializer(
                SessionPlan.objects.filter(
                    Q(subject=subject) & Q(is_active=True)
                ).order_by("-created_at"),
                many=True,
            )
        else:
            serializer = SessionPlanGetSerializer(
                SessionPlan.objects.filter(is_active=True).order_by("-created_at"),
                many=True,
            )

        return Response(
            {
                "success": True,
                "status": "success",
                "message": "",
                "results": serializer.data,
            }
        )

    def get_by_id(self, request, pk):
        try:
            existing_sessionplan = SessionPlan.objects.get(pk=pk)
            serializer = None
            if existing_sessionplan.is_active == True:
                serializer = SessionPlanGetSerializer(existing_sessionplan)

            return Response(
                {
                    "success": True,
                    "status": "success",
                    "message": "",
                    "results": [serializer.data] if serializer else [],
                }
            )
        except Domain.DoesNotExist:
            return Response(
                {"success": False, "error": "SessionPlan not found"},
                status=status.HTTP_404_NOT_FOUND,
            )
        except Exception as e:
            print("Exception ====> ", e)
            return Response(
                {"success": False, "error": "Something went wrong"},
                status=status.HTTP_400_BAD_REQUEST,
            )

    def get_session_tree(self, request):
        try:
            queryset = SessionPlan.objects.filter(is_active=True)
            serializer = SessionTreeSerializer(queryset, many=True).data
            return Response(
                {
                    "success": True,
                    "status": "success",
                    "message": "",
                    "results": serializer,
                }
            )

        except Exception as e:
            print("Exception ====> ", e)
            return Response(
                {"success": False, "error": "Something went wrong"},
                status=status.HTTP_400_BAD_REQUEST,
            )

    def get_session_tree_by_id(self, request, pk):
        try:
            queryset = SessionPlan.objects.get(pk=pk)
            print(queryset.is_active)
            serializer = None
            if queryset.is_active == True:
                serializer = SessionTreeSerializer([queryset], many=True).data
            else:
                serializer = []
            return Response(
                {
                    "success": True,
                    "status": "success",
                    "message": "",
                    "results": serializer,
                }
            )

        except Exception as e:
            print("Exception ====> ", e)
            return Response(
                {"success": False, "error": "Something went wrong"},
                status=status.HTTP_400_BAD_REQUEST,
            )

    def create(self, request):
        name = request.data.get("name")
        if SessionPlan.objects.filter(name=name).exists():
            return Response(
                {"success": False, "error": "SessionPlan already exists"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        serializer = SessionPlanSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            serializer.save()

        return Response(
            {
                "success": True,
                "status": "success",
                "message": "SessionPlan saved successfully.",
                "results": [serializer.data],
            }
        )

    def update(self, request, pk):
        try:
            existing_sessionplan = SessionPlan.objects.get(pk=pk)
            name = request.data.get("name")

            if existing_sessionplan.name != name:
                if SessionPlan.objects.filter(name=name).exists():
                    return Response(
                        {"success": False, "error": "SessionPlan already exists"},
                        status=status.HTTP_400_BAD_REQUEST,
                    )
                existing_sessionplan.name = name

            is_active = request.data.get("is_active")
            if is_active is not None and is_active != existing_sessionplan.is_active:
                existing_sessionplan.is_active = is_active

            description = request.data.get("description")
            if existing_sessionplan.description != description:
                existing_sessionplan.description = description

            sequence = request.data.get("sequence")
            if existing_sessionplan.sequence != sequence:
                existing_sessionplan.sequence = sequence

            mega_domain = request.data.get("mega_domain")
            if mega_domain and mega_domain != existing_sessionplan.mega_domain:
                change_mega_domain = MegaDomain.objects.get(pk=mega_domain)

                existing_sessionplan.mega_domain = change_mega_domain

            existing_sessionplan.save()
            serializer = SubTopicGetSerializer(existing_sessionplan)

            return Response(
                {
                    "success": True,
                    "status": "success",
                    "message": "Session plan updated successfully",
                    "results": [serializer.data],
                }
            )
        except Exception as e:
            print("Exception ====> ", e)
            return Response(
                {"success": False, "error": "Something went wrong"},
                status=status.HTTP_400_BAD_REQUEST,
            )


# student session plan
class StudentModuleSerializer(BaseSerializer):
    class Meta:
        model = StudentModule
        fields = "__all__"


class StudentModuleViewSet(BaseViewset, BasePaginator):
    permission_classes = (IsPlatformAdmin,)
    serializer = StudentModuleSerializer
    model = StudentModule

    def list(self, request):
        serializer = StudentModuleSerializer(StudentModule.objects.all(), many=True)

        return Response(
            {
                "success": True,
                "status": "success",
                "message": "",
                "results": serializer.data,
            }
        )


class StudentDomainSerializer(BaseSerializer):
    class Meta:
        model = StudentDomain
        fields = "__all__"


class StudentDomainViewSet(BaseViewset, BasePaginator):
    permission_classes = (IsPlatformAdmin,)
    serializer = StudentDomainSerializer
    model = StudentDomain

    def list(self, request):
        serializer = StudentDomainSerializer(StudentDomain.objects.all(), many=True)
        return Response(
            {
                "success": True,
                "status": "success",
                "message": "",
                "results": serializer.data,
            }
        )


class StudentTopicSerializer(BaseSerializer):
    class Meta:
        model = StudentTopic
        fields = "__all__"


class StudentTopicViewSet(BaseViewset, BasePaginator):
    permission_classes = (IsPlatformAdmin,)
    serializer = StudentTopicSerializer
    model = StudentTopic

    def list(self, request):
        serializer = StudentTopicSerializer(StudentTopic.objects.all(), many=True)
        return Response(
            {
                "success": True,
                "status": "success",
                "message": "",
                "results": serializer.data,
            }
        )


class StudentSubTopicSerializer(BaseSerializer):
    class Meta:
        model = StudentSubTopic
        fields = "__all__"


class StudentSubTopicViewSet(BaseViewset, BasePaginator):
    permission_classes = (IsPlatformAdmin,)
    serializer = StudentSubTopicSerializer
    model = StudentSubTopic

    def list(self, request):
        serializer = StudentSubTopicSerializer(StudentSubTopic.objects.all(), many=True)
        return Response(
            {
                "success": True,
                "status": "success",
                "message": "",
                "results": serializer.data,
            }
        )

    # in case a student needs extra assistance on a sub-topic
    def add_student_sub_topic(self, request):
        try:
            student_subtopic_id = request.data.get("student_subtopic_id")
            sub_topic_name = request.data.get("sub_topic_name")
            if StudentSubTopic.objects.filter(name=sub_topic_name).exists():
                return Response(
                    {
                        "success": False,
                        "error": "Student Subtopic with this name already exists",
                    },
                    status=status.HTTP_409_CONFLICT,
                )

            student_subtopic = StudentSubTopic.objects.get(pk=student_subtopic_id)
            sequence = request.data.get("sequence")

            new_student_subtopic = StudentSubTopic.objects.create(
                name=sub_topic_name,
                description=student_subtopic.description,
                sequence=sequence,
                is_active=True,
                is_extra=True,
                time=student_subtopic.time,
                student=student_subtopic.student,
                sub_topic=student_subtopic.sub_topic,
                student_topic=student_subtopic.student_topic,
            )
            new_student_subtopic.save()
            serializer = StudentSubTopicSerializer(new_student_subtopic)

            return Response(
                {
                    "success": True,
                    "status": "success",
                    "message": "",
                    "results": serializer.data,
                }
            )
        except Exception as e:
            print("Exception ====> ", e)
            return Response(
                {"success": False, "error": "Something went wrong"},
                status=status.HTTP_400_BAD_REQUEST,
            )


class StudentSessionPlanSerializer(BaseSerializer):
    class Meta:
        model = StudentSessionPlan
        fields = "__all__"


class StudentSessionPlanGetSerializer(BaseSerializer):
    mega_domain = MegaDomainGetSerializer(read_only=True)
    session_plan = SessionPlanGetSerializer(read_only=True)

    class Meta:
        model = SessionPlan
        fields = [
            "id",
            "name",
            "description",
            "sequence",
            "mega_domain",
            "session_plan",
        ]


class StudentTopicTreeSerializer(BaseSerializer):
    student_sub_topics = StudentSubTopicSerializer(
        many=True, source="student_subtopic.all"
    )

    class Meta:
        model = Module
        fields = [
            "id",
            "name",
            "description",
            "sequence",
            "is_active",
            "student_sub_topics",
        ]


class StudentDomainTreeSerializer(BaseSerializer):
    student_topics = StudentTopicTreeSerializer(many=True, source="student_topic.all")

    class Meta:
        model = Module
        fields = [
            "id",
            "name",
            "description",
            "sequence",
            "is_active",
            "student_topics",
        ]


class StudentModuleTreeSerializer(BaseSerializer):
    student_domains = StudentDomainTreeSerializer(
        many=True, source="student_domain.all"
    )

    class Meta:
        model = Module
        fields = [
            "id",
            "name",
            "description",
            "sequence",
            "is_active",
            "student_domains",
        ]


class NewMegaDomainSerializer(BaseSerializer):
    domains = DomainSerializer(many=True, read_only=True)

    class Meta:
        model = MegaDomain
        fields = "__all__"


class StudentSessionPlanTreeSerializer(BaseSerializer):
    session_plan = StudentSessionPlanSerializer(read_only=True)
    subject = SubjectSerializer()
    mega_domain = NewMegaDomainSerializer()

    class Meta:
        model = SessionPlan
        fields = [
            "id",
            "name",
            "description",
            "is_active",
            "sequence",
            "session_plan",
            "subject",
            "mega_domain",
            "is_completed",
        ]


class NewStudentSessionPlanTreeSerializer(BaseSerializer):
    session_plan = StudentSessionPlanSerializer(read_only=True)
    subject = SubjectSerializer()
    mega_domain = NewMegaDomainSerializer()

    class Meta:
        model = StudentSessionPlan
        fields = "__all__"
        # fields = [
        #     "id",
        #     "name",
        #     "description",
        #     "is_active",
        #     "session_plan",
        #     "subject",
        #     "mega_domain",
        #     "is_completed",
        # ]


class StudentSessionViewSet(BaseViewset, BasePaginator):
    permission_classes = (IsPlatformAdmin | IsStudent,)
    serializer = StudentSessionPlanSerializer
    model = StudentSessionPlan

    def list(self, request):
        try:
            subject = request.GET.get("subject")
            if subject:
                serializer = StudentSessionPlanSerializer(
                    StudentSessionPlan.objects.filter(subject=subject), many=True
                )
            else:
                serializer = StudentSessionPlanSerializer(
                    StudentSessionPlan.objects.all(), many=True
                )

            return Response(
                {
                    "success": True,
                    "status": "success",
                    "message": "",
                    "results": serializer.data,
                }
            )
        except Exception as e:
            print("Exception ====> ", e)
            return Response(
                {"success": False, "error": "Something went wrong"},
                status=status.HTTP_400_BAD_REQUEST,
            )

    def get_by_student_id(self, request, pk):
        try:
            serializer = NewStudentSessionPlanTreeSerializer(
                StudentSessionPlan.objects.filter(Q(student=pk) & Q(is_active=True)),
                many=True,
            )
            return Response(
                {
                    "success": True,
                    "status": "success",
                    "message": "",
                    "results": serializer.data,
                }
            )
        except User.DoesNotExist:
            return Response(
                {"success": False, "error": "User not found"},
                status=status.HTTP_404_NOT_FOUND,
            )
        except StudentSessionPlan.DoesNotExist:
            return Response(
                {"success": False, "error": "StudentSessionPlan not found"},
                status=status.HTTP_404_NOT_FOUND,
            )
        except Exception as e:
            print("Exception ====> ", e)
            return Response(
                {"success": False, "error": "Something went wrong"},
                status=status.HTTP_400_BAD_REQUEST,
            )

    def create(self, request):
        try:
            student_id = request.data.get("student_id")
            session_plan_ids = request.data.get("session_plan_ids")
            corePrep = request.data.get("core_prep")
            targetTest = request.data.get("target_test")

            english_reading_assigned = False
            english_writing_assigned = False
            math_assigned = False

            if StudentSessionPlan.objects.filter(
                Q(student=student_id) & Q(session_plan__in=session_plan_ids)
            ).exists():
                return Response(
                    {
                        "success": False,
                        "error": "This Session plan is already exists for this student",
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )

            student = User.objects.get(id=student_id)
            sub_topic_time = ""

            student_category = None
            session_plans = SessionPlan.objects.filter(pk__in=session_plan_ids)

            student_session_plans = []
            student_modules = []
            student_domains = []
            student_topics = []
            student_subtopics = []
            student_assignments = []
            subtopics = []  # addding
            student_assignment_questions = []
            student_question_options = []

            for session_plan in session_plans:
                if session_plan.subject.name == "English":
                    student_category = student.english_category
                elif session_plan.subject.name == "Math":
                    student_category = student.math_category

                if session_plan.mega_domain.name == "Reading":
                    print("session plan mega_domain==>", session_plan.mega_domain.name)
                    english_reading_assigned = True
                elif session_plan.mega_domain.name == "Writing":
                    english_writing_assigned = True
                    print("session plan mega_domain==>", session_plan.mega_domain.name)
                elif session_plan.mega_domain.name == "Math":
                    math_assigned = True
                    print("session plan mega_domain==>", session_plan.mega_domain.name)

                student_session_plan = StudentSessionPlan.objects.create(
                    name=session_plan.name,
                    description="Description",
                    subject=session_plan.subject,
                    mega_domain=session_plan.mega_domain,
                    student=student,
                    session_plan=session_plan,
                    corePrep=corePrep,
                    targetTest=targetTest,
                    category=student_category.name,
                )
                student_session_plans.append(student_session_plan)

                # creating student domains
                mother_session_molecule = MotherSessionMolecule.objects.filter(
                    session_plan=student_session_plan.session_plan
                ).values_list("molecule_id", flat=True)
                print("mother_session_molecule=========>", mother_session_molecule)

                molecule_ids = Molecule.objects.filter(
                    pk__in=mother_session_molecule
                ).values_list("domain_id", flat=True)
                print("tempMoleculedomain=========>", molecule_ids)

                domains = Domain.objects.filter(pk__in=molecule_ids, is_active=True)
                print("tempdomains=========>", domains)

                # domains = Domain.objects.filter(mega_domain=session_plan.mega_domain,is_active=True)
                # print("domains=======>",domains)

                for domain in domains:
                    student_domain = StudentDomain.objects.create(
                        name=domain.name,
                        description=domain.description,
                        sequence=domain.sequence,
                        is_active=domain.is_active,
                        domain=domain,
                        student=student,
                        student_session=student_session_plan,
                        # mega_domain=domain.mega_domain
                    )
                    student_domains.append(student_domain)
                    # creating student topics
                    topics = Topic.objects.filter(
                        domain=domain,
                        is_active=True,
                        moleculetopicsubtopic_id__molecule__id__in=mother_session_molecule,
                    ).distinct()
                    # topic_id = MoleculeTopicSubtopic.objects.filter(molecule_id__in=molecule_ids).values_list('topic_id')
                    # topics = Topic.objects.filter(pk__in=topic_id,is_active=True)
                    print("topics=======>", topics)
                    # print("Enter in topic")
                    for topic in topics:
                        if MoleculeTopicSubtopic.objects.filter(topic=topic).exists():
                            student_topic = StudentTopic.objects.create(
                                name=topic.name,
                                description=topic.description,
                                sequence=topic.sequence,
                                is_active=topic.is_active,
                                topic=topic,
                                student=student,
                                student_domain=student_domain,
                                # mega_domain=domain.mega_domain ##
                            )
                            student_topics.append(student_topic)

                            # subtopic_id = MoleculeTopicSubtopic.objects.filter(molecule_id__in=molecule_ids).values_list('subtopic_id')
                            # subtopics = Topic.objects.filter(pk__in=subtopic_id,is_active=True)
                            subtopics = SubTopic.objects.filter(
                                topic=topic,
                                is_active=True,
                                moleculetopicsubtopic_id__molecule__id__in=mother_session_molecule,
                            ).distinct()
                        for subtopic in subtopics:
                            # print("non-filtered subtopic====>",subtopic)
                            if MoleculeTopicSubtopic.objects.filter(
                                subtopic=subtopic
                            ).exists():
                                student_subtopic = StudentSubTopic.objects.create(
                                    name=subtopic.name,
                                    description=subtopic.description,
                                    sequence=subtopic.sequence,
                                    is_active=subtopic.is_active,
                                    time=sub_topic_time,
                                    student=student,
                                    sub_topic=subtopic,
                                    practice_sheet=subtopic.practice_sheet,
                                    student_topic=student_topic,
                                    # mega_domain=domain.mega_domain
                                )
                                # print("student_Subtopic====>",student_subtopics)
                            student_subtopics.append(student_subtopic)

                            # print("filter student_subtopics======>",student_subtopics)
                            assignments = Assignment.objects.filter(
                                subTopic=subtopic, is_active=True
                            )
                            # print("print after assignment==== 1842>", assignments)
                            # if len(assignments)<= 0:
                            #     print("success")

                            for assignment in assignments:
                                check_molecule_topic_subtopic = (
                                    MoleculeTopicSubtopic.objects.filter(
                                        subtopic=assignment.subTopic
                                    ).exists()
                                )
                                # print("check_molecule_topic_subtopic===>", check_molecule_topic_subtopic)
                                if (
                                    check_molecule_topic_subtopic
                                    and assignment.category == student_category.name
                                ):
                                    # if assignment.category == student_category.name:
                                    # print("Matching category found for assignment")
                                    student_assignment = (
                                        StudentAssignment.objects.create(
                                            name=assignment.name,
                                            description=assignment.description,
                                            is_active=assignment.is_active,
                                            marks=assignment.marks,
                                            type=assignment.type,
                                            subject=assignment.subject,
                                            subtopic=assignment.subTopic,
                                            assignment=assignment,
                                            student=student,
                                            megadomain=domain.mega_domain,
                                        )
                                    )

                                    student_assignments.append(student_assignment)
                                    assignment_questions = (
                                        AssignmentQuestion.objects.filter(
                                            assignment=assignment, is_active=True
                                        )
                                    )

                                    for assignment_question in assignment_questions:
                                        # print("student inside question=====> ", student)
                                        student_assignment_question = StudentAssignmentQuestion.objects.create(
                                            name=assignment_question.name,
                                            passage=assignment_question.passage,
                                            # description=assignment_question.description,
                                            is_active=assignment_question.is_active,
                                            sequence=assignment_question.sequence,
                                            # marks=assignment_question.marks,
                                            type=assignment_question.type,
                                            student_assignment=student_assignment,
                                            student=student,
                                            assignment_question=assignment_question,
                                        )
                                        student_assignment_questions.append(
                                            student_assignment_question
                                        )

                                        # creating student options
                                        question_options = (
                                            QuestionOption.objects.filter(
                                                questions=assignment_question,
                                                is_active=True,
                                            )
                                        )
                                        for question_option in question_options:
                                            # print("student inside question_option=====> ", student)
                                            student_question_option = StudentQuestionOption.objects.create(
                                                name=question_option.name,
                                                # description=question_option.description,
                                                is_active=question_option.is_active,
                                                sequence=question_option.sequence,
                                                student_assignment_question=student_assignment_question,
                                                student=student,
                                                question_option=question_option,
                                            )
                                            student_question_options.append(
                                                student_question_option
                                            )

            if english_reading_assigned:
                student.is_english_reading_assigned = True
            if english_writing_assigned:
                student.is_english_writing_assigned = True
            if math_assigned:
                student.is_math_assigned = True

            student.save()

            return Response(
                {
                    "success": True,
                    "status": "success",
                    "message": "Session Plans successfully assigned to the Student",
                    "results": [],
                }
            )

        except Exception as e:
            print("Exception ====> ", e)
            return Response(
                {"success": False, "error": "Something went wrong"},
                status=status.HTTP_400_BAD_REQUEST,
            )


########################


class MoleculeSerializer(BaseSerializer):

    subject = SubjectSerializer()
    mega_domain = MegaDomainSerializer()
    domain = DomainSerializer()

    class Meta:
        model = Molecule
        # fields = ['title', 'subject', 'mega_domain', 'domain', 'is_active']
        fields = "__all__"


# Assignment
class AssignmentSerializer(BaseSerializer):
    # subject = SubjectSerializer()
    subTopic = SubTopicSerializer()

    class Meta:
        model = Assignment
        fields = "__all__"


class GetAssignmentSerializer(BaseSerializer):

    subTopic = SubTopicSerializer(read_only=True)
    assignment = AssignmentSerializer(read_only=True)
    # options = QuestionOptionSerializer(many=True, source="question_options.all")

    topic = TopicSerializer(source="assignment.subTopic.topic", read_only=True)
    domain = DomainSerializer(source="assignment.subTopic.topic.domain", read_only=True)
    megaDomain = MegaDomainSerializer(
        source="assignment.subTopic.topic.domain.mega_domain", read_only=True
    )

    class Meta:
        model = Assignment
        fields = [
            "id",
            "updated_at",
            "name",
            "description",
            "is_active",
            "marks",
            "type",
            "domain",
            "topic",
            "subTopic",
            "category",
            "assignment",
            "megaDomain",
        ]


class AssignmentQuestionSerializer(BaseSerializer):
    class Meta:
        model = AssignmentQuestion
        fields = "__all__"


class QuestionOptionSerializer(BaseSerializer):
    class Meta:
        model = QuestionOption
        fields = "__all__"


class AssignmentQuestionGetSerializer(BaseSerializer):

    # subTopic = SubTopicSerializer(read_only=True)
    # assignment = AssignmentSerializer(read_only=True)
    # options = QuestionOptionSerializer(many=True, source="question_options.all")
    # topic = TopicSerializer(source="assignment.subTopic.topic", read_only=True)
    # domain = DomainGetSerializer(source="assignment.subTopic.topic.domain", read_only=True)
    # megaDomain = MegaDomainSerializer(source="assignment.subTopic.topic.domain.mega_domain",read_only=True),

    class Meta:
        model = AssignmentQuestion
        fields = [
            "id",
            "name",
            "passage",
            "is_active",
            "sequence",
            "type",
            "explanation",
            "remarks",
            "enter_your_answer",
            # "assignment",
            # "options",
            # "subTopic",
            # "topic",
            # "domain",
            # "megaDomain",
        ]


class CustomPagination(PageNumberPagination):
    page_size = 10  # Display 10 items per page
    page_size_query_param = (
        "page_size"  # Allow client to override the page size via query parameter
    )
    max_page_size = 100


class AssignmentViewSet(BaseViewset, BasePaginator):
    permission_classes = ((IsPlatformAdmin | IsTypist),)
    serializer = AssignmentSerializer

    model = Assignment
    fields = ["id", "name", "description", "marks", "type", "category", "pdf_url"]

    filter_backends = [rest_filters.SearchFilter]
    # search_fields = ("name", "type", "category")

    def list(self, request):
        try:
            assignments = Assignment.objects.all().order_by("id")
            # assignments = Assignment.objects.all().order_by(F('type').asc(), F('name').asc(),F('category').asc())

            search_term = request.GET.get("search", None)
            search_field = request.GET.get("search_field")

            # for search_term, search_field in zip(search_terms, search_fields):
            if search_term:
                if search_field == "category":
                    assignments = assignments.filter(category__icontains=search_term)
                elif search_field == "type":
                    assignments = assignments.filter(type__icontains=search_term)
                elif search_field == "name":
                    assignments = assignments.filter(name__icontains=search_term)

            type_filter = request.GET.get("type", None)
            if type_filter:
                assignments = assignments.filter(type__icontains=type_filter)

            category_filter = request.GET.get("category", None)
            if category_filter:
                assignments = assignments.filter(category__icontains=category_filter)

            name_filter = request.GET.get("name", None)
            if name_filter:
                assignments = assignments.filter(name__icontains=name_filter)

            paginator = PageNumberPagination()
            paginator.page_size = request.GET.get("page_size", 10)
            paginated_assignments = paginator.paginate_queryset(
                assignments, self.request
            )

            serializer = GetAssignmentSerializer(paginated_assignments, many=True)

            assignment_data = []

            for assignment_serializer_data in serializer.data:
                existing_assignment_id = assignment_serializer_data["id"]
                existing_assignment = assignments.get(id=existing_assignment_id)

                sub_topic_data = None
                topic_data = None
                domain_data = None
                mega_domain_data = None

                if existing_assignment.subTopic:
                    sub_topic = existing_assignment.subTopic
                    # sub_topic = existing_assignment.subTopic.order_by('name')
                    sub_topic_data = SubTopicSerializer(sub_topic).data
                    topic_data = TopicSerializer(sub_topic.topic).data
                    domain_data = DomainSerializer(sub_topic.topic.domain).data
                    mega_domain_data = MegaDomainSerializer(
                        sub_topic.topic.domain.mega_domain
                    ).data

                assignment_data.append(
                    {
                        **assignment_serializer_data,
                        "topic": topic_data,
                        "domain": domain_data,
                        "megaDomain": mega_domain_data,
                    }
                )

            total_records = assignments.count()

            return Response(
                {
                    "success": True,
                    "status": "success",
                    "message": "",
                    "total_records": total_records,
                    "results": assignment_data,
                }
            )

        except Exception as e:
            print("Exception ====> ", e)
            return Response(
                {"success": False, "error": "Something went wrong"},
                status=status.HTTP_400_BAD_REQUEST,
            )

    def get_by_id(self, request, pk):
        try:
            existing_assignment = Assignment.objects.get(pk=pk)
            serializer = GetAssignmentSerializer(existing_assignment)

            sub_topic_data = None
            topic_data = None
            domain_data = None
            mega_domain_data = None

            # if existing_assignment.assignment:
            #     assignment = existing_assignment.assignment

            if existing_assignment.subTopic:
                sub_topic = existing_assignment.subTopic

                sub_topic_data = SubTopicSerializer(sub_topic).data
                topic_data = TopicSerializer(sub_topic.topic).data
                domain_data = DomainGetSerializer(sub_topic.topic.domain).data
                mega_domain_data = MegaDomainSerializer(
                    sub_topic.topic.domain.mega_domain
                ).data

            return Response(
                {
                    "success": True,
                    "status": "success",
                    "message": "",
                    "results": [
                        {
                            **serializer.data,
                            "topic": topic_data,
                            "domain": domain_data,
                            "megaDomain": mega_domain_data,
                        }
                    ],
                }
            )
        except Assignment.DoesNotExist:
            return Response(
                {"success": False, "error": "Assignment not found"},
                status=status.HTTP_404_NOT_FOUND,
            )
        except Exception as e:
            print("Exception ====> ", e)
            return Response(
                {"success": False, "error": "Something went wrong"},
                status=status.HTTP_400_BAD_REQUEST,
            )

    def create(self, request):
        try:
            existing_assignment = Assignment.objects.filter(
                name__iexact=request.data.get("name")
            )
            print("existing_assignment is:", existing_assignment)
            if existing_assignment.exists():
                return Response(
                    {"success": False, "error": "Assignment already exists"},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            print("category is:", request.data.get("category"))
            subtopic_id = request.data.get("subtopic")
            subTopic = SubTopic.objects.get(pk=subtopic_id)

            subject_id = request.data.get("subject")
            subject = Subject.objects.get(pk=subject_id)

            assignment = Assignment.objects.create(
                name=request.data.get("name"),
                description=request.data.get("description"),
                type=request.data.get("type"),
                # sequence=request.data.get("sequence"),
                subTopic=subTopic,
                category=request.data.get("category"),
                subject=subject,
                pdf_url=request.data.get("pdf_url"),
            )

            serializer = AssignmentSerializer(assignment)

            return Response(
                {
                    "success": True,
                    "status": "success",
                    "message": "Assignment saved successfully.",
                    "results": serializer.data,
                }
            )

        except Exception as e:
            print("Exception ====> ", e)
            return Response(
                {"success": False, "error": "Something went wrong"},
                status=status.HTTP_400_BAD_REQUEST,
            )

    def update(self, request, pk):
        try:
            existing_assignment = Assignment.objects.get(pk=pk)

            name = request.data.get("name")
            if name is not None and existing_assignment.name != name:
                if Assignment.objects.filter(name=name).exists():
                    return Response(
                        {"success": False, "error": "Assignment already exists"},
                        status=status.HTTP_400_BAD_REQUEST,
                    )
                existing_assignment.name = name

            is_active = request.data.get("is_active")
            if is_active is not None and is_active != existing_assignment.is_active:
                existing_assignment.is_active = is_active

            description = request.data.get("description")
            if (
                description is not None
                and existing_assignment.description != description
            ):
                existing_assignment.description = description

            sub_topic_id = request.data.get("subtopic")
            if (
                sub_topic_id is not None
                and sub_topic_id != existing_assignment.subTopic_id
            ):
                change_sub_topic = SubTopic.objects.get(pk=sub_topic_id)
                existing_assignment.subTopic = change_sub_topic

            # sequence = request.data.get("sequence")
            # if sequence is not None and existing_assignment.sequence != sequence:
            #     existing_assignment.sequence = sequence

            type = request.data.get("type")
            if type is not None and existing_assignment.type != type:
                existing_assignment.type = type

            category = request.data.get("category")
            if existing_assignment.category != category:
                existing_assignment.category = category

            existing_assignment.save()
            serializer = AssignmentSerializer(existing_assignment)

            return Response(
                {
                    "success": True,
                    "status": "success",
                    "message": "Assignment updated successfully",
                    "results": [serializer.data],
                }
            )
        except Exception as e:
            print("Exception ====> ", e)
            return Response(
                {"success": False, "error": "Something went wrong"},
                status=status.HTTP_400_BAD_REQUEST,
            )

    search_fields = ("subject__name",)

    filter_backends = (
        filters.DjangoFilterBackend,
        rest_filters.SearchFilter,
    )

    pagination_class = CustomPagination()

    def get_completed_assignments(self, request, user_id):
        try:
            queryset = StudentAssignment.objects.filter(
                student_id=user_id, is_completed=True
            ).order_by("-created_at")
            # print("queryset===>",queryset)
            assignment_type = request.query_params.get("type", None)

            # print("Assignment Type:", assignment_type)
            if assignment_type:
                queryset = queryset.filter(type__iexact=assignment_type)
                queryset = queryset.annotate(assignment_length=Length("name")).order_by(
                    "assignment_length", "name"
                )

            for backend in list(self.filter_backends):
                print("==>")
                queryset = backend().filter_queryset(request, queryset, self)

                print("queryset====>", queryset)

            page = self.pagination_class.paginate_queryset(queryset, request, view=self)
            if page is not None:
                serializer = NewStudentAssignmentSerializer(page, many=True)
                return self.pagination_class.get_paginated_response(serializer.data)

            serializer = NewStudentAssignmentSerializer(queryset, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)

        except Exception as e:
            print("Exception =====>", e)
            return Response(
                {"success": False, "error": "Something went wrong"},
                status=status.HTTP_400_BAD_REQUEST,
            )


class QuestionOptionSerializer(BaseSerializer):
    class Meta:
        model = QuestionOption
        fields = ["id", "name", "is_active", "is_correct", "questions"]


class AssignmentQuestionViewSet(BaseViewset, BasePaginator):
    permission_classes = ((IsPlatformAdmin | IsTypist),)

    def list(self, request):
        assignment_id = request.GET.get("assignment")
        print("@@@@@@@@@@@@@@@", assignment_id)

        assignment_data = []

        if assignment_id:
            assignment_questions = AssignmentQuestion.objects.filter(
                assignment=assignment_id
            ).order_by("-created_at")

            for assignment_question in assignment_questions:
                assignment_serializer = AssignmentQuestionGetSerializer(
                    assignment_question
                )
                question_options = assignment_question.question_options.all()
                question_option_data = QuestionOptionSerializer(
                    question_options, many=True
                ).data

                assignment_data.append(
                    {
                        **assignment_serializer.data,
                        "question_options": question_option_data,
                    }
                )

        return Response(
            {
                "success": True,
                "status": "success",
                "message": "",
                "results": assignment_data,
            }
        )

    def get_by_id(self, request, pk):
        try:
            existing_question = AssignmentQuestion.objects.get(pk=pk)
            serializer = AssignmentQuestionGetSerializer(existing_question)

            sub_topic_data = None
            topic_data = None
            domain_data = None
            mega_domain_data = None
            assignment_data = None
            question_option_data = None

            if existing_question.assignment:
                assignment = existing_question.assignment

                if assignment.subTopic:
                    sub_topic = assignment.subTopic

                    sub_topic_data = SubTopicSerializer(sub_topic).data
                    topic_data = TopicSerializer(sub_topic.topic).data
                    domain_data = DomainGetSerializer(sub_topic.topic.domain).data
                    mega_domain_data = MegaDomainSerializer(
                        sub_topic.topic.domain.mega_domain
                    ).data
                    assignment_data = GetAssignmentSerializer(assignment).data

                    question_options = existing_question.question_options.all()
                    question_option_data = QuestionOptionSerializer(
                        question_options, many=True
                    ).data

            return Response(
                {
                    "success": True,
                    "status": "success",
                    "message": "",
                    "results": [
                        {
                            **serializer.data,
                            "assignment": assignment_data,
                            "topic": topic_data,
                            "domain": domain_data,
                            "megaDomain": mega_domain_data,
                            "question_options": question_option_data,
                        }
                    ],
                }
            )
        except AssignmentQuestion.DoesNotExist:
            return Response(
                {"success": False, "error": "Question not found"},
                status=status.HTTP_404_NOT_FOUND,
            )
        except Exception as e:
            print("Exception ====> ", e)
            return Response(
                {"success": False, "error": "Something went wrong"},
                status=status.HTTP_400_BAD_REQUEST,
            )

    def create(self, request):
        try:
            question = request.data
            # print("@@@@@@@@@@@@@@@@@",question)

            options = request.data.get("options")

            assignment = Assignment.objects.get(pk=question.get("assignment"))

            # if AssignmentQuestion.objects.filter(
            #     Q(assignment=assignment) & Q(name=question.get("name"))
            # ).exists():
            #     return Response(
            #         {"success": False, "error": "Question already exists"},
            #         status=status.HTTP_400_BAD_REQUEST,
            #     )
            # print("name is:", question.get("name"))
            # print("type is:", question.get("type"))
            # print("explanation is:", question.get("explanation"))
            # print("passage is:", question.get("passage"))
            # print("remarks is:", question.get("remarks"))

            # exclude_keys = {'assignment', 'is_active'}

            # if any((isinstance(value, str) and value.strip() == '' or value is None) for key, value in question.items() if type(value) in (bool, int) and key not in exclude_keys):
            #     return Response(
            #         {"success": False, "error": "white space and null value not allowed."},
            #         status=status.HTTP_400_BAD_REQUEST,
            #     )

            new_question = AssignmentQuestion.objects.create(
                name=question.get("name"),
                # description=question.get("description"),
                is_active=True,
                # marks=question.get("marks"),465167
                type=question.get("type"),
                explanation=question.get("explanation"),
                passage=question.get("passage"),
                remarks=question.get("remarks"),
                enter_your_answer=question.get("enter_your_answer"),
                sequence=question.get("sequence"),
                assignment=assignment,
            )

            option_list = []
            for option in options:
                opt = QuestionOption.objects.create(
                    name=option.get("name"),
                    # description=option.get("description"),
                    is_active=True,
                    is_correct=option.get("is_correct"),
                    sequence=option.get("sequence"),
                    questions=new_question,
                )
                option_list.append(model_to_dict(opt))

            new_question_data = AssignmentQuestionGetSerializer(new_question).data
            new_question_data["question_options"] = option_list

            return Response(
                {
                    "success": True,
                    "status": "success",
                    "message": "Question saved successfully.",
                    "results": [new_question_data],
                }
            )
        except Exception as e:
            print("Exception ====> ", e)
            return Response(
                {"success": False, "error": "Something went wrong"},
                status=status.HTTP_400_BAD_REQUEST,
            )

    def update(self, request, pk):
        try:
            question = request.data
            options = question.get("options")
            existing_question = AssignmentQuestion.objects.get(pk=pk)
            existing_options = QuestionOption.objects.filter(
                questions=existing_question
            )

            # updating question
            if question.get(
                "name"
            ) is not None and existing_question.name != question.get("name"):
                existing_question.name = question.get("name")
            if question.get(
                "passage"
            ) is not None and existing_question.passage != question.get("passage"):
                existing_question.passage = question.get("passage")
            if question.get(
                "sequence"
            ) is not None and existing_question.sequence != question.get("sequence"):
                existing_question.sequence = question.get("sequence")
            if question.get(
                "type"
            ) is not None and existing_question.type != question.get("type"):
                existing_question.type = question.get("type")
            if question.get(
                "explanation"
            ) is not None and existing_question.explanation != question.get(
                "explanation"
            ):
                existing_question.explanation = question.get("explanation")
            if question.get(
                "remarks"
            ) is not None and existing_question.remarks != question.get("remarks"):
                existing_question.remarks = question.get("remarks")

            if question.get(
                "enter_your_answer"
            ) is not None and existing_question.enter_your_answer != question.get(
                "enter_your_answer"
            ):
                existing_question.enter_your_answer = question.get("enter_your_answer")

            if question.get(
                "is_active"
            ) is not None and existing_question.is_active != question.get("is_active"):
                existing_question.is_active = question.get("is_active")

            existing_question.save()

            # for option in existing_options:

            #     if option.name != options.get("name"):
            #        option.name = options.get("name")
            #        option.save()

            #     if   option.is_active != options.get("is_active"):
            #          option.is_active = options.get("is_active")
            #          option.save()

            #     if option.is_correct != options.get("is_correct"):
            #        option.is_correct = options.get("is_correct")
            #        option.save()

            #     if option.sequence != options.get("sequence"):
            #        option.sequence = options.get("sequence")
            #        option.save()
            # option.save()

            # updating options
            option_list = []
            for option in options:
                if option.get("id") is None:
                    opt = QuestionOption.objects.create(
                        name=option.get("name"),
                        is_active=True,
                        is_correct=option.get("is_correct"),
                        sequence=option.get("sequence"),
                        questions=existing_question,
                    )
                    option_list.append(opt)
                else:
                    for existing_option in existing_options:
                        if option.get("id") == existing_option.id:
                            should_update = False
                            if option.get(
                                "name"
                            ) is not None and existing_option.name != option.get(
                                "name"
                            ):
                                should_update = True
                                existing_option.name = option.get("name")
                            if option.get(
                                "is_active"
                            ) is not None and existing_option.is_active != option.get(
                                "is_active"
                            ):
                                should_update = True
                                existing_option.is_active = option.get("is_active")
                            if option.get(
                                "is_correct"
                            ) is not None and existing_option.is_correct != option.get(
                                "is_correct"
                            ):
                                should_update = True
                                existing_option.is_correct = option.get("is_correct")
                            if option.get(
                                "sequence"
                            ) is not None and existing_option.sequence != option.get(
                                "sequence"
                            ):
                                should_update = True
                                existing_option.sequence = option.get("sequence")
                            if should_update:
                                existing_option.save()
                                should_update = False

            for option in options:
                for existing_option in existing_options:
                    if option.get("id") == existing_option.id:
                        should_update = False
                        if existing_option.name != option.get("name"):
                            should_update = True
                            existing_option.name = option.get("name")
                        if existing_option.is_active != option.get("is_active"):
                            should_update = True
                            existing_option.is_active = option.get("is_active")
                        if existing_option.is_correct != option.get("is_correct"):
                            should_update = True
                            existing_option.is_correct = option.get("is_correct")
                        if existing_option.sequence != option.get("sequence"):
                            should_update = True
                            existing_option.sequence = option.get("sequence")
                        if should_update:
                            existing_option.save()
                            should_update = False

            return Response(
                {
                    "success": True,
                    "status": "success",
                    "message": "Question updated successfully.",
                    "results": [
                        AssignmentQuestionGetSerializer(existing_question).data
                    ],
                }
            )
        except AssignmentQuestion.DoesNotExist:
            return Response(
                {"success": False, "error": "AssignmentQuestion not found"},
                status=status.HTTP_404_NOT_FOUND,
            )
        except Exception as e:
            print("Exception ====> ", e)
            return Response(
                {"success": False, "error": "Something went wrong"},
                status=status.HTTP_400_BAD_REQUEST,
            )

    def delete(self, request, pk):
        print("enter")
        try:
            question = AssignmentQuestion.objects.get(pk=pk)
            print("question===>", question)
        except AssignmentQuestion.DoesNotExist:
            return Response(
                {"error": "AssignmentQuestion not found"},
                status=status.HTTP_404_NOT_FOUND,
            )
        question_options = question.question_options.all()
        print("question_options===>", question_options)
        question_options.delete()

        question.delete()
        return Response({"success": True}, status=status.HTTP_204_NO_CONTENT)


class StudentAssignmentSerializer(BaseSerializer):

    class Meta:
        model = StudentAssignment
        fields = ["id", "name", "description"]


class NewStudentAssignmentSerializer(BaseSerializer):
    subject_name = serializers.ReadOnlyField(source="subject.name")

    class Meta:
        model = StudentAssignment
        fields = "__all__"
        read_only_fields = ("subject_name",)


class StudentAssignmentViewSet(BaseViewset, BasePaginator):
    permission_classes = (IsPlatformAdmin,)

    def get_by_student_id(self, request, pk):
        serializer = StudentAssignmentSerializer(
            StudentAssignment.objects.filter(student_id=pk), many=True
        )

        return Response(
            {
                "success": True,
                "status": "success",
                "message": "",
                "results": serializer.data,
            }
        )


# reason for error
class ReasonForErrorSerailizer(BaseSerializer):
    class Meta:
        model = ReasonForError
        fields = "__all__"


class ReasonForErrorViewSet(BaseViewset):
    serializer_class = ReasonForErrorSerailizer
    model = ReasonForError

    def list(self, request):
        topic = request.GET.get("topic")
        if topic:
            serializer = ReasonForErrorSerailizer(
                ReasonForError.objects.filter(topic=topic), many=True
            )
        else:
            serializer = ReasonForErrorSerailizer(
                ReasonForError.objects.all(), many=True
            )
        return Response(serializer.data)


# code use to get custom api link created by suresh
class Create_custom_Link(BaseViewset):
    permission_classes = (IsPlatformAdmin,)

    def get_custom_link_data(self, request):
        data = [
            {
                "subject_name": "math",
                "Chapter": "chapter1",
                "Upcoming_Date": date.today(),
                "meeting_link": "http://zoom.com",
            },
            {
                "subject_name": "math",
                "Chapter": "chapter1",
                "Upcoming_Date": date.today(),
                "meeting_link": "http://zoom.com",
            },
            {
                "subject_name": "math",
                "Chapter": "chapter1",
                "Upcoming_Date": date.today(),
                "meeting_link": "http://zoom.com",
            },
        ]
        return Response({"result": data})


class HomeAssignment(BaseViewset):
    permission_classes = (IsPlatformAdmin,)

    def get_homeassignment(self, request):
        data = [
            {
                "subject_name": "math",
                "chapter": "chapter2",
                "Upcoming_Date": datetime.now(),
                "meeting_link": "http://zoom.com",
            },
            {
                "subject_name": "math",
                "chapter": "chapter2",
                "Upcoming_Date": datetime.now(),
                "meeting_link": "http://zoom.com",
            },
            {
                "subject_name": "math",
                "chapter": "chapter2",
                "Upcoming_Date": datetime.now(),
                "meeting_link": "http://zoom.com",
            },
        ]
        return Response({"result": data})


# getting all module list api created by suresh yadav


class NewModuleSerilializer(BaseSerializer):
    # mega_domain = MegaDomainGetSerializer(read_only=True)

    class Meta:
        model = Module
        fields = ["id", "name", "description", "sequence"]


class ListModuleViewSet(BaseViewset):
    permission_classes = (IsPlatformAdmin,)
    serializer_class = NewModuleSerilializer
    model = Module
    fields = ["id", "name", "description", "sequence"]

    def list(self, request):
        mega_domain = request.GET.get("name")
        print("mega_domain is:", mega_domain)
        if mega_domain:
            serializer = NewModuleSerilializer(
                Module.objects.filter(name=mega_domain).order_by("-created_at"),
                many=True,
            )
        else:
            serializer = NewModuleSerilializer(
                Module.objects.all().order_by("-created_at"), many=True
            )
        return Response(
            {
                "success": True,
                "status": "success",
                "message": "",
                "results": serializer.data,
            }
        )

    def get_by_id(self, request, pk):
        try:
            existing_module = Module.objects.get(pk=pk)
            serializer = NewModuleSerilializer(existing_module)

            return Response(
                {
                    "success": True,
                    "status": "success",
                    "message": "",
                    "results": [serializer.data],
                }
            )
        except Module.DoesNotExist:
            return Response(
                {"success": False, "error": "Module not found"},
                status=status.HTTP_404_NOT_FOUND,
            )
        except Exception as e:
            print("Exception ====> ", e)
            return Response(
                {"success": False, "error": "Something went wrong"},
                status=status.HTTP_400_BAD_REQUEST,
            )

    def create(self, request):
        try:
            name = request.data.get("name")
            print("name is:", name)
            existing_module = Module.objects.filter(name=name)
            if existing_module:
                return Response(
                    {"success": False, "error": "Module already exists"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            serializer = NewModuleSerilializer(data=request.data)
            if serializer.is_valid(raise_exception=True):
                serializer.save()

            return Response(
                {
                    "success": True,
                    "status": "success",
                    "message": "Module saved successfully.",
                    "results": serializer.data,
                }
            )
        except Exception as e:
            print("Exception ====> ", e)
            return Response(
                {"success": False, "error": "Something went wrong"},
                status=status.HTTP_400_BAD_REQUEST,
            )

    def update(self, request, pk):
        try:
            existing_module = Module.objects.get(pk=pk)
            name = request.data.get("name")

            if existing_module.name != name:
                if Module.objects.filter(name=name).exists():
                    return Response(
                        {"success": False, "error": "Module already exists"},
                        status=status.HTTP_400_BAD_REQUEST,
                    )
                existing_module.name = name

            description = request.data.get("description")
            if existing_module.description != description:
                existing_module.description = description

            sequence = request.data.get("sequence")
            if existing_module.sequence != sequence:
                existing_module.sequence = sequence

            # mega_domain = request.data.get("mega_domain")
            # if mega_domain and mega_domain != existing_module.mega_domain:
            #     change_megadomain = MegaDomain.objects.get(pk=mega_domain)
            #     existing_module.mega_domain = change_megadomain

            existing_module.save()
            serializer = NewModuleSerilializer(existing_module)

            return Response(
                {
                    "success": True,
                    "status": "success",
                    "message": "Module updated successfully",
                    "results": [serializer.data],
                }
            )
        except Exception as e:
            print("Exception ====> ", e)
            return Response(
                {"success": False, "error": "Something went wrong"},
                status=status.HTTP_400_BAD_REQUEST,
            )


# class SubTopicSerializer(serializers.ModelSerializer):
#     topic = TopicSerializer(read_only=True)
#     class Meta:
#         model = SubTopic
#         fields = "__all__"


class TopicSerializer(serializers.ModelSerializer):
    # assignments = AssignmentSerializer(many=True)
    subtopics = SubTopicSerializer(many=True, read_only=True)

    class Meta:
        model = Topic
        fields = "__all__"


class DomainTopicSerilazer(serializers.ModelSerializer):
    topic = TopicSerializer(many=True, read_only=True)

    class Meta:
        model = Domain
        fields = "__all__"


class MegaDomainTopicSerializer(serializers.ModelSerializer):
    domains = DomainTopicSerilazer(many=True)

    class Meta:
        model = MegaDomain
        fields = "__all__"


class MoleculeTopicSubtopicSerializer(serializers.ModelSerializer):
    molecule = MoleculeSerializer()
    topic = TopicSerializer(read_only=True)
    subtopics = SubTopicSerializer(read_only=True)

    class Meta:
        model = MoleculeTopicSubtopic
        fields = "__all__"


class MoleculeSerializers(serializers.ModelSerializer):
    class Meta:
        model = Molecule
        fields = [
            "id",
            "title",
            "is_active",
            "created_at",
            "updated_at",
            "domain",
            "mega_domain",
            "subject",
        ]


class MoleculeGetSerializer(serializers.ModelSerializer):

    molecule_topic_subtopics = MoleculeTopicSubtopicSerializer(
        many=True, read_only=True
    )
    topics = TopicSerializer(many=True, read_only=True)
    subtopics = SubTopicSerializer(many=True, read_only=True)
    subject = SubjectSerializer(read_only=True)
    mega_domain = MegaDomainSerializer(read_only=True)
    domain = DomainSerializer(read_only=True)

    class Meta:
        model = Molecule
        fields = [
            "id",
            "title",
            "is_active",
            "subject",
            "mega_domain",
            "domain",
            "topics",
            "subtopics",
            "molecule_topic_subtopics",
        ]


class GetMotherSessionMoleculeSerializer(BaseSerializer):
    class Meta:
        model = MotherSessionMolecule
        fields = "__all__"


class MoleculeViewSet(BaseViewset):
    permission_classes = ((IsPlatformAdmin | IsTypist | IsManager),)

    def list(self, request):

        try:

            archive_param = request.GET.get("archive")
            subject_param = request.GET.get("subject")
            mega_domain_param = request.GET.get("mega_domain")
            name_param = request.GET.get("name")
            molecule_topic_subtopics = []
            paginated_results = []
            total_records = None

            if archive_param == "false" or archive_param is None:
                molecule_topic_subtopics = MoleculeTopicSubtopic.objects.filter(
                    molecule__is_active=True
                ).order_by("id")
            else:
                molecule_topic_subtopics = MoleculeTopicSubtopic.objects.filter(
                    molecule__is_active=False
                ).order_by("id")

            if subject_param:
                molecule_topic_subtopics = molecule_topic_subtopics.filter(
                    Q(molecule__subject__name=subject_param)
                )

            if mega_domain_param:
                molecule_topic_subtopics = molecule_topic_subtopics.filter(
                    Q(molecule__mega_domain__name=mega_domain_param)
                )

            if name_param:
                molecule_topic_subtopics = molecule_topic_subtopics.filter(
                    Q(molecule__title__icontains=name_param)
                )

            # if request.GET.get("page") is None and request.GET.get("page_size") is None:
            #     molecule_topic_subtopics = MoleculeTopicSubtopic.objects.all().order_by("id")

            unique_molecules = defaultdict(dict)

            for molecule_topic_subtopic in molecule_topic_subtopics:
                molecule_id = molecule_topic_subtopic.molecule.id
                subtopic_data = SubTopicSerializer(
                    molecule_topic_subtopic.subtopic
                ).data

                if "subtopics" not in unique_molecules[molecule_id]:
                    unique_molecules[molecule_id]["subtopics"] = []

                existing_subtopics = {
                    subtopic["id"]
                    for subtopic in unique_molecules[molecule_id]["subtopics"]
                }

                if subtopic_data["id"] not in existing_subtopics:
                    unique_molecules[molecule_id]["subtopics"].append(subtopic_data)

                if "id" not in unique_molecules[molecule_id]:
                    unique_molecules[molecule_id].update(
                        MoleculeGetSerializer(molecule_topic_subtopic.molecule).data
                    )

            total_records = len(unique_molecules)
            # results = list(unique_molecules.values())
            if request.GET.get("page") != None and request.GET.get("page_size"):
                page = request.GET.get("page", 1)
                per_page = 10
                sorted_molecules = sorted(
                    unique_molecules.values(), key=itemgetter("id")
                )
                paginator = Paginator(sorted_molecules, per_page)
                # paginator = Paginator(list(unique_molecules.values()), per_page)
                paginated_results = paginator.get_page(page)
                paginated_results = paginated_results.object_list
            else:
                paginated_results = list(unique_molecules.values())

                # if archive_param == 'false' or archive_param is None:
                #     filtered_records = Molecule.objects.filter(is_active=True)
                # else:
                #     filtered_records = Molecule.objects.filter(is_active=False)

                # if subject_param:
                #     filtered_records = filtered_records.filter(subject__name=subject_param)

                # if name_param:
                #     filtered_records = filtered_records.filter(title__icontains=name_param)

                # total_records = filtered_records.count()

            return Response(
                {
                    "success": True,
                    "status": "success",
                    "message": "",
                    "total_records": total_records,
                    "results": paginated_results,
                }
            )

        except Exception as e:
            print("Exception ====> ", e)
            return Response(
                {"success": False, "error": "Something went wrong"},
                status=status.HTTP_400_BAD_REQUEST,
            )

    def get_by_id(self, request, pk):

        molecule = Molecule.objects.get(id=pk)
        molecule_serializer = MoleculeGetSerializer(molecule).data

        molecule_topic_subtopics = MoleculeTopicSubtopic.objects.filter(molecule_id=pk)
        topics = []
        topic_dict = {}

        for molecule_topic_subtopic in molecule_topic_subtopics:

            topic_serializer = TopicSerializer(molecule_topic_subtopic.topic)
            topic_data = topic_serializer.data

            subtopic_serializer = SubTopicSerializer(molecule_topic_subtopic.subtopic)
            subtopic_data = subtopic_serializer.data

            if topic_data["id"] not in topic_dict:
                topic_dict[topic_data["id"]] = {
                    "id": topic_data["id"],
                    "name": topic_data["name"],
                    "subtopics": [],
                }

            topic_dict[topic_data["id"]]["subtopics"].append(subtopic_data)

        topics = list(topic_dict.values())
        molecule_serializer["topics"] = topics

        return Response(
            {
                "success": True,
                "status": "success",
                "message": "",
                "results": molecule_serializer,
            }
        )

    def create(self, request):
        try:
            title = request.data.get("title")
            if Molecule.objects.filter(title__iexact=title).exists():
                return Response(
                    {"success": False, "error": "Molecule already exists"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            subject = Subject.objects.get(pk=request.data.get("subject"))
            megadomain = MegaDomain.objects.get(pk=request.data.get("megadomain"))
            domain = Domain.objects.get(pk=request.data.get("domain"))
            subtopics_data = request.data.get("subtopics")

            molecule = Molecule.objects.create(
                title=title, subject=subject, mega_domain=megadomain, domain=domain
            )

            subtopic_ids = []
            for subtopic_data in subtopics_data:
                subtopic_ids.append(subtopic_data.get("id"))

            subtopics = SubTopic.objects.filter(pk__in=subtopic_ids)

            topic_ids = []
            for subtopic in subtopics:
                MoleculeTopicSubtopic.objects.create(
                    molecule=molecule, topic=subtopic.topic, subtopic=subtopic
                )

            return Response(
                {
                    "success": True,
                    "status": "success",
                    "message": "Molecule saved successfully.",
                    "results": [MoleculeSerializers(molecule).data],
                }
            )
        except ValidationError as ve:
            return Response(
                {"success": False, "error": str(ve)},
                status=status.HTTP_400_BAD_REQUEST,
            )

        except Exception as e:
            print("Exception ====> ", e)
            return Response(
                {"success": False, "error": "Something went wrong"},
                status=status.HTTP_400_BAD_REQUEST,
            )

    def update(self, request, pk):

        try:
            existing_molecule = Molecule.objects.get(pk=pk)

            is_active = request.data.get("is_active")
            if is_active is not None:
                if is_active == True:
                    existing_molecule.is_active = False
                else:
                    existing_molecule.is_active = True

            title = request.data.get("title")
            if title is not None and existing_molecule.title != title:
                existing_molecule.title = title

            subject = request.data.get("subject")
            if subject and subject != existing_molecule.subject:
                change_subject = Subject.objects.get(pk=subject)
                existing_molecule.subject = change_subject

            mega_domain = request.data.get("megadomain")
            if mega_domain and mega_domain != existing_molecule.mega_domain:
                change_mega_domain = MegaDomain.objects.get(pk=mega_domain)
                existing_molecule.mega_domain = change_mega_domain

            domain = request.data.get("domain")
            if domain and domain != existing_molecule.domain:
                change_domain = Domain.objects.get(pk=domain)
                existing_molecule.domain = change_domain

            existing_molecule.save()

            sub_topics = request.data.get("subtopics")
            print(f"sub_topics: {sub_topics}")
            if sub_topics is not None:

                for sub_topic_data in sub_topics:
                    subtopic_id = sub_topic_data.get("id")

                    if subtopic_id is not None:
                        try:
                            subtopic_instance = SubTopic.objects.get(pk=subtopic_id)
                            topic_instance = subtopic_instance.topic
                            molecule_topic_subtopic = MoleculeTopicSubtopic.objects.get(
                                molecule=existing_molecule,
                                subtopic__id=subtopic_id,
                                topic=topic_instance,
                            )
                        except MoleculeTopicSubtopic.DoesNotExist:
                            molecule_topic_subtopic = MoleculeTopicSubtopic(
                                molecule=existing_molecule,
                                subtopic=subtopic_instance,
                                topic=subtopic_instance.topic,
                            )
                            molecule_topic_subtopic.save()

            serializer = MoleculeSerializers(existing_molecule)

            return Response(
                {
                    "success": True,
                    "status": "success",
                    "message": "Molecule updated successfully",
                    "results": [serializer.data],
                }
            )

        except Exception as e:
            print("Exception ====> ", e)
            return Response(
                {"success": False, "error": "Something went wrong"},
                status=status.HTTP_400_BAD_REQUEST,
            )

    def delete_subtopic_molecules(self, request, molecule_id, subtopic_id):
        MoleculeTopicSubtopic.objects.filter(
            molecule_id=molecule_id, subtopic_id=subtopic_id
        ).delete()
        return Response(
            {
                "success": True,
                "status": "success",
                "message": "Molecules deleted Successfully",
            }
        )


class MotherSessionMoleculeSerializer(BaseSerializer):
    molecule = MoleculeSerializer()

    class Meta:
        model = MotherSessionMolecule
        fields = "__all__"


class MotherSessionMoleculeViewSet(BaseViewset):
    permission_classes = (
        ~IsGuest,
        ~IsStudent,
        ~IsParent,
        ~IsCounselor,
    )

    def create(self, request):
        session_plan_name = request.data.get("session_plan_name")
        description = request.data.get("description")
        # sequence = request.data.get("sequence")
        subject_id = request.data.get("subject")
        mega_domain_id = request.data.get("mega_domain")
        molecule_ids = request.data.get("molecule_ids", [])

        subject = Subject.objects.get(pk=subject_id)
        mega_domain = MegaDomain.objects.get(pk=mega_domain_id)

        session_plan = SessionPlan.objects.create(
            name=session_plan_name,
            description=description,
            is_active=True,
            # sequence = sequence,
            subject=subject,
            mega_domain=mega_domain,
        )

        session_plan = SessionPlan.objects.get(pk=session_plan.id)
        created_records = []

        for molecule_id in molecule_ids:
            molecule = Molecule.objects.get(pk=molecule_id)

            mother_session_molecule = MotherSessionMolecule.objects.create(
                molecule=molecule, session_plan=session_plan
            )
            serializer = MotherSessionMoleculeSerializer(mother_session_molecule)
            created_records.append(serializer.data)

        return Response(
            {
                "success": True,
                "status": "success",
                "message": "Session created successfully",
                "results": [created_records],
            }
        )

    def list(self, request):
        msls = MotherSessionMolecule.objects.all().order_by("id")
        print("length====> ", len(msls))
        session_dict = defaultdict(dict)

        for msl in msls:
            session_id = msl.session_plan.id
            molecule_data = MoleculeSerializer(msl.molecule).data

            if "molecules" not in session_dict[session_id]:
                session_dict[session_id]["molecules"] = []

            existing_molecules = {
                molecule["id"] for molecule in session_dict[session_id]["molecules"]
            }

            if molecule_data["id"] not in existing_molecules:
                domain = msl.molecule.domain
                domain_data = DomainSerializer(domain).data

                topics = domain.topics.all()

                topic_data_list = []

                for topic in topics:
                    topic_data = TopicSerializer(topic).data

                    subtopics = topic.subtopics.all()
                    subtopic_data_list = SubTopicSerializer(subtopics, many=True).data

                    topic_data["subtopics"] = subtopic_data_list
                    topic_data_list.append(topic_data)

                molecule_data["topics"] = topic_data_list
                session_dict[session_id]["molecules"].append(molecule_data)

            if "id" not in session_dict[session_id]:
                session_dict[session_id].update(
                    SessionPlanSerializer(msl.session_plan).data
                )

        results = list(session_dict.values())

        return Response(
            {
                "success": True,
                "status": "success",
                "message": "",
                "results": results,
            }
        )
