from collections import defaultdict
import re
from django.db.models.functions import Length
from django.db.models.functions import Substr
from django.db.models import IntegerField
from django.forms import CharField
from django.shortcuts import get_object_or_404
from rest_framework import serializers, status
# from datetime import datetime, date
from django.utils import timezone
from rest_framework.response import Response
import requests
# from datetime import datetime, time
import pytz
import base64
import os
import math
from dotenv import load_dotenv
from zuperscore.db import models
from zuperscore.db.models.base import (EnglishCategory, MathCategory, User)
from zuperscore.utils.ip_address import get_client_ip
from itertools import chain
from datetime import datetime, timedelta, timezone, time, date
from django.utils import timezone
from django.http import HttpResponse, HttpResponseNotFound, Http404
from django.db.models import Q
# from django.db.models import Func, F, Value
from django.db.models import Prefetch
from django.utils.dateparse import parse_datetime
from django.utils.timezone import now
from django.db.models import Max
from django.db.models.functions import Cast
from django.db.models.functions import Lower
from concurrent.futures import ThreadPoolExecutor, as_completed
from django.db.models import Count
from django.db.models.functions import Coalesce
from django.contrib.postgres.fields import ArrayField
from django.db.models import Q, Count, Value, Case, When, F,Func
from django.db.models import Value
from django.db.models.functions import Concat



from .people import UserMinimumSerializer, UserTeachersSerializer
from .base import BaseSerializer, BaseViewset
from rest_framework.pagination import PageNumberPagination

from zuperscore.utils.paginator import BasePaginator
from zuperscore.db.models.library import Assignment, CpeaReport, Molecule, MoleculeTopicSubtopic, MotherSessionMolecule, QuestionOption, SubTopic, Subject, MegaDomain, SessionPlan
from zuperscore.db.models.conduct import (
    # StudentCategory,
    AppointmentMolecule,
    AppointmentReport,
    FeedBack,
    FeedbackQuestionRating,
    FeedbackQuestions,
    StudentGroupEvents,
    StudentAssignment,
    StudentAssignmentQuestion,
    StudentCpeaReport,
    StudentGroupEvents,
    # StudentJourney,
    StudentQuestionOption,
    StudentReadingCpeaReport,
    StudentSessionPlan,
    StudentModule,
    StudentDomain,
    StudentTopic,
    StudentSubTopic,
    Appointments,
    Attendee,
    Booking,
    StudentAvailability,   
)

from zuperscore.db.models.base import (
    StudentCategory,
)
   
from zuperscore.api.serializers.people import UserSerializer,UserBaseSerializer

from zuperscore.api.views.subjects import AssignmentSerializer, GetAssignmentSerializer, MoleculeSerializer, MoleculeTopicSubtopicSerializer, MotherSessionMoleculeSerializer, StudentSessionPlanSerializer, SubTopicSerializer, SubjectSerializer

# from zuperscore.api.views.conduct import AppointmentViewSet.get_available_appointment

load_dotenv()




# student category
class StudentCategorySerializer(BaseSerializer):
    class Meta:
        model = StudentCategory
        fields = "__all__"

class StudentAvailabilitySerializer(BaseSerializer):
    class Meta:
        model = StudentAvailability
        fields = "__all__"

class SessionPlanSerializer(serializers.ModelSerializer):
    class Meta:
        model = SessionPlan
        fields = '__all__'
        
class SubTopicPracticeSheetSerializer(BaseSerializer):
    # topic = TopicSerializer()
    class Meta:
        model = SubTopic
        fields = ['practice_sheet']

class StudentAssignmentSerializer(serializers.ModelSerializer):
    subtopic = SubTopicPracticeSheetSerializer()
    subject = serializers.SerializerMethodField()

    class Meta:
        model = StudentAssignment
        fields = '__all__'

    def get_subject(self, obj):
        return obj.subject.name if obj.subject else None


class StudentQuestionOptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = StudentQuestionOption
        fields = ['id','name', 'description', 'is_correct', 'sequence', "student_assignment_question"]

class NewAppointmentSerializer(BaseSerializer):
    subject = SubjectSerializer()
    class Meta:
        model = Appointments
        fields = "__all__"


class StudentAssignmentQuestionSerializer(serializers.ModelSerializer):
    student_assignment = StudentAssignmentSerializer()
    student_question_options = StudentQuestionOptionSerializer(many=True, read_only=True)
    
    class Meta:
        model = StudentAssignmentQuestion
        fields = ['id','student_assignment','assignment_question','name', 'passage', 'description', 'marks', 'sequence', 'type', 'student_question_options']

class StudentHomeAssignmentSerializer(serializers.ModelSerializer):
    subtopic = SubTopicPracticeSheetSerializer()
    student_assignment_questions = StudentAssignmentQuestionSerializer(many=True, read_only=True)

    class Meta:
        model = StudentAssignment
        fields = '__all__'


class QuestionOptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = QuestionOption
        fields = ['id', 'name', 'is_correct'] 


class StudentCategoryViewSet(BaseViewset, BasePaginator):
    serializer = StudentCategorySerializer
    model = StudentCategory

    def list(self, request):
        serializer = StudentCategorySerializer(StudentCategory.objects.all(), many=True)
        return Response(
            {
                "success": True,
                "status": "success",
                "message": "",
                "results": serializer.data,
            }
        )

class AttendeeSerializer(BaseSerializer):
    class Meta:
        model = Attendee
        fields = "__all__"

# class appointments crud
class AppointmentSerializer(BaseSerializer):
    home_assignment_present = serializers.BooleanField(read_only=True, required=False)
    home_assignment_completed = serializers.BooleanField(read_only=True, required=False)
    student = UserMinimumSerializer ()

    class Meta:
        model = Appointments
        fields = "__all__"

class AppointmentMinimumSerializer(BaseSerializer):
    student = UserMinimumSerializer()
    student_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = Appointments
        fields = ["id","zoom_link","host", "start_at", "end_at", "host_name","student","booking","duration","title","is_completed","type","mega_domain","student_count","resource_id","event_duration"]



#------serializer by divyanshu--------------------------------
class TutorialSerializer(BaseSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'first_name', 'last_name', 'role']

class BookingSerializer(BaseSerializer):
    class Meta:
        model = Booking
        fields = '__all__'


class UserSerializer(serializers.ModelSerializer):
    """
    User Serializer View
    """
    english_tutors_detail = UserMinimumSerializer(read_only=True, many=True, source="english_tutors")
    math_tutors_detail = UserMinimumSerializer(read_only=True, many=True, source="math_tutors")
 

    class Meta:
        model = User
        fields = (
            "id",
            "email",
            "first_name",
            "last_name",
            "is_active",
            "role",
            "english_tutors_detail",
            "math_tutors_detail",
            "day_schedule_user_id", 
            "tutor_type",
              
        )
        
class AppointmentFeedbackSerializers(serializers.ModelSerializer):
     class Meta:
        model = FeedBack
        fields = '__all__'

class NewMoleculeSerializers(serializers.ModelSerializer):
    class Meta:
        model = Molecule
        fields = "__all__"

class AppointmentMoleculeSerializers(serializers.ModelSerializer):
    molecule = NewMoleculeSerializers()
    class Meta:
        model = AppointmentMolecule
        fields = '__all__'


class NewAppointmentSerializer(BaseSerializer):
    subject = SubjectSerializer()
    class Meta:
        model = Appointments
        fields = "__all__"

class NewMoleculeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Molecule
        fields = '__all__'


class FeedbackQuestionRatingSerializer(serializers.ModelSerializer):
     class Meta:
        model = FeedbackQuestionRating
        fields = '__all__'


class FeedbackQuestionSerializer(serializers.ModelSerializer):
    class Meta:
        model = FeedbackQuestions
        fields = '__all__'



class CustomPageNumberPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 1000



class AppointmentViewSet(BaseViewset, BasePaginator):
    serializer_class = AppointmentSerializer
    model = Appointments

    def list(self, request):
        serializer = AppointmentSerializer(Appointments.objects.all(), many=True)
        return Response(serializer.data)

    def create(self, request):
        serializer = AppointmentSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response({"success": False, "error": "serialize.errors"})

    def get_appointment(self, request, pk):
        appointment = Appointments.objects.get(pk=pk)
        if not appointment:
            return Response({"success": False, "error": "Appointment doesn't exists"})
        serializer = AppointmentSerializer(appointment).data
        return Response(serializer)

    def partial_update(self, request, pk):
        appointment = Appointments.objects.get(pk=pk)
        serializer = AppointmentSerializer(appointment, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors)

    def get_all_appointments(self, request):
        # if request.user.role != "admin":
        #    return Response({"success": False, "error": "UnAuthorized Access"})
        appointments = Appointments.objects.all().order_by('-created_at')
        serializer = AppointmentSerializer(appointments, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)



    def filter_by_name(self, name, logged_in_user_id):
        names = name.split()
        users = User.objects.filter(Q(id=logged_in_user_id) | Q(is_active=True))  
        

        if len(names) == 1:
            first_name = names[0].lower()
            users = users.filter(Q(first_name__icontains=first_name) | Q(last_name__icontains=first_name))

        elif len(names) >= 2:
            first_name = names[0]
            print("first_name",first_name)
            last_name = ' '.join(names[0:])
            print("last_name",last_name)
            users = users.filter(
                Q(first_name__icontains=first_name) | Q(last_name__icontains=last_name) 
            )
        return users
    
        # ---------------------  Generate zoom access token  ----------------------
    # def create_zoom_session(self, request):
    #     zoom_link = generate_zoom_link(request)
    #     user = User.objects.get(pk=request.data["host"])

    #     if zoom_link["data"]:
    #         calendar_saved = generate_calendar_token(zoom_link["data"]["join_url"], request, user)

    #         if calendar_saved["data"]:
    #             if not user.role == "tutor":
    #                 return Response("user role is not teacher")
    #             request.data["zoom_link"] = zoom_link["data"]["join_url"]
    #             request.data["created_by_ip"] = get_client_ip(request)
    #             request.data["updated_by_ip"] = get_client_ip(request)

    #             user_id = request.user.id
    #             request.data["created_by"] = user_id
    #             request.data["updated_by"] = user_id

    #             serializer = AppointmentSerializer(data=request.data)
    #             if serializer.is_valid():
    #                 serializer.save()
    #                 data = {
    #                     "appointment": serializer.data["id"],
    #                     "attendee": user_id,
    #                     "type": request.user.role,
    #                     "join_time": zoom_link["data"]["start_time"],
    #                 }

    #                 attSerializer = AttendeeSerializer(data=data)
    #                 if attSerializer.is_valid():
    #                     attSerializer.save()
    #                     return Response({"data": serializer.data})
    #                 else:
    #                     return Response({"error": "invalid attSerializer"})
    #             return Response({"error": serializer.errors})

    #         else:
    #             return Response({"error": calendar_saved["error"]})
    #     elif zoom_link["error"]:
    #         return Response({"error": zoom_link["error"]})
    #----------------------------------------------------------------

    def get_student_teachers(self, request, pk):
        try:
            subject = request.query_params.get('subject', None)
            cpea = request.query_params.get('cpea', None)
            slug = request.query_params.get('slug')
            student = User.objects.get(pk=pk)
            serializer = UserSerializer(student)
            english_reading_tutors = student.english_reading_tutors.all()
            english_writing_tutors = student.english_writing_tutors.all()
            math_tutors = student.math_tutors.all()
            
            if subject == 'math':
                tutors = math_tutors
            elif subject == 'english_reading':
                tutors = english_reading_tutors
            elif subject == 'english_writing':
                tutors = english_writing_tutors
            else:
                tutors = english_reading_tutors.union(english_writing_tutors, math_tutors)

            if cpea:
                cpea_enabled_tutors = User.objects.filter(is_cpea_eligible=True)
                tutors = cpea_enabled_tutors.exclude(id__in=tutors.values_list('id', flat=True))
                if subject in ['math', 'english_reading', 'english_writing']:
                    tutors = tutors.filter(tutor_type=subject)

            all_responses = []

            if cpea:
                tutor_name_counter = 1

            tutor_data=[]

            for tutor in tutors:
                tutor_data_response = self.get_dayScheduler_resource_by_id(request, tutor.day_schedule_user_id, slug)
                if tutor_data_response.status_code == 200:
                    tutor_data = tutor_data_response.data.get("users_list", [])
                    
                    if cpea:
                        tutor_data = [event for event in tutor_data if 'CPEA' in event['name']]
            
                        anonymized_tutor = [{
                        "id": tutor.id,
                        "first_name": f"Tutor {tutor_name_counter}",
                        "last_name": "",
                        "email":tutor.email,
                        "tutor_type":tutor.tutor_type,
                        }]
                        tutor_name_counter += 1

                    else:
                        anonymized_tutor = UserMinimumSerializer([tutor], many=True).data
                        
                    all_responses.append({
                        "tutors_detail": anonymized_tutor,
                        "tutor_id": tutor.day_schedule_user_id,
                        "users_list": tutor_data
                    })

            filtered_student = {
                "id": student.id,
                "email": student.email,
                "first_name": student.first_name,
                "last_name": student.last_name,
                "is_active": student.is_active,
                "role": student.role,
                "tutors_detail":all_responses,                
            }

            return Response(
                {
                    "success": True,
                    "status": "success",
                    "message": "",
                    "results": [filtered_student],
                }
            )
        
        except Exception as e:
            print("Exception ====> ", e)
            return Response(
                {"success": False, "error": "Something went wrong"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        
    #Private Method
    def admin_all_tutor_list(self, mega_domain, request, id, slug):
        student = User.objects.get(pk=id)
        serializer = UserSerializer(student)
        
        # Fetch all tutors related to the student
        english_reading_tutors = student.english_reading_tutors.all()
        english_writing_tutors = student.english_writing_tutors.all()
        math_tutors = student.math_tutors.all()
        
        all_student_tutors = list(english_reading_tutors) + list(english_writing_tutors) + list(math_tutors)
        
        subject_tutors = User.objects.filter(tutor_type=mega_domain.lower(), role='tutor', day_schedule_user_id__isnull=False)

        cpea = request.query_params.get('cpea', None)
        if cpea:
            subject_tutors = subject_tutors.filter(is_cpea_eligible=True)
        
        assigned_tutor = None
        for tutor in all_student_tutors:
            if tutor in subject_tutors:
                assigned_tutor = tutor
                break
        
        if assigned_tutor:
            subject_tutors = [assigned_tutor] + [tutor for tutor in subject_tutors if tutor != assigned_tutor]

        all_responses = []
        for tutor in subject_tutors:
            tutor_data_response = self.get_dayScheduler_resource_by_id(request, tutor.day_schedule_user_id, slug)
            # print("")
            if tutor_data_response.status_code == 200:
                tutor_data = tutor_data_response.data.get("users_list", [])

                if cpea:
                    tutor_data = [event for event in tutor_data if 'CPEA' in event['name']]

                all_responses.append({
                    "tutors_detail": UserMinimumSerializer([tutor], many=True).data,
                    "tutor_id": tutor.day_schedule_user_id,
                    "users_list": tutor_data
                })
                                
        return Response(
            {
                "id": student.id,
                "email": student.email,
                "first_name": student.first_name,
                "last_name": student.last_name,
                "is_active": student.is_active,
                "role": student.role,
                "day_Scheduler_reponse": all_responses
            }
        )
    #----------------------------------------------------------------
    # get user information of child and it's tutors by student id used for the admin perspective
    def get_child(self, request, id):
        mega_domain = request.query_params.get('mega_domain', None)
        cpea = request.query_params.get('cpea', None)
        slug = request.query_params.get('slug')

        if request.user.role == "admin":
            return self.admin_all_tutor_list(mega_domain, request, id,slug)
        
        student = User.objects.get(pk=id)
        english_reading_tutors = student.english_reading_tutors.all()
        english_writing_tutors = student.english_writing_tutors.all()
        math_tutors = student.math_tutors.all()

        if mega_domain == 'math':
            tutors = math_tutors
            print("enter in math")
        elif mega_domain == 'english_reading':
            tutors = english_reading_tutors
        elif mega_domain == 'english_writing':
            tutors = english_writing_tutors
        else:
            # tutors = list(chain(english_reading_tutors,english_writing_tutors, math_tutors))
            tutors = english_reading_tutors.union(english_writing_tutors, math_tutors)

        if cpea:
            print("enter in cpea")
            cpea_enabled_tutors = User.objects.filter(is_cpea_eligible=True)
            print("cpea_enabled_tutors===>",cpea_enabled_tutors)
            tutors = cpea_enabled_tutors.exclude(id__in=tutors.values_list('id', flat=True))

            if mega_domain in ['math', 'english_reading', 'english_writing']:
                tutors = tutors.filter(tutor_type=mega_domain)
                
        all_responses = []

        for tutor in tutors:
            tutor_data_response = self.get_dayScheduler_resource_by_id(request, tutor.day_schedule_user_id, slug)
            print('response===>',tutor_data_response)
            if tutor_data_response.status_code == 200:
                tutor_data = tutor_data_response.data.get("users_list", [])
                
                if cpea:
                    print("enter in if cpea")
                    tutor_data = [event for event in tutor_data if 'CPEA' in event['name']]
                
                all_responses.append({
                    "tutors_detail": UserMinimumSerializer([tutor], many=True).data,
                    "tutor_id": tutor.day_schedule_user_id,
                    "users_list": tutor_data
                })
                    # processed_tutors.add(tutor.id)


        return Response (
            {
            "id": student.id,   
            "email": student.email,
            "first_name": student.first_name,
            "last_name": student.last_name,
            "is_active": student.is_active,
            "role": student.role,
            "day_Scheduler_reponse":all_responses,    
            }
        )

    
    #----------------------------------------------------------------
    # day scheduler api to return all users link based on the Day-scheduler id
    def get_dayScheduler_resource_by_id(self, request, tutor_id, slug):
        if not tutor_id:
            return Response({"error": "Tutor DayScheduler ID is not provided or is invalid"}, status=status.HTTP_400_BAD_REQUEST)
        
        get_all_users_url = "https://api.dayschedule.com/v1/resources"
        headers = {"Content-Type": "application/json"}

        params = {
            "user_id": tutor_id,
            "apiKey": "AOthHfwumTELV7qUslLHRNxeOpObRhvp"
        }

        try:
            response = requests.get(get_all_users_url, headers=headers, params=params)
            
            if response.status_code == 200:
                users_list = response.json().get("result", [])
                print("users_list===>", users_list)

                if slug:
                    filtered_events = [event for event in users_list if slug in event['slug']]
                    print("filtered_events====>", filtered_events)
                    users_list = filtered_events

                return Response({"users_list": users_list})

            else:
                return Response({"error": response.status_code}, status=status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            print("Error Occurred:", e)
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

     #----------------------------------------------------------------

    # get available Appointment  created by divyanshu by resource_id
    def get_available_appointments(self, request, pk):
        get_available_appointments_url = f"https://api.dayschedule.com/v1/availability/{pk}/"
        duration = request.query_params.get("duration", "")
        print("duration===>",duration)

        today = datetime.today() - timedelta(days=1)
        end_date = today + timedelta(days=7)

        headers = {
            "Content-Type": "application/json",
        }
        params = {
            "apiKey": "AOthHfwumTELV7qUslLHRNxeOpObRhvp",
            "start": request.query_params.get("start", today.isoformat()),
            "end": request.query_params.get("end", end_date.isoformat()),   
            "time_zone": request.query_params.get("time_zone", "Asia/Calcutta"),  
            "duration": duration, 
        }
       
        try:
            response = requests.get(get_available_appointments_url, headers=headers, params=params)
            print("get_available_appointments_url===>",get_available_appointments_url)
            print("params====>",params)

            if response.status_code == 200:
                availability_data = response.json()

                filtered_slots = []
                for slot in availability_data:
                    slot_date = datetime.strptime(slot["date"], "%Y-%m-%d").date()
                    if today.date() <= slot_date <= end_date.date():
                        filtered_slots.append(slot)
                return Response(filtered_slots)
            else:
                return Response({"error": response.status_code}, status=response.status_code)

        except Exception as e:
            print("Error Occurred:", e)
            return Response({"error": "Internal Server Error"}, status=500)    
            

#---------------------------------------------------------------------------------------
    def slot_booking(self, request, type=None):
        try:
            slot_booking_url = "https://api.dayschedule.com/v1/bookings"
            headers = {"Content-Type": "application/json"}
            params = {"apiKey": "AOthHfwumTELV7qUslLHRNxeOpObRhvp"}

            appointment_type = type

            if appointment_type not in ['coreprep', 'cpea', 'group_class']:
                return Response({'error': 'Invalid appointment type provided.'}, status=status.HTTP_400_BAD_REQUEST)

            invitee_name = request.data.get("invitee_name", "")
            invitee_email = request.data.get("invitee_email", "")
            start_at = request.data.get("start_at", "")
            resource_id = request.data.get("resource_id", "")
            invitee_id = request.data.get("invitee_id", "")
            ds_host_id = request.data.get("host_id", "")
            host = request.data.get("host", "")
            mega_domain = request.data.get("subject", "")

            if not ds_host_id:
                return Response({"error": "Day-Scheduler id not found"}, status=status.HTTP_400_BAD_REQUEST)

            try:
                host = User.objects.get(pk=host)
                host_name = f"{host.first_name} {host.last_name}"
            except User.DoesNotExist:
                return Response({"error": "Host user not found"}, status=status.HTTP_400_BAD_REQUEST)

            if request.user.role == "admin":
                student_id = request.data.get("student", "")
                student = User.objects.get(pk=student_id)
            else:
                student = request.user

            # if appointment_type != 'group_class':
                MAX_DURATION_MINUTES = 60

                new_start_datetime = parse_datetime(request.data.get("start_at", ""))

                estimated_end_time = new_start_datetime + timedelta(minutes=MAX_DURATION_MINUTES)

                # Retrieve all appointments for the student on the same day.
                appointment_date = new_start_datetime.date()
                same_day_appointments = Appointments.objects.filter(student=student, start_at__date=appointment_date)

                # Check for time overlap with a conservative duration estimate.
                for appointment in same_day_appointments:
                    appointment_start = appointment.start_at
                    appointment_end = appointment_start + timedelta(minutes=int(appointment.duration) if appointment.duration else MAX_DURATION_MINUTES)

                    if (new_start_datetime < appointment_end and estimated_end_time > appointment_start):
                        return Response({"error": "The new appointment overlaps with an existing one."}, status=status.HTTP_400_BAD_REQUEST)
                    
                if appointment_type == 'group_class':
                    existing_group_classes = Appointments.objects.filter(student=student, type='group_class',start_at__date=appointment_date,mega_domain=mega_domain,)
                    if existing_group_classes.exists():
                        return Response({"error": "You can only book one group class of the same mega domain at a time."}, status=status.HTTP_400_BAD_REQUEST)

            new_booking = Appointments.objects.create(
                invitee_name=invitee_name,
                invitee_email=invitee_email,
                start_at=start_at,
                resource_id=resource_id,
                invitee_id=invitee_id,
                student=student,
                ds_host_id=ds_host_id,
                host=host,
                host_name=host_name,
                mega_domain=mega_domain,
                type=appointment_type,
                # subject = subject,
            )
            booking_data = AppointmentSerializer(new_booking).data
            booking_id = booking_data.get("id")

            payload = {
                "resource": {
                    "resource_id": resource_id
                },
                "host": {
                    "user_id": ds_host_id
                },
                "start_at": start_at,
                "location": {
                    "name": "zoom",
                    "type": "zoom"
                },
                "attendees": [
                    {}
                ],
                "invitees": [
                    {
                        "invitee_id": invitee_id,
                        "name": invitee_name,
                        "email": invitee_email,
                        "questions": [
                            {
                                "type": "string",
                                "name": "string",
                                "label": "string",
                                "options": [
                                    {
                                        "key": "string",
                                        "label": "string"
                                    }
                                ]
                            }
                        ],
                        "payment": {
                            "amount": 0,
                            "name": "string",
                            "currency": "string",
                            "gateway": "string"
                        }
                    }
                ]
            }

            response = requests.post(slot_booking_url, headers=headers, params=params, json=payload)
            if response.status_code == 200:
                duration = response.json().get("duration", {}).get('value', 0)
                ds_booking_id = response.json().get("booking_id")
                existing_booking = Appointments.objects.get(pk=booking_id)
                existing_booking.booking = ds_booking_id
                existing_booking.duration = duration
                existing_booking.save()
                return Response({"success": True, "message": "Booking successful"})
            else:
                error_message = response.json().get("message", "Booking failed")
                return Response({"error": response.status_code, "message": error_message}, status=response.status_code)

        except Exception as e:
            print("Error Occurred:", e)
            return Response({"error": "Internal Server Error"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        

    def get_coming_classes(self, request, invitee_id):
       
        try:
            bookings = Appointments.objects.filter(invitee_id=invitee_id).exclude(status__in=['CANCELLED', 'RESCHEDULED']).select_related('host').order_by("start_at")
            serializer = AppointmentSerializer(bookings, many=True)
            data = serializer.data
           
            booking_ids = [item.get("booking") for item in data]
            day_scheduler_responses = []
            expired_appointments = []

            for booking_id in booking_ids:
                day_scheduler_response = self.get_dayScheduler_booking(request, booking_id)
                day_scheduler_responses.append(day_scheduler_response.data)

            for appointment_data, day_scheduler_response in zip(data, day_scheduler_responses):
                zoom_link = day_scheduler_response.get("users_list", {}).get("location", {}).get("join_url")
                subject = day_scheduler_response.get("users_list", {}).get("subject", {})

                appointment_id = appointment_data.get("id")

                appointment = Appointments.objects.filter(id=appointment_id).exclude(status__in=['CANCELLED', 'RESCHEDULED']).get()
                if zoom_link:
                    appointment.zoom_link = zoom_link
                    appointment.title = subject
                    appointment.save()
                
                duration_minutes = int(appointment.duration)  
                class_end_time = appointment.start_at + timedelta(minutes=duration_minutes)
                current_time = datetime.now(timezone.utc)

                if current_time > class_end_time:
                    
                    appointment_report = AppointmentReport.objects.filter(appointment_id=appointment_id).first()
                    if appointment_report:
                        is_student_joined = appointment_report.is_student_joined
                        is_tutor_joined = appointment_report.is_tutor_joined

                        if not is_student_joined and not is_tutor_joined:
                            status = 'unattended'
                            reason = 'BOTH_TUTOR_AND_STUDENT_NOT_JOIN'
                        elif is_student_joined and not is_tutor_joined:
                            status = None
                            reason = 'TUTOR_NOT_JOINED'
                        elif not is_student_joined and is_tutor_joined:
                            status = None
                            reason = 'STUDENT_NOT_JOINED'
                        else:
                            status = 'attended'
                            reason = 'BOTH_TUTOR_AND_STUDENT_JOIN'

                        appointment_report.status = status
                        appointment_report.reason = reason
                        appointment_report.save()
                        expired_appointments.append(appointment_data)

                taught_molecules = AppointmentMolecule.objects.filter(appointment__id=appointment_id, is_completed=True).values_list('molecule_id', flat=True)
                related_subtopics = MoleculeTopicSubtopic.objects.filter(molecule_id__in=taught_molecules).values_list('subtopic_id', flat=True)
                
                
                completed_home_assignments = StudentAssignment.objects.filter(
                    subtopic_id__in=related_subtopics,
                    student_id=invitee_id,
                    is_completed=True,
                    type="HOME",
                )
                
                related_class_assignments = StudentAssignment.objects.filter(
                    subtopic_id__in=related_subtopics,
                    student_id=appointment.student_id,
                    type="CLASS",
                )

                class_assignment_completed = related_class_assignments.exists() and related_class_assignments.filter(is_completed=False).count() == 0

                related_home_assignments = StudentAssignment.objects.filter(
                    subtopic_id__in=related_subtopics,
                    student_id=invitee_id,
                    type="HOME",
                )
                has_molecules = AppointmentMolecule.objects.filter(appointment__id=appointment.id).exists()
                home_assignment_present = related_home_assignments.exists() 
                home_assignment_count = len(related_home_assignments)
                are_all_home_assignments_completed = len(completed_home_assignments)  == home_assignment_count
                                
                host_subject_name = appointment.host.tutor_type
                student_feedback_exists = FeedBack.objects.filter(appointment_id=appointment_id, student_id=appointment.student_id, commenter='user').exists()
                tutor_feedback_exists = FeedBack.objects.filter(appointment_id=appointment_id, tutor_id=appointment.host_id,commenter='tutor').exists()

                appointment_data['class_assignment_completed'] = class_assignment_completed
                appointment_data['home_assignment_completed'] = are_all_home_assignments_completed
                appointment_data['subject_name'] = host_subject_name
                appointment_data['is_student_filled_feedback'] = student_feedback_exists
                appointment_data['is_tutor_filled_feedback'] = tutor_feedback_exists
                appointment_data['home_assignment_present'] = home_assignment_present
                appointment_data['has_molecules'] = has_molecules

            for expired_appointment in expired_appointments:
                data.remove(expired_appointment)

            return Response({
                "bookings": data,
            })
        except Exception as e:
            return Response({"error": str(e)}, status=500)
    
    def get_dayScheduler_booking(self, request, booking_id):
        print("enter")
        get_all_users_url = f"https://api.dayschedule.com/v1/bookings/{booking_id}"

        headers = {
            "Content-Type": "application/json",   
        }

        params ={
            "apiKey": "AOthHfwumTELV7qUslLHRNxeOpObRhvp"
        }

        try: 
            response = requests.get(get_all_users_url, headers=headers, params=params)
            if response.status_code == 200:
                users_list = response.json()
                return Response({"users_list": users_list})
                
            else :
                return Response({"error": "Failed to retrieve booking info, status code: {}".format(response.status_code)}, status=response.status_code)

        except Exception as e:
            print("Error Occured:", e)
            return Response({"error": "An error occurred while retrieving booking information."}, status=500)
        

        #Get api for admin to see all users by create suresh
    def get_all_users(self, request):
        get_appointments_url = f"https://api.dayschedule.com/v1/bookings"

        headers = {
            "Content-Type":"application/json",
        }

        params = {
            "apiKey": "AOthHfwumTELV7qUslLHRNxeOpObRhvp"
        }

        try:
            response = requests.get(get_appointments_url, headers=headers, params=params)
            
            if response.status_code == 200:
                page_list = response.json().get("result",[])
                print(f"Page List: {page_list}")
                return Response({"page_list": page_list})
            
            else :
                return Response({"error": response.status_code}, status=response.status_code)

        except Exception as e:
            print("Error Occured:", e)     

    def get_appointments(self, request,tutor_id):
        get_appointments_url = f"https://api.dayschedule.com/v1/pages/"

        headers = {
            "Content-Type":"application/json",
        }

        params = {
            "id":tutor_id,
            "apiKey": "AOthHfwumTELV7qUslLHRNxeOpObRhvp"
        }

        try:
            response = requests.get(get_appointments_url, headers=headers, params=params)
            
            if response.status_code == 200:
                page_list = response.json().get("result",[])
                print(f"Page List: {page_list}")
                return Response({"page_list": page_list})
            
            else :
                return Response({"error": response.status_code}, status=response.status_code)

        except Exception as e:
            print("Error Occured:", e)
            
class StudentRelatedTeacherViewSet(BaseViewset, BasePaginator):

    def students_related_teacher(self, request):
        logged_in_user_id = request.user.id
        name = request.GET.get("name", '')

        try:
            users = User.objects.get(id=logged_in_user_id, is_active=True)
            users = users.english_reading_tutors.all().distinct() | \
                    users.math_tutors.all().distinct() | \
                    users.english_writing_tutors.all().distinct()
            
            users=users.order_by('-created_at')

            if name and not name.strip():
                return Response({"results":[]})

            if name:

                users = users.filter(Q(first_name__icontains=name) | Q(last_name__icontains=name) | Q(first_name__icontains=name.split()[0], last_name__icontains=name.split()[-1]))

            paginator = CustomPageNumberPagination()
            paginated_students = paginator.paginate_queryset(users, request)

            serialized_students = UserMinimumSerializer(paginated_students, many=True).data

            results = []
            for student_data in serialized_students:
                student_sessions = StudentSessionPlan.objects.filter(student_id=student_data["id"])
                serialized_student_sessions = StudentSessionPlanSerializer(student_sessions, many=True).data
                student_availability = StudentAvailability.objects.filter(student_id=student_data["id"]).exclude(target_test_date_1__isnull = True).first()
                serialized_availability = StudentAvailabilitySerializer(student_availability).data if student_availability else {}

                teacher_student_session_dates = {
                    "student_details": student_data,
                    "student_sessions": serialized_student_sessions,
                    "availability_details": serialized_availability,
                }
                results.append(teacher_student_session_dates)
            return paginator.get_paginated_response(results)

        except Exception as e:
            print(f"Error in students_related_teacher: {str(e)}")
            return Response({"error": "An error occurred"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
class AppointmentAgendaViewSet(BaseViewset, BasePaginator):      

    def get_appointment_molecule(self, request, student_id, tutor_id):
            try:
                total_number_of_classes= 0
                per_day_molecule = 0
                query_set_data = None

                # tutor_subject_type = request.user.tutor_type
                tutor_subject_type = User.objects.get(id=tutor_id).tutor_type 
                print("tutor_subject_type===>",tutor_subject_type)
                appointment_id = request.query_params.get('Appointment_Id', None)
                print("Appointment id:&&&&&&",appointment_id)

                if appointment_id:
                    query_set_data = AppointmentMolecule.objects.filter(
                        appointment_id=appointment_id,
                        is_completed=True
                    ).select_related('molecule')  

                    molecules_list = [molecule.molecule for molecule in query_set_data]
                    print("molecules_list===>",molecules_list)

                    sorted_molecules = sorted(molecules_list, key=lambda x: int(re.search(r'\d+', x.title).group()) if re.search(r'\d+', x.title) else float('inf'))

                    serializer = NewMoleculeSerializer(sorted_molecules, many=True)

                    return Response({"results": serializer.data})
                
                else:
                
                    student_session_plans = StudentSessionPlan.objects.filter(student=student_id, is_active=True)
                    print("student_session_plans===>",student_session_plans)
                    
                    for session_plan in student_session_plans:
                        subject_name = session_plan.subject.name.lower()
                        print("subject_name===>",subject_name)

                        mega_domain_name = session_plan.mega_domain.name.lower() if session_plan.mega_domain else ""
                        print("mega_domain_name===>",mega_domain_name)

                        if subject_name == "english":
                            if not (("reading" in mega_domain_name and tutor_subject_type == "english_reading") or
                                    ("writing" in mega_domain_name and tutor_subject_type == "english_writing")):
                                continue  

                        elif subject_name == "math" and tutor_subject_type != "math":
                            continue 
            
                        # if subject_name not in ["english", "math"] or subject_name != tutor_subject_type:
                        #     continue

                        total_number_of_molecule = MotherSessionMolecule.objects.filter(session_plan=session_plan.session_plan.id).count() 
                        # print("total_number_of_molecule===>",total_number_of_molecule)

                        category = session_plan.category.upper()
                        
                        # if tutor_subject_type == "english" and subject_name == "english":

                        if subject_name == "english":
                            print("===english===")
                            if category == "R":
                                
                                total_number_of_classes = total_number_of_molecule/2 
                                per_day_molecule = total_number_of_molecule/total_number_of_classes
                            elif category == "S":
                            
                                total_number_of_classes = total_number_of_molecule/3 
                                per_day_molecule = total_number_of_molecule/total_number_of_classes
                            elif category == "T":
                            
                                total_number_of_classes = total_number_of_molecule/4 
                                per_day_molecule = total_number_of_molecule/total_number_of_classes

                        elif subject_name == "math":
                            print("===math===")
                            if category == "R":
                                
                                total_number_of_classes = total_number_of_molecule/2 
                                per_day_molecule = total_number_of_molecule/total_number_of_classes
                            elif category == "S":
                                
                                total_number_of_classes = total_number_of_molecule/3 
                                per_day_molecule = total_number_of_molecule/total_number_of_classes
                            elif category == "T":
                            
                                # number_of_molecule /= 4
                                total_number_of_classes = total_number_of_molecule/4 # 9
                                per_day_molecule = total_number_of_molecule/total_number_of_classes

                        # Filtering out molecules already present in AppointmentMolecule
                        existing_molecule_ids = AppointmentMolecule.objects.filter(appointment__student=student_id, is_completed=True).values_list('molecule_id', flat=True)
                    
                        query_set_data = MotherSessionMolecule.objects.filter(session_plan=session_plan.session_plan.id).exclude(molecule_id__in=existing_molecule_ids)

                        print("query_set_data==>",query_set_data)

                        molecules_list = list(query_set_data)

                        sorted_molecules = sorted(molecules_list, key=lambda x: int(re.search(r'\d+', x.molecule.title).group()) if re.search(r'\d+', x.molecule.title) else float('inf'))

                        final_molecules = sorted_molecules[:math.ceil(per_day_molecule)]

                        serializer = MotherSessionMoleculeSerializer(final_molecules, many=True)

                        
                    
                        return Response({"results": serializer.data})

                    return Response({"results": query_set_data})

            except Exception as stacktrace:
                print("Error Occurred:", stacktrace)
                return Response({"error": "An error occurred while processing the request"}, status=500)
            
    
    def createAppointmentMolecules(self, request):
        try:
            molecules_data = request.data.get('molecules',[])
            appointment_id = request.data.get('appointment_id')

            appointment= get_object_or_404(Appointments,pk=appointment_id)

            for molecule_id in molecules_data:
                if not AppointmentMolecule.objects.filter(appointment=appointment, molecule_id=molecule_id).exists():
                    AppointmentMolecule.objects.get_or_create(
                        appointment=appointment,
                        molecule_id=molecule_id,
                        is_completed=False
                    )
            return Response({'message': 'Molecules Saved..!!'}, status=status.HTTP_200_OK)
        except Exception as e:
            print("Error Occurred:", e)
            return Response({"error": "An error occurred while processing the request"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


    def update_appointment_molecules_and_feedback(self, request):
        try:
            molecules_data = request.data.get('molecules', [])
            appointment_id = request.data.get('appointment_id')
            feedback_data = request.data.get('feedback', {})  
            feedback_questions = request.data.get('feedback_questions', [])

            appointment = get_object_or_404(Appointments, pk=appointment_id)

            user_type = request.user.role
            commenter_type = 'tutor' if user_type == 'tutor' else 'user'
           
            if user_type == 'tutor':
                for molecule_id in molecules_data:
                    AppointmentMolecule.objects.update_or_create(
                        appointment=appointment,
                        molecule_id=molecule_id,
                        defaults={'is_completed': True}
                    )
            elif user_type == 'user':

                molecules_data_str = list(map(str, molecules_data))

                appointment_molecules = AppointmentMolecule.objects.filter(appointment=appointment)

                for molecule in appointment_molecules:

                    if str(molecule.molecule_id) in molecules_data_str:
                            molecule.is_completed = True
                    else:
                            molecule.is_completed = False
                    molecule.save()

            feedback = FeedBack.objects.create(
                comment=feedback_data.get('comment'),
                student_id=feedback_data.get('student_id'),
                tutor_id=feedback_data.get('tutor_id'),
                appointment=appointment,
                commenter=commenter_type,
            )
            
            for feedback_question in feedback_questions:
                question_id = feedback_question.get('question_id')
                rating = feedback_question.get('rating')
                question = get_object_or_404(FeedbackQuestions, pk=question_id)
                FeedbackQuestionRating.objects.create(
                    feedback=feedback,
                    question=question,
                    rating=rating
                )
            
            appointment.is_completed = True
            if user_type == 'tutor':
                print("enter in tutor side")
                print("saving in tutor side")
                western_time = pytz.timezone('Asia/Kolkata')
                appointment.end_at = western_time.localize(datetime.now())


            appointment.save()

            return Response({'message': 'Feedback and molecules updated successfully.'}, status=status.HTTP_200_OK)
        
        except Exception as e:
            return Response({"error": f"An error occurred: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

                 

    def get_other_covered_agenda(self, request, student_id):
        try:
            tutor_subject_type = request.user.tutor_type
            print("tutor_subject_type-->",tutor_subject_type)

            excluded_molecule_ids = AppointmentMolecule.objects.filter(
                appointment__student=student_id,
                # is_completed=False,
            ).values_list('molecule_id', flat=True)

            print('excluded_molecule_ids-->',excluded_molecule_ids)

            student_session_plans = StudentSessionPlan.objects.filter(student=student_id)
            # print("student_session_plans @@@@@@@====>>>",student_session_plans)

            print('student_session_plans===>',student_session_plans)

            eligible_molecules = []

            for session_plan in student_session_plans:
                subject_name = session_plan.subject.name.lower() if session_plan.subject else ""
                mega_domain_name = session_plan.mega_domain.name.lower() if session_plan.mega_domain else ""
                if subject_name == "english":
                    print("english-->")

                    if (("reading" in mega_domain_name and tutor_subject_type == "english_reading") or
                        ("writing" in mega_domain_name and tutor_subject_type == "english_writing")):

                        queryset = MotherSessionMolecule.objects.filter(
                            session_plan=session_plan.session_plan.id
                        ).exclude(molecule_id__in=excluded_molecule_ids)

                        print("queryset english==>", queryset)
                        
                        molecules_list = list(queryset)
                        
                        sorted_molecules = sorted(
                            molecules_list, 
                            key=lambda x: (x.molecule.title[0], int(re.search(r'\d+', x.molecule.title).group()) if re.search(r'\d+', x.molecule.title) else 0)
                        )
                        
                        molecules = molecules_list[:2]
                        
                        eligible_molecules.extend(molecules)

                elif subject_name == "math" and tutor_subject_type == "math":
                    print('math==>')

                    queryset = MotherSessionMolecule.objects.filter(
                        session_plan=session_plan.session_plan.id
                    ).exclude(molecule_id__in=excluded_molecule_ids)

                    print("queryset math--->",queryset)

                    molecules_list = list(queryset)
                    
                    sorted_molecules = sorted(molecules_list, key=lambda x: (x.molecule.title[0], int(re.search(r'\d+', x.molecule.title).group()) if re.search(r'\d+', x.molecule.title) else 0))
                    
                    molecules = sorted_molecules[:2]
                    
                    eligible_molecules.extend(molecules)

            serializer = MotherSessionMoleculeSerializer(eligible_molecules, many=True)
            return Response({"results": serializer.data})

        except Exception as e:
            print("Error Occurred:", e)
            return Response({"error": "An error occurred while processing the request"}, status=500)
        
class LastClassAgendaViewSet(BaseViewset, BasePaginator):  
    
        
    def get_last_classes_agenda(self, request):
        mega_domain = request.query_params.get('megadomain')
        student_id = request.query_params.get('student_id')
        
        last_completed_appointment = Appointments.objects.filter(
            student_id=student_id, 
            mega_domain=mega_domain.lower(), 
            is_completed=True
        ).order_by('-start_at').first()
        
        if last_completed_appointment:
            last_classes_agenda = AppointmentMolecule.objects.filter(
                appointment=last_completed_appointment, 
                is_completed=True
            )
            molecule=last_classes_agenda.values_list('molecule', flat=True)

            molecule_topic_subtopic=MoleculeTopicSubtopic.objects.filter(molecule_id__in=molecule)

            home_assignment_status =StudentAssignment.objects.filter(subtopic__in=molecule_topic_subtopic.values_list('subtopic', flat=True),student_id=student_id,type="HOME",is_completed=True).exists()

            appointment_serializer = NewAppointmentSerializer(last_completed_appointment)
            last_class_agenda_serializers = AppointmentMoleculeSerializers(last_classes_agenda, many=True)
            
          
            appointment_data = appointment_serializer.data
            appointment_data['molecules'] = last_class_agenda_serializers.data
            appointment_data['home_assignments'] = home_assignment_status
            
            return Response({
                    "sucess": True, 
                    "status": "success",
                    "message":"Last Class Detail",
                    "results": [appointment_data],
                })
        else:
            return Response({"results": []})

class TeacherAppointmentViewSet(BaseViewset, BasePaginator):
    def get_teachers_appointments(self, request):
        host_id = request.user.id
        now = timezone.now()
        sort_order= request.query_params.get('sort_order', 'desc')
        appointment_status= request.query_params.get('status')
        appointments = Appointments.objects.filter(host_id=host_id)

        search = request.query_params.get('search', None)
        if search and not search.strip():
                return Response({"results":[]})

        if search:
            appointments = appointments.filter(Q(student__first_name__icontains=search) | Q(student__last_name__icontains=search) | Q(student__first_name__icontains=search.split()[0], student__last_name__icontains=search.split()[-1])|Q(title=search))

        if appointment_status == 'completed':
            appointments = appointments.filter(Q(is_completed=True) | (Q(start_at__lt=now - timedelta(hours=1, minutes=30)) & Q(is_completed=False))).exclude(status__in=['CANCELLED', 'RESCHEDULED']).order_by("-start_at")

        elif appointment_status == 'upcoming':
            # upcoming_margin = now + timedelta(hours=1, minutes=30)
            # appointments = appointments.filter(Q(is_completed=False) & Q(start_at__gt=now) & Q(start_at__gte=upcoming_margin))
            appointments = appointments.filter(is_completed=False).exclude(status__in=['CANCELLED', 'RESCHEDULED'])

    
        if sort_order == 'asc':
            appointments = appointments.filter(host_id=host_id).order_by('start_at')

        else :
            appointments = appointments.filter(host_id=host_id).order_by('-start_at')

        appointments = appointments.annotate(student_count=Count('student'))
        appointments = list(appointments)
        serializer = AppointmentMinimumSerializer(appointments, many=True).data
            
        modified_appointments = []
        appointment_resource_grouping_map = {}
        groupedAppointId = set()
        response_data=[]

        for app in serializer:
            if app['type'] == 'group_class':
                if app['resource_id'] in appointment_resource_grouping_map:
                    appointment_resource_grouping_map[app['resource_id']].append(app['student'])
                    
                else:
                    appointment_resource_grouping_map[app['resource_id']] = [app['student']]
                    groupedAppointId.add(app['id'])

        paginator = CustomPageNumberPagination()
        paginated_appointments = paginator.paginate_queryset(appointments, request)
        
        
        for appointment in appointments:
            appointment_filter = {'appointment_id': appointment.id}

            has_molecules = AppointmentMolecule.objects.filter(
                appointment__id=appointment.id,
                **appointment_filter
            ).exists()
            
            completed_assignments = AppointmentMolecule.objects.filter(
                appointment__id=appointment.id,
                **appointment_filter,
            ).values_list('molecule_id', flat=True)
            
            related_subtopics = MoleculeTopicSubtopic.objects.filter(
                molecule_id__in=completed_assignments
            ).values_list('subtopic_id', flat=True)
            
            related_assignments = StudentAssignment.objects.filter(
                subtopic_id__in=related_subtopics,
                student_id=appointment.student_id,
                type="CLASS",
            )
            total_assignments_count = related_assignments.count()

            if total_assignments_count == 0:
                class_assignment_completed = False
            else:
                completed_assignments_count = related_assignments.filter(is_completed=True).count()
                class_assignment_completed = total_assignments_count == completed_assignments_count


            appointment_data = AppointmentMinimumSerializer(appointment).data
            appointment_data['class_assignment_complete'] = class_assignment_completed
            appointment_data['has_molecules'] = has_molecules 

            if appointment_data['type'] == 'group_class':
                appointment_data['student_count'] = len(appointment_resource_grouping_map.get(appointment_data['resource_id'], []))


            appointment_obj=AppointmentReport.objects.filter(appointment=appointment.id).first()
            appointment_data['is_tutor_joined']=appointment_obj.is_tutor_joined if appointment_obj else False

            modified_appointments.append(appointment_data)
         
        for app in modified_appointments:
            if app['type'] == 'group_class' and app['id'] in groupedAppointId:
                app['student'] = appointment_resource_grouping_map[app['resource_id']]
                response_data.append(app)
            elif app['type'] == 'group_class' :#add
                print("group class", app['id'])#add
            if app['type'] != 'group_class': 
                response_data.append(app)
        print("response_data====>",len(response_data))
        paginator = CustomPageNumberPagination()
        paginated_appointments = paginator.paginate_queryset(response_data, request)#add
        print("response_data====>",len(paginated_appointments))
        return paginator.get_paginated_response(paginated_appointments)
    


    def alphanumeric_sort(s):
            parts = []
            current_part = ''

            for char in s:
                if char.isdigit():
                    current_part += char
                else:
                    if current_part:
                        parts.append(int(current_part))
                        current_part = ''
                    parts.append(char)
            
            if current_part:
                parts.append(int(current_part))

            return parts

class AppointmentAssignemntViewset(BaseViewset, BasePaginator):
    
    def get_student_class_assignment(self, request, student_id, appointment_id=None):  
        
        try:
            appointment_filter = {}
            if appointment_id:
                appointment_filter['appointment_id'] = appointment_id

            completed_molecules = AppointmentMolecule.objects.filter(
            appointment__student_id=student_id,
            **appointment_filter,
            ).values_list('molecule_id', flat=True)

            related_subtopics = MoleculeTopicSubtopic.objects.filter(
            molecule_id__in=completed_molecules
            ).values_list('subtopic_id', flat=True)

            related_assignments = StudentAssignment.objects.filter(
            subtopic_id__in=related_subtopics,
            student_id=student_id,
            type="CLASS",
            )

            related_assignments = related_assignments.annotate(
                        assignment_length=Length('name')
                    ).order_by('assignment_length', 'name')
        
            total_assignments_count = related_assignments.count()
            
            if total_assignments_count == 0:
                class_assignment_completed = False
            else:
                completed_assignments_count = related_assignments.filter(is_completed=True).count()
                class_assignment_completed = total_assignments_count == completed_assignments_count
            serializer = StudentAssignmentSerializer(related_assignments, many=True)

            response_data = {
            'assignments': serializer.data,
            'class_assignment_completed': class_assignment_completed
            }

            return Response(response_data)
        
        except Exception as e:
            print("Exception ====> ", e)
            return Response(
                {"success": False, "error": "Something went wrong"},
                status=status.HTTP_400_BAD_REQUEST,
            )


    def get_student_home_assignment(self, request, student_id, appointment_id=None):
        try:
            appointment_filter = {}

            if appointment_id:
                appointment_filter['appointment_id'] = appointment_id

            completed_molecules = AppointmentMolecule.objects.filter(
                appointment__student_id=student_id,
                is_completed=True,
                **appointment_filter,
            ).values_list('molecule_id', flat=True)

            related_subtopics = MoleculeTopicSubtopic.objects.filter(
                molecule_id__in=completed_molecules
            ).values_list('subtopic_id', flat=True)


            related_assignments = StudentAssignment.objects.filter(
                subtopic_id__in=related_subtopics,
                student_id=student_id,
                type="HOME",
                is_active = True,
            ).select_related('subject').prefetch_related(
                'student_assignment_questions__student_question_options'
            )
            
            related_assignments = related_assignments.annotate(
                        assignment_length=Length('name')
                    ).order_by('assignment_length', 'name')  
            

            total_assignments_count = related_assignments.count()
            
            if total_assignments_count == 0:
                home_assignment_completed = False
            else:
                completed_assignments_count = related_assignments.filter(is_completed=True).count()
                home_assignment_completed = total_assignments_count == completed_assignments_count

            serializer = StudentHomeAssignmentSerializer(related_assignments, many=True)

            response_data = {
                'assignments': serializer.data,
                'home_assignment_completed': home_assignment_completed
            }

            return Response(response_data)

        except Exception as e:
            print("Exception ====> ", e)
            return Response(
                {"success": False, "error": "Something went wrong"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        

    def get_student_assignment_question(self, request, student_assignment_id):
        try:
            student_assignment = StudentAssignment.objects.get(pk=student_assignment_id)

            student_assignment_serialized = StudentAssignmentSerializer(student_assignment).data

            questions = StudentAssignmentQuestion.objects.filter(student_assignment=student_assignment).prefetch_related('student_question_options')
            questions_serialized = StudentAssignmentQuestionSerializer(questions, many=True).data

            for question in questions_serialized:
                question.pop('student_assignment', None)

            response_data = {
                "student_assignment": student_assignment_serialized,
                "questions": questions_serialized
            }

            return Response(response_data)
        except StudentAssignment.DoesNotExist:
            return Response({'error': 'StudentAssignment not found'}, status=404)
        
    def update_student_assignment_question(self, request):
        questions = request.data.get('questions', [])
        is_submit_clicked = request.data.get('is_submit_clicked', False)
        student_assignment_ids = set()  

        for question in questions:
            student_assignment_id = question.get('student_assignment_id')
            if student_assignment_id is not None:
                student_assignment_ids.add(student_assignment_id)  
            
            options = question.get('student_question_options', [])
            for option in options:
                option_id = option.get('id')
                is_correct = option.get('is_correct', False)
                
                try:
                    question_option = StudentQuestionOption.objects.get(
                        id=option_id, 
                        student_assignment_question__id=question.get('id')  
                    )
                    
                    question_option.is_correct = is_correct
                    question_option.save()
                except StudentQuestionOption.DoesNotExist:
                    continue
        
        messages = []
   
        for student_assignment_id in student_assignment_ids:
            try:
                student_assignment = StudentAssignment.objects.get(pk=student_assignment_id)
   
                if is_submit_clicked:
                    student_assignment.is_completed = True
                    student_assignment.save()
                    messages.append(f"Assignment {student_assignment_id} marked as completed successfully.")
                else:
                    pass
            except StudentAssignment.DoesNotExist:
                messages.append(f"StudentAssignment {student_assignment_id} not found.")

        if not messages:
            messages.append("No updates were made.")
        
        return Response({"messages": messages}, status=status.HTTP_200_OK)
        
    
    def correct_answer_for_questions(self, request, student_id):
        question_ids = request.data.get('question_ids', [])
        results = []

        student_answers_qs = StudentQuestionOption.objects.filter(
            student_assignment_question__assignment_question__in=question_ids,
            student__id=student_id
        ).select_related('question_option', 'student_assignment_question')

        for question_id in question_ids:
            correct_options_qs = QuestionOption.objects.filter(
                questions_id=question_id, 
                is_correct=True
            ).prefetch_related('questions')

            correct_options_serializer = QuestionOptionSerializer(correct_options_qs, many=True)

            # Filter student_answers for the current question
            filtered_student_answers = [
                ans for ans in student_answers_qs
                if ans.student_assignment_question.assignment_question_id == question_id
            ]

            validation = [{
                "student_option_id": answer.id,
                "selected_option_id": answer.question_option.id if answer.question_option else None,
                "is_correct": answer.is_correct
            } for answer in filtered_student_answers]

            results.append({
                "question_id": question_id,
                "correct_options": correct_options_serializer.data,
                "student_selection": validation
            })

        return Response(results)
    
#----------------------------------------------------------------

class CompletedClassViewSet(BaseViewset, BasePaginator):

    def get_completed_classes(self, request, student_id):
        sort_order = self.request.query_params.get('order',None)
        subject_query = request.query_params.get('search', None)

        appointments = Appointments.objects.filter(is_completed=True, student_id=student_id).exclude(status__in=['CANCELLED', 'RESCHEDULED']).order_by('created_at')

        if subject_query:
            appointments = appointments.filter(
                Q(subject__name__icontains=subject_query) 
            )
       
        valid_appointments = []
        
        for appointment in appointments:

            if appointment.type == 'cpea':
                valid_appointments.append(appointment)

            else:
                student_feedback_exists = FeedBack.objects.filter(
                    Q(student=appointment.student.id),
                    appointment=appointment,
                ).exists()

                
                tutor_feedback_exists = FeedBack.objects.filter(
                    Q(tutor=appointment.host),
                    appointment=appointment,
                ).exists()

                
                if student_feedback_exists and tutor_feedback_exists:

                    completed_molecules = AppointmentMolecule.objects.filter(
                        appointment=appointment
                    ).values_list('molecule_id', flat=True)

                    related_subtopics = MoleculeTopicSubtopic.objects.filter(
                        molecule_id__in=completed_molecules
                    ).values_list('subtopic_id', flat=True)

                    has_home_assignments = StudentAssignment.objects.filter(
                        subtopic_id__in=related_subtopics,
                        student_id=student_id,
                        type="HOME",
                        is_active=True
                    ).exists()

                    home_assignment_completed = StudentAssignment.objects.filter(
                        subtopic_id__in=related_subtopics,
                        student_id=student_id,
                        type="HOME",
                        is_active=True,
                        is_completed=True  
                    ).exists()

                    appointment.home_assignment_present = has_home_assignments  #_Transient_field
                    appointment.home_assignment_completed = home_assignment_completed

                    valid_appointments.append(appointment)

        if sort_order == 'desc':
            appointments = Appointments.objects.filter(is_completed=True, student_id=student_id).order_by('-created_at')
        else:
            appointments = Appointments.objects.filter(is_completed=True, student_id=student_id).order_by('created_at')

        paginator = CustomPageNumberPagination()
        paginated_appointment = paginator.paginate_queryset(valid_appointments, request)
        
        serializer = AppointmentSerializer(paginated_appointment, many=True, context={'request': request})
        return Response(serializer.data)
        
class LastClassViewSet(BaseViewset, BasePaginator):

    def get_last_classes(self, request, student_id):
        last_class = Appointments.objects.filter(
            student_id=student_id,
            is_completed=True
        ).order_by('-start_at').first()
        
        if last_class:
            serialized_data = AppointmentSerializer(last_class).data
            return Response({
                "last_class": serialized_data,
            })
        else:
            return Response({
                "last_class": None,
            })

 #----------------------------------------------------------------

# def generate_zoom_link(request):
#     get_zoom_link = "https://zoom.us/oauth/token"
#     client_id = os.environ.get("ZOOM_CLIENT_ID")
#     client_secret = os.environ.get("ZOOM_CLIENT_SECRET")
#     refresh_token = os.environ.get("ZOOM_REFRESH_TOKEN")
#     cleint_credentials = f"{client_id}:{client_secret}"
#     client_credentials_b64 = base64.b64encode(cleint_credentials.encode()).decode()
#     headers = {
#         "Authorization": f"Basic {client_credentials_b64}",
#         "Content-Type": "application/x-www-form-urlencoded",
#     }
#     data = {"grant_type": "refresh_token", "refresh_token": refresh_token}
#     response_token = requests.post(get_zoom_link, headers=headers, data=data)

#     if response_token.json():
#         create_meeting_url = "https://api.zoom.us/v2/users/me/meetings"
#         meeting_data = {
#             "topic": request.data["title"],
#             "type": 2,
#             "start_time": request.data["start_time"],
#             "duration": request.data["duration"],
#             "settings": {
#                 "host_video": True,
#                 "participant_video": True,
#                 "join_before_host": True,
#                 "mute_upon_entry": True,
#                 "watermark": True,
#                 "audio": "voip",
#                 "auto_recording": "cloud",
#             },
#         }

#         # Define headers with the access token
#         headers = {
#             "Authorization": f"Bearer {response_token.json()['access_token']}",
#             "Content-Type": "application/json",
#         }

#         try:
#             response = requests.post(create_meeting_url, headers=headers, json=meeting_data)

#             if response.status_code == 201:
#                 meeting_details = response.json()
#                 return {"data": meeting_details}

#             else:
#                 return {"error": response.status_code}

#         except Exception as e:
#             print(f"An error occurred: {str(e)}")
#             return {"error": f"An error occurred: {str(e)}"}

#     else:
#         return {"error": "Access token Generation Error..!!"}


# def generate_calendar_token(join_link, request, userhost):
#     client_id = os.environ.get("GMAIL_CLIENT_ID")
#     client_secret = os.environ.get("GMAIL_CLIENT_SECRET")
#     grant_type = "refresh_token"
#     refresh_token = os.environ.get("GMAIL_REFRESH_TOKEN")
#     api = f"https://oauth2.googleapis.com/token?client_id={client_id}&client_secret={client_secret}&grant_type={grant_type}&refresh_token={refresh_token}"
#     headers = {"Authorization": f"Bearer {refresh_token}", "Content-Type": "application/x-www-form-urlencoded"}
#     response_token = requests.post(api, headers=headers)
#     # print('response_token ==>>> ', response_token)
#     if response_token.json():
#         # print('userhost.email ==>> ', userhost.email)
#         calendar_api = (
#             "https://www.googleapis.com/calendar/v3/calendars/zuperscore.india@gmail.com/events?sendNotifications=true"
#         )

#         headers = {
#             "Authorization": f"Bearer {response_token.json()['access_token']}",
#             "Content-Type": "application/x-www-form-urlencoded",
#         }

#         # print('start_time ==>> ', request.data["start_time"])
#         # print('end_time ==>> ', request.data["end_time"])
#         # print('request.user.email ==>> ', request.user.email)
#         zoom_dummy = {
#             "summary": request.data["title"],
#             "start": {"dateTime": request.data["start_time"], "timeZone": "UTC"},
#             "end": {"dateTime": request.data["end_time"], "timeZone": "UTC"},
#             "description": f"Zoom Meeting Link:{join_link}",
#             "attendees": [{"email": request.user.email}],
#         }

#         response_calendar_schedule = requests.post(calendar_api, headers=headers, json=zoom_dummy)
#         # print('response_calendar_schedule.json() ==>>> ', response_calendar_schedule.json())
#         if response_calendar_schedule.json():
#             return {"data": response_calendar_schedule.json()}
#         else:
#             return {"error": "Error in Meeting Scheduling..!!"}
        
class StudentAvailabilityViewSet(BaseViewset):

    serializer_class = StudentAvailabilitySerializer
    model = StudentAvailability

    def create(self, request, pk):
        try:
            student_user = User.objects.get(id=pk)
            if hasattr(student_user, 'goal_post') and student_user.goal_post is not None:
                target_test_date_str = student_user.goal_post.get("target_test_date")
                target_test_date_1 = datetime.strptime(target_test_date_str, "%Y-%m-%d")
                core_prep_date = target_test_date_1 - timedelta(weeks=8)
            else:
                raise Http404("User's goal_post is missing or invalid.")

            data = request.data
            student_user_id = pk 
            student_availability=StudentAvailability.objects.filter(student=pk)
            test_tracker=0
            student_check=student_availability.filter(target_test_date_1__isnull=False)
            if not student_check.exists():
                            test_tracker=1
                            
            student_check=student_availability.filter(target_test_date_2__isnull=False)
            if not student_check.exists() and test_tracker==0:
                            test_tracker=2
                        
            student_check=student_availability.filter(target_test_date_3__isnull=False)
            if not student_check.exists() and test_tracker==0:
                            test_tracker=3
                            
            student_check=student_availability.filter(target_test_date_4__isnull=False)
            if not student_check.exists() and test_tracker==0:
                            test_tracker=4

            if not data: 
                default_entry = {
                    'student': student_user_id,
                    'target_test_date_1': target_test_date_str,
                    'core_prep_date': core_prep_date.strftime("%Y-%m-%d")
                }
                serializer = StudentAvailabilitySerializer(data=default_entry)
            else:
                for entry in data:
                    entry['student'] = student_user_id
                    if (test_tracker-1)==1:
                        entry['target_test_date_1'] = target_test_date_str  
                    elif (test_tracker-1)==2:
                        entry['target_test_date_2'] = target_test_date_str
                    elif (test_tracker-1)==3:
                        entry['target_test_date_3'] = target_test_date_str
                    else:
                        entry['target_test_date_4'] = target_test_date_str
                    entry['core_prep_date'] = core_prep_date.strftime("%Y-%m-%d") 
                    if 'start_date' in entry and entry['start_date'] is not None and 'end_date' in entry and entry['end_date'] is not None:
                        entry['total_days']=int((datetime.strptime(entry['end_date'], "%Y-%m-%d") - datetime.strptime(entry['start_date'], "%Y-%m-%d")).days) + 1
                    
                serializer = StudentAvailabilitySerializer(data=data, many=True)
            if serializer.is_valid():
                serializer.save()
                return Response({
                    "success": True,
                    "status": "success",
                    "message": "Dates created successfully",
                    "results": serializer.data,
                }, status=status.HTTP_201_CREATED)
            else:
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        except User.DoesNotExist:
            return Response({"success": False, "error": "User does not exist"}, status=status.HTTP_404_NOT_FOUND)
        except Http404 as e:
            print("Http404 Exception: ", e)
            return Response({"success": False, "error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            print("Exception: ", e)
            return Response({"success": False, "error": "Something went wrong"}, status=status.HTTP_400_BAD_REQUEST)
        
    def update_days(self, request, student_id):
        try:
            entry=request.data
            student_availability=StudentAvailability.objects.filter(student_id=student_id,start_date__isnull=True,end_date__isnull=True,type__isnull=False)
            if 'type' in entry and entry['type']=='black_out':
                student_availability=student_availability.filter(type='black_out').first()
            elif 'type' in entry and entry['type']=='accelerator':
                student_availability=student_availability.filter(type='accelerator').first()
            else :
                raise Http404('Invalid data')
            
            if 'total_days' in entry and entry['total_days'] is not None and student_availability is not None:
                student_availability.total_days=entry['total_days']

                student_availability.save()
                serializer=StudentAvailabilitySerializer(student_availability)
                return Response({"success": True, "status": "success", "message": "Dates updated successfully", "results": serializer.data}, status=status.HTTP_200_OK)
            else:
                raise Http404('Invalid data')

        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_404_NOT_FOUND)
        
    def get_by_id(self, request, pk):
        try:
            student_availability = StudentAvailability.objects.filter(student=pk)
            serializer = StudentAvailabilitySerializer(student_availability, many=True)

            recent_updates = {}
            recent_updates_set = set() 
            recent_update_tuple=()

            for availability in student_availability:
                if availability.target_test_date_1 is None:
                    continue
                recent_target_test_dates = [
                    availability.target_test_date_1,
                    availability.target_test_date_2,
                    availability.target_test_date_3,
                    availability.target_test_date_4,
                ]

                recent_target_test_date=max((i for i in recent_target_test_dates if i is not None))
                print("execute=======>2", availability)
                print("recent target test=====>",recent_target_test_date)
                # if recent_update_tuple==():
                recent_core_prep_date = availability.core_prep_date
                if recent_update_tuple != () and recent_update_tuple[0] < recent_target_test_date:
                    print("run inside if")
                    recent_update_tuple = (recent_target_test_date, recent_core_prep_date) 
                
                if recent_update_tuple not in recent_updates_set:
                    recent_updates = {
                        'target_test_date': recent_target_test_date,
                        'core_prep_date': recent_core_prep_date,
                    }
                    recent_updates_set.add(recent_update_tuple)

            response_data = {
                "recentUpdates": recent_updates,
                "data": serializer.data,
            }

            return Response({
                "success": True,
                "status": "success",
                "message": "Date retrieved successfully",
                "results": response_data,
            }, status=status.HTTP_200_OK)

        except Exception as e:
            print("Exception=====>", e)
            return Response(
                {"success": False, "status": "error", "message": "Something went wrong"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
                    
            
    def destroy(self, request, pk):
        try:
            student_availability = StudentAvailability.objects.filter(id=pk)
            student_availability.delete()
            return Response(
                {"success": True, "status": "success", "message": "Deleted successfully"},
                status=status.HTTP_200_OK,
            )
        except Exception as e:
            print("Exception=====>", e)
            return Response(
                {"success": False, "status": "error", "message": "Something went wrong"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
    
    def get(self, request):
        try:
            student_availabilities = StudentAvailability.objects.all()
            serializer = StudentAvailabilitySerializer(student_availabilities, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)

        except Exception as e:
            print("Exception=====>", e)
            return Response(
                {"success": False, "status": "error", "message": "Something went wrong"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
        
class CalculateStudentAvailabilityViewSet(BaseViewset):

    def calculate_availability(self, request, student_id):
        try:
            student_availabilities = StudentAvailability.objects.filter(student=student_id)
            
            if not student_availabilities.exists(): 
                raise Http404('Student not found') 

            total_blackout_days = 0
            total_accelerator_days = 0
            target_test_date_1 = None
            join_date = student_availabilities[0].student.class_start_date
            subject_name = None
            core_prep_date = None
            total_classes_per_week = 0
            test_tracker=0
            student_check=student_availabilities.filter(target_test_date_1__isnull=False)
            if not student_check.exists() and test_tracker==0:
                    test_tracker=1
                
            student_check=student_availabilities.filter(target_test_date_2__isnull=False)
            if not student_check.exists() and test_tracker==0 :
                    test_tracker=2
                
            student_check=student_availabilities.filter(target_test_date_3__isnull=False)
            if not student_check.exists() and test_tracker==0:
                    test_tracker=3
                
            student_check=student_availabilities.filter(target_test_date_4__isnull=False)
            if not student_check.exists() and test_tracker==0:
                    test_tracker=4
        
            for student_availability in student_availabilities:
                core_prep_date = student_availability.core_prep_date
                        
                if (test_tracker-1)==1:
                    target_test_date_1 = student_availability.target_test_date_1
                elif (test_tracker-1)==2:
                    target_test_date_1 = student_availability.target_test_date_2
                elif (test_tracker-1)==3:
                    target_test_date_1 = student_availability.target_test_date_3
                else :
                    target_test_date_1 = student_availability.target_test_date_4
        
                # target_test_date_1 = student_availability.target_test_date_1
                start_date = student_availability.start_date
                end_date = student_availability.end_date
                total_days=student_availability.total_days
                if total_days==0 and start_date is not None and end_date is not None:
                        if student_availability.type == 'black_out':
                                total_blackout_days += (end_date - start_date).days + 1
                        elif student_availability.type == 'accelerator':
                                total_accelerator_days += (end_date - start_date).days + 1
                        
                else :
                     if student_availability.type == 'black_out':
                         total_blackout_days+=student_availability.total_days
                     elif student_availability.type == 'accelerator':
                          total_accelerator_days+=student_availability.total_days

            # Convert to weeks
            total_blackout_weeks = total_blackout_days / 7
            total_accelerator_weeks = total_accelerator_days / 7 
            number_of_weeks = abs((core_prep_date - join_date).days) / 7

            disposable_time = math.ceil(number_of_weeks) - math.ceil(total_blackout_weeks) + 0.5 * math.ceil(total_accelerator_weeks)
            student_session_plans = StudentSessionPlan.objects.filter(student=student_id)
            
            if not student_session_plans.exists(): 
                raise Http404('Student has not been assigned any session plan') 
            
            temp_dict = {}
            temp_dict['total_blackout_days'] = abs(math.ceil(total_blackout_days))
            temp_dict['total_accelerator_days'] = abs(math.ceil(total_accelerator_days))
            temp_dict['total_blackout_weeks'] = abs(math.ceil(total_blackout_weeks))
            temp_dict['total_accelerator_weeks'] = abs(math.ceil(total_accelerator_weeks))
            temp_dict['number_of_weeks'] = abs(math.ceil(number_of_weeks))
            temp_dict['target_test_date_1'] = target_test_date_1
            temp_dict['core_prep_date'] = core_prep_date

            english_number_of_molecules = 0
            math_number_of_molecules = 0

            for session_plan in student_session_plans:
                subject_name = session_plan.subject.name

                if subject_name:
                    number_of_molecule = MotherSessionMolecule.objects.filter(session_plan=session_plan.session_plan.id).count()
                    if subject_name.lower() == "english": 
                        e_category = session_plan.category
                        if e_category.upper() == "R":
                            english_number_of_molecules += number_of_molecule / 2
                        elif e_category.upper() == "S":
                            english_number_of_molecules += number_of_molecule / 3
                        elif e_category.upper() == "T":
                            english_number_of_molecules += number_of_molecule / 4

                    elif subject_name.lower() == "math":
                        m_category = session_plan.category
                        if m_category.upper() == "R":
                            math_number_of_molecules += number_of_molecule / 2
                        elif m_category.upper() == "S":
                            math_number_of_molecules += number_of_molecule / 3
                        elif m_category.upper() == "T":
                            math_number_of_molecules += number_of_molecule / 4

            temp_dict['english_number_of_molecules'] = temp_dict.get('english_number_of_molecules', 0) + english_number_of_molecules
            temp_dict['math_number_of_molecules'] = temp_dict.get('math_number_of_molecules', 0) + math_number_of_molecules

            total_session = temp_dict['english_number_of_molecules'] + temp_dict['math_number_of_molecules']

            No_of_Session_per_Week = abs(math.ceil(total_session / disposable_time))
            temp_dict['total_classes'] = No_of_Session_per_Week

            return Response({
                "success": True,
                "status": "success",
                "message": "Calculation performed successfully.",
                "results":temp_dict
            }, status=status.HTTP_200_OK)

        except Http404 as e:
            return Response({'error': str(e)}, status=status.HTTP_404_NOT_FOUND)

        except Exception as e:
            print("Exception=====>", e)
            return Response(
                {"success": False, "status": "error", "message": "Something went wrong"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
       
class AssignCategoryViewSet(BaseViewset):

    def assign_category(self, request, student_id):
        print("enter in code")
        try:
            data_list = request.data 
            user = User.objects.get(id=student_id)
            print("user===>",user)

            user.test_results = data_list

            for data in data_list:
                english_score = int(data.get('score', {}).get('english', 0))
                math_score = int(data.get('score', {}).get('math', 0))

                # Determine English category
                if english_score > 650:
                    user.english_category = EnglishCategory.objects.get(name="T")
                elif 550 <= english_score <= 650:
                    user.english_category = EnglishCategory.objects.get(name="S")
                else:
                    user.english_category = EnglishCategory.objects.get(name="R")
                    
                # Determine Math category
                if math_score > 650:
                    user.math_category = MathCategory.objects.get(name="T")
                elif 550 <= math_score <= 650:
                    user.math_category = MathCategory.objects.get(name="S")
                else:
                    user.math_category = MathCategory.objects.get(name="R")

                user.save()

            return Response({"success": "Test results processed successfully"}, status=status.HTTP_200_OK)

        except Exception as e:
            print("Exception=====>", e)
            return Response(
                {"success": False, "status": "error", "message": "Something went wrong"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


class UsersTeamViewSet(BaseViewset):

    def user_list(self, request):
        try:
            type = request.query_params.get('type', None)
            
            if type == "english_reading":
                users = User.objects.filter(tutor_type="english_reading", role='tutor')
            elif type == "english_writing":
                users = User.objects.filter(tutor_type="english_writing", role='tutor')
            elif type == "math":
                users = User.objects.filter(tutor_type="math", role='tutor')
                
            elif type == "manager":
                users = User.objects.filter(role="manager")
            elif type == "prep_manager":
                users = User.objects.filter(role="prep_manager")
            elif type == "sso_manager":
                users = User.objects.filter(role="sso_manager")
            elif type == "manager":
                users = User.objects.filter(role="manager")
            
            serializer = UserMinimumSerializer(users, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)

        except Exception as e:
            print("Exception=====>", e)
            return Response(
                {"success": False, "status": "error", "message": "Something went wrong"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
              

    def get_user_teams(self,request, user_id):
        try:
            user = User.objects.get(pk=user_id)
            print("user==>",user)

            if user.role == "user" and user.english_category and user.math_category:
                print("enter")
                english_reading_tutors = User.objects.filter(role="tutor", tutor_type="english_reading", english_category=user.english_category)
                english_writing_tutors = User.objects.filter(role="tutor", tutor_type="english_writing", english_category=user.english_category)
                math_tutors = User.objects.filter(role="tutor", tutor_type="math", math_category=user.math_category)
                teams = english_reading_tutors | english_writing_tutors | math_tutors
            else:
                teams = (
                    user.sso_managers.all() |
                    user.prep_managers.all() |
                    user.ops_managers.all() |
                    user.english_tutors.all() |
                    user.math_tutors.all()
                ).distinct()

            serializer = UserMinimumSerializer(teams, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        
        except Exception as e:
            print("Exception=====>", e)
            return Response(
                {"success": False, "status": "error", "message": "Something went wrong"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


    def create_student_team(self, request):
        try:
            student_id = request.data.get("student_id")
            user_id = request.data.get("user_id")

            student = User.objects.get(pk=student_id)
            user = User.objects.get(id=user_id)
            role = 'TUTOR'
            # Perform the Day-Schedule ID check only for tutors
            if user.role == "tutor" and not user.day_schedule_user_id:
                print("Enter")
                return Response({
                    "success": False,
                    "status": "error",
                    "message": "Tutor must integrate Day-Schedule ID first."
                }, status=status.HTTP_400_BAD_REQUEST)

            # Assigning tutors based on their tutor type
            if user.tutor_type == "english_reading":
                student.english_reading_tutors.add(user)
            elif user.tutor_type == "english_writing":
                student.english_writing_tutors.add(user)
            elif user.tutor_type == "math":
                student.math_tutors.add(user)

 
            elif user.role == "prep_manager":
                role = 'PREP MANAGER'
                student.prep_managers.add(user)
            elif user.role == "sso_manager":
                role = 'SSO MANAGER'
                student.sso_managers.add(user)
            elif user.role == "manager":
                role = 'MANAGER'
                student.ops_managers.add(user)

            student.save()
            message = role + "assigned successfully..!!"
            return Response({
                    "success": True,
                    "status": "success",
                    "message": message,
                }, status=status.HTTP_200_OK)

        except Exception as e:
            print("Exception=====>", e)
            return Response(
                {"success": False, "status": "error", "message": "Something went wrong"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
        

    def delete_student_team(self, request, student_id, user_id):
        try:

            student = User.objects.get(pk= student_id)
            user = User.objects.get(id = user_id)

            if user.tutor_type == "english_reading": 
                student.english_reading_tutors.remove(user)
            if user.tutor_type == "english_writing": 
                student.english_writing_tutors.remove(user)
            elif user.tutor_type == "math":
                student.math_tutors.remove(user)
            elif user.role == "prep_manager":
                student.prep_managers.remove(user)
            elif user.role == "sso_manager":
                student.sso_managers.remove(user)
            elif user.role == "ops_manager":
                student.ops_managers.remove(user)

            return Response({
                "success": True,
                "status": "success",
                "message": "Team Member Removed successfully.",
                }, status=status.HTTP_200_OK)
        
        except Exception as e:
            print("Exception=====>", e)
        return Response({
            "success": False, "status": "error", "message": "Something went wrong"
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class TutorDashBoradViewSet(BaseViewset):

    def tutor_dashboard(self,request):
        logged_in_user_id = request.user.id
        user = User.objects.get(id=logged_in_user_id, is_active=True)
        english_reading_tutors = user.english_reading_tutors.all().distinct()
        english_writing_tutors = user.english_writing_tutors.all().distinct()
        math_tutors = user.math_tutors.all().distinct()
        
        if user.tutor_type.lower() == 'math':
            users = math_tutors

        elif user.tutor_type.lower() == 'english_reading':
            users = english_reading_tutors
        else:
            users = english_writing_tutors 

        current_time = datetime.now()
        upcoming_appointments = Appointments.objects.filter(
            host=logged_in_user_id,
            start_at__gt=current_time,
            is_completed = False 
        ).exclude(status__in=['CANCELLED', 'RESCHEDULED']).order_by('start_at')

        
        total_feedback = FeedBack.objects.filter(
            tutor = logged_in_user_id
        )
        serialized_users = UserMinimumSerializer(users, many=True).data
        


        return Response({
            "total_students": len(serialized_users), #users.count(),
            "total_upcoming_classes": upcoming_appointments.count(),  
            "total_feedbacks":total_feedback.count()
        })


class TeacherAppointmentFeedbackViewSet(BaseViewset):    
    def list(self, request, appointment_id):
        try:
            tutor_id = request.query_params.get('tutor_id')
            student_id = request.query_params.get('student_id')

            feedback_type = 'tutor' if tutor_id else 'student'            
            response_data = {
                "appointment_molecule": [],
                "feedback": []
            }

            appointment_molecules = AppointmentMolecule.objects.filter(appointment_id=appointment_id).order_by('created_at')
            response_data["appointment_molecule"] = AppointmentMoleculeSerializers(appointment_molecules, many=True).data

            
            all_feedback_questions = FeedbackQuestions.objects.filter(type=feedback_type)

            feedback_filter = Q(appointment_id=appointment_id)
            if tutor_id:
                feedback_filter &= Q(tutor_id=tutor_id)
                feedback_filter &= Q(commenter='tutor')

            if student_id:
                feedback_filter &= Q(student_id=student_id) & (Q(commenter='tutor') | Q(commenter='user'))
                
            feedback_entries = FeedBack.objects.filter(feedback_filter).order_by("-created_at")

            if feedback_entries:
                for fb in feedback_entries:
                    feedback_serializer = AppointmentFeedbackSerializers(fb).data
                    feedback_question_ratings_data = []

                    comment_key = "tutor_comment" if fb.commenter == 'tutor' else "student_comment"
                    feedback_serializer[comment_key] = feedback_serializer.pop('comment')

                    for question in all_feedback_questions:
                        rating = FeedbackQuestionRating.objects.filter(feedback_id=fb.id, question=question).first()
                        rating_data = FeedbackQuestionRatingSerializer(rating).data if rating else None
                        question_data = FeedbackQuestionSerializer(question).data
                        question_data['rating'] = rating_data
                        feedback_question_ratings_data.append(question_data)

                    feedback_serializer["feedback_question_ratings"] = feedback_question_ratings_data
                    response_data["feedback"].append(feedback_serializer)
            else:
                feedback_question_ratings_data = []
                for question in all_feedback_questions:
                    question_data = FeedbackQuestionSerializer(question).data
                    question_data['rating'] = None
                    feedback_question_ratings_data.append(question_data)

               
                response_data["feedback"].append({
                    "feedback_question_ratings": feedback_question_ratings_data
                })

            return Response({
                "success": True,
                "status": "success",
                "results": [response_data]  
            }, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({
                "success": False,
                "status": "error",
                "message": "Something went wrong: " + str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
        
   
class StudentDashBoardViewSet(BaseViewset):

    def get_student_availabilities(self, student_id):
        student_availabilities = StudentAvailability.objects.filter(student=student_id)
        if not student_availabilities.exists():
            raise Http404('Student not found')
        return student_availabilities

    def get_test_tracker(self, student_availabilities):
        for i in range(1, 5):
            student_check = student_availabilities.filter(**{f'target_test_date_{i}__isnull': False})
            if student_check.exists():
                return i
        return 0

    def get_course_and_exam_dates(self, student_availabilities, test_tracker):
        course_end_date = None
        exam_date = None
        for student_availability in student_availabilities:
            if not course_end_date and student_availability.core_prep_date:
                course_end_date = student_availability.core_prep_date
            if test_tracker == 1:
                exam_date = student_availability.target_test_date_1
            elif test_tracker == 2:
                exam_date = student_availability.target_test_date_2
            elif test_tracker == 3:
                exam_date = student_availability.target_test_date_3
            elif test_tracker == 4:
                exam_date = student_availability.target_test_date_4
        return course_end_date, exam_date

    def calculate_total_days(self, student_availabilities):
        total_blackout_days = 0
        total_accelerator_days = 0
        for student_availability in student_availabilities:
            start_date = student_availability.start_date
            end_date = student_availability.end_date
            total_days = student_availability.total_days
            if total_days == 0 and start_date and end_date:
                days = (end_date - start_date).days + 1
            else:
                days = total_days
            if student_availability.type == 'black_out':
                total_blackout_days += days
            elif student_availability.type == 'accelerator':
                total_accelerator_days += days
        return total_blackout_days, total_accelerator_days

    def get_tutors_assigned(self, user):
        return {
            'english_reading': user.english_reading_tutors.exists(),
            'english_writing': user.english_writing_tutors.exists(),
            'math': user.math_tutors.exists()
        }

    def get_session_completion(self, student_session_plans, student_id, tutors_assigned):
        session_completed = {
            'english_reading': False,
            'english_writing': False,
            'math': False
        }
        sessions_assigned = {
            'english_reading': False,
            'english_writing': False,
            'math': False
        }

        for session_plan in student_session_plans:
            domain_name = session_plan.mega_domain.name.lower()
            related_assignments = StudentAssignment.objects.filter(
                student_id=student_id,
                megadomain=session_plan.mega_domain,
                type='HOME',
                is_completed=False
            )

            is_completed = getattr(session_plan, 'is_completed', False)

            if domain_name == 'reading' and tutors_assigned['english_reading']:
                sessions_assigned['english_reading'] = True
                session_completed['english_reading'] = not related_assignments.exists() or is_completed
            elif domain_name == 'writing' and tutors_assigned['english_writing']:
                sessions_assigned['english_writing'] = True
                session_completed['english_writing'] = not related_assignments.exists() or is_completed
            elif domain_name == 'math' and tutors_assigned['math']:
                sessions_assigned['math'] = True
                session_completed['math'] = not related_assignments.exists() or is_completed

            if not related_assignments.exists() or is_completed:
                session_plan.is_completed = True
                session_plan.save()

        for key in session_completed:
            if session_completed[key] is None:
                session_completed[key] = False

        return sessions_assigned, session_completed

    def calculate_total_classes(self, student_session_plans):
        english_number_of_molecules_list = []
        math_number_of_molecules_list = []

        for session_plan in student_session_plans:
            subject_name = session_plan.subject.name.lower()
            category = session_plan.category.upper()
            number_of_molecule = MotherSessionMolecule.objects.filter(session_plan=session_plan.session_plan_id).count()
            if subject_name == "english":
                if category == "R":
                    english_number_of_molecules_list.append(number_of_molecule / 2)
                elif category == "S":
                    english_number_of_molecules_list.append(number_of_molecule / 3)
                elif category == "T":
                    english_number_of_molecules_list.append(number_of_molecule / 4)
            elif subject_name == "math":
                if category == "R":
                    math_number_of_molecules_list.append(number_of_molecule / 2)
                elif category == "S":
                    math_number_of_molecules_list.append(number_of_molecule / 3)
                elif category == "T":
                    math_number_of_molecules_list.append(number_of_molecule / 4)

        total_classes = math.ceil(sum(english_number_of_molecules_list)) + math.ceil(sum(math_number_of_molecules_list))
        return total_classes

    def calculate_student_progress(self, request, student_id):
        try:
            student_availabilities = self.get_student_availabilities(student_id)
            student = student_availabilities.first().student
            join_date = student.class_start_date
            # student_availabilities[0].student.class_start_date
            print("join_date",join_date)
            test_tracker = self.get_test_tracker(student_availabilities)
            course_end_date, exam_date = self.get_course_and_exam_dates(student_availabilities, test_tracker)

            if not course_end_date:
                return Response({
                    "success": False,
                    "status": "error",
                    "message": "Course end date (core_prep_date) is missing for the student."
                }, status=status.HTTP_400_BAD_REQUEST)

            if not exam_date:
                return Response({
                    "success": False,
                    "status": "error",
                    "message": "Exam date (target_test_date_1) is missing for the student."
                }, status=status.HTTP_400_BAD_REQUEST)

            total_blackout_days, total_accelerator_days = self.calculate_total_days(student_availabilities)
            user = User.objects.get(id=student_id)
            tutors_assigned = self.get_tutors_assigned(user)
            student_session_plans = StudentSessionPlan.objects.filter(student=student_id)

            sessions_assigned, session_completed = self.get_session_completion(
                student_session_plans, student_id, tutors_assigned
            )

            total_classes = self.calculate_total_classes(student_session_plans)
            print("total_classes",total_classes)
            total_course_duration_days = (course_end_date - join_date).days
            print("total_course_duration_days",total_course_duration_days)
            elapsed_duration_days = (date.today() - join_date).days
            print("elapsed_duration_days",elapsed_duration_days)

            if elapsed_duration_days > total_course_duration_days:
                elapsed_duration_days = total_course_duration_days

            proportion_of_course_elapsed = elapsed_duration_days / total_course_duration_days if total_course_duration_days > 0 else 0
            print("Proportion of course elapsed", proportion_of_course_elapsed)
            expected_classes = max(0, proportion_of_course_elapsed * total_classes)
            print("expected_classes==>",expected_classes)
            total_attended_classes = Appointments.objects.filter(
                student_id=student_id,
                is_completed=True,
                is_active=True
            ).count()

            results = {
                'total_classes': total_classes,
                'expected_classes': math.ceil(expected_classes),
                'course_end_date': course_end_date,
                'exam_date': exam_date,
                'total_attended_classes': total_attended_classes,
                'english_reading_assigned': sessions_assigned['english_reading'],
                'english_writing_assigned': sessions_assigned['english_writing'],
                'math_assigned': sessions_assigned['math'],
                'math_session_completed': session_completed['math'],
                'english_writing_session_completed': session_completed['english_writing'],
                'english_reading_session_completed': session_completed['english_reading'],
                'total_class_per_day': user.total_class_per_day,
                'total_mega_domain_class_per_day': user.total_mega_domain_class_per_day
            }

            return Response({
                "success": True,
                "status": "success",
                "message": "Total classes calculated successfully.",
                "results": results
            }, status=status.HTTP_200_OK)

        except Exception as e:
            print("Exception=====>", e)
            return Response(
                {"success": False, "status": "error", "message": "Something went wrong"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
         
class NewAssignmentSerializer(BaseSerializer): 
    class Meta:
        model = Assignment
        fields = "__all__"

class CpeaReportSerializer(serializers.ModelSerializer):
    class Meta:
        model = CpeaReport
        fields = '__all__'

class StudentCpeaReportSerializer(serializers.ModelSerializer):
    student_name = serializers.SerializerMethodField()
    mega_domain = serializers.SerializerMethodField()
    class Meta:
        model = StudentCpeaReport
        fields = '__all__'
    
    def get_student_name(self, obj):
        return f"{obj.student.first_name} {obj.student.last_name}"

    def get_mega_domain(Self, obj):
        return obj.appointment.mega_domain 
    
   
    
class CpeaBaseViewSet(BaseViewset):

    def get_cpea_assignment(self, request, mega_domain):
         
        mega_domain_prefix = {
            'reading': 'CPEA_R',
            'writing': 'CPEA_W',
            'math': 'CPEA_M'
        }.get(mega_domain.lower())

        if not mega_domain_prefix:
            return Response({'error': 'Invalid mega domain.'}, status=400)

        assignments = Assignment.objects.filter(type__startswith=mega_domain_prefix, is_active=True)
        print("assignment==>",assignments)
        serializer = NewAssignmentSerializer(assignments, many=True)
        return Response({
                    "success": True,
                    "status": "success",
                    "message": "CPEA Assignmets..!!",
                    "results": serializer.data
                }, status=status.HTTP_200_OK)
    

    def post_cpea_assignment_report(self, request,student_id,tutor_id):
        try:
            student = User.objects.get(id=student_id)
            tutor = User.objects.get(id=tutor_id)
            appointment = Appointments.objects.get(id=request.data.get('appointment'))  

        except User.DoesNotExist:
            return Response({'error': 'Student or Tutor not found.'}, status=404)
        
        answers_data = request.data.get('answers', [])
        overall_feedback = request.data.get('overall_feedback')

        score_mapping = {
        "WELL_LEARNT": 2,
        "REMEMBERS_PARTIALLY": 1,
        "COULD_NOT_RECALL": 0
        }

        for answer in answers_data:
            answer_score = score_mapping.get(answer.get('remark'), 0)  
            answer['score'] = answer_score

        cpea_report = StudentCpeaReport.objects.create(
            student=student,
            tutor=tutor,
            appointment=appointment, 
            # status=status,
            answers = answers_data,
            overall_feedback= overall_feedback,
            # assignment=assignment,
        )

        appointment.is_completed=True
        appointment.save()

        serializer = StudentCpeaReportSerializer(cpea_report)
        return Response({
                    "success": True,
                    "status": "success",
                    "message": "CPEA report submitted successfully",
                    "results": serializer.data,
                })
    
    
    def get_student_cpea_report(self, request, student_id):
            appointment_id = request.query_params.get("appointment_id")
            if appointment_id:
                student_cpea_report = StudentCpeaReport.objects.filter(student=student_id, appointment=appointment_id)
            else:
                student_cpea_report = StudentCpeaReport.objects.filter(student=student_id)
            
            serializers = StudentCpeaReportSerializer(student_cpea_report, many=True)
            return Response({
                "sucess": True,
                "status": "success",
                "message":"CPEA Results..!!",
                "results": serializers.data,
            })
    
    
    

    def update_student_cpea_report(self, request, student_id, appointment_id):
        cpea_report = StudentCpeaReport.objects.get(student=student_id, appointment=appointment_id)

        is_student_view = request.data.get('is_student_view', False)
        cpea_report.is_student_view = is_student_view
        cpea_report.save()

        return Response({
            "sucess":True,
            "status": "success",
            "message":"Update Sucessfully"
        })

    
    def get_cpea_questions(self,request, mega_domain_name):
        mega_domain = MegaDomain.objects.filter(name=mega_domain_name).values_list('id', flat=True)
        cpea_qns = CpeaReport.objects.filter(mega_domain_id__in=mega_domain)
        serializer = CpeaReportSerializer(cpea_qns, many=True)
        return Response({
                "sucess": True, 
                "status": "success",
                "message":"CPEA Questions",
                "results": serializer.data,
            })
    
class StudentReadingCpeaReportSerializer(serializers.ModelSerializer):
    class Meta:
        model = StudentReadingCpeaReport
        fields = '__all__'
    
class ReadingCpeaBaseViewSet(BaseViewset):
    
    def create_reading_cpea_report(self, request):
        try:
            type = request.data.get('type')
            student_id = request.data.get('student_id')
            mega_domain = request.data.get('mega_domain')
            reports = request.data.get('reports')

            for report_data in reports:
                report_data['type'] = type
                report_data['student'] = student_id
                report_data['mega_domain'] = mega_domain

                serializer = StudentReadingCpeaReportSerializer(data=report_data)
                if serializer.is_valid():
                    serializer.save()
                else:
                    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
                
            return Response({
            "success": True,
            "status": "success",
            "message": "CPEA Reading created Successfully",
            "results": serializer.data,
            })
        except Exception as e:
            return Response(str(e), status=status.HTTP_500_INTERNAL_SERVER_ERROR)
     

    
    
class GroupClassSerializer(serializers.ModelSerializer):
    class Meta:
        model = StudentGroupEvents
        fields = '__all__'

class GroupClassesBaseViewSet(BaseViewset):

    def get_dayScheduler_group_events(self, request, student_id):
        try:
            subject = request.query_params.get('subject')
            student_group_events = StudentGroupEvents.objects.filter(student_id=student_id, subject=subject, is_sso_verified= True)
            print("student_group_event===>", student_group_events)
            serializer = GroupClassSerializer(student_group_events, many=True)
            serialized_data = serializer.data
            print("serialized_data==>",serialized_data)

            today = datetime.today() - timedelta(days=1)
            end_date = today + timedelta(days=7)

            for event in serialized_data:
                pk = event['event_id']
                print("event_id==>",pk)
                get_available_appointments_url = f"https://api.dayschedule.com/v1/availability/{pk}/"
                headers = {"Content-Type": "application/json",}
                params = {
                    "apiKey": "AOthHfwumTELV7qUslLHRNxeOpObRhvp",
                    "start": request.query_params.get("start", today.isoformat()),
                    "end": request.query_params.get("end", end_date.isoformat()),   
                    "time_zone": request.query_params.get("time_zone", "Asia/Calcutta"),  
                    "duration": request.query_params.get("duration", ""),
                }

                response = requests.get(get_available_appointments_url, headers=headers, params=params)
                print("response==>",response)
                if response.status_code == 200:
                    print("200")
                    event_details = response.json()
                    ("result", {})
                    event['event_details'] = event_details
            return Response(serialized_data, status=status.HTTP_200_OK)

        except Exception as e:
            print("Error Occurred:", e)
            return Response({"error": "Internal Server Error"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class AssignGroupClassesBaseViewSet(BaseViewset):

    def assign_group_classes(self, request, deptHead_id):
        try:
            deptHead = User.objects.get(id=deptHead_id)  
        except User.DoesNotExist:
            return Response({'error': 'Department Head not found.'}, status=404)
        
        sso = User.objects.get(id=request.data.get('sso'))  
    
        target_test_date = request.data.get('targetDt',None)

        if not sso:
            return Response({'error':'SSO Id is required'},status=404)
        
        if not target_test_date:
            return Response({'error':'Target Test Date is Required'},status=404)

        student_ids = request.data.get('studentList', [])
        class_events = request.data.get('classEvents', [])

        if not student_ids:
            return Response({'error': 'Student IDs are required.'}, status=400)
        if not class_events:
            return Response({'error': 'Class events are required.'}, status=400)

        created_group_classes = []

        try:
            for student_id in student_ids:
                student = User.objects.get(id=student_id)
                for class_event in class_events:
                    tutor_id = class_event.get('tutorId')
                    tutor_name = class_event.get('tutorName')
                    class_name = class_event.get('className')
                    # subject = class_event.get('subject')
                    event_id = class_event.get('eventId')
                    group_id = class_event.get('groupId')

                    if not (tutor_id and tutor_name and class_name and event_id):
                        return Response({'error': 'Incomplete class event information provided.'}, status=400)

                    try:
                        tutor = User.objects.get(id=tutor_id)
                        subject = tutor.tutor_type.title()
                    except User.DoesNotExist:
                        return Response({'error': 'Tutor not found.'}, status=404)

                    group_class = StudentGroupEvents.objects.create(
                        student=student,
                        deptHead=deptHead,
                        class_name=class_name,
                        tutor_name=tutor_name,
                        tutor=tutor,
                        subject=subject,
                        event_id=event_id,
                        group_id=group_id,
                        sso=sso,
                        target_test_date=target_test_date,
                        
                    )
                    created_group_classes.append(group_class)
        except User.DoesNotExist:
            return Response({'error': 'One or more users not found.'}, status=404)
        except KeyError as e:
            return Response({'error': f'Missing key in class event: {e}'}, status=400)
        except serializers.ValidationError as e:
            return Response({'error': str(e)}, status=400)

        serializer = GroupClassSerializer(created_group_classes, many=True)
        return Response({
            "success": True,
            "status": "success",
            "message": "Group Classes added!",
            "results": serializer.data,
        })
    

class StudentGroupEventBaseViewSet(BaseViewset):

    def get_student_group_events(self,request):
        logged_in_user_sso = request.user
        search = request.GET.get('search', None)
        events_query = StudentGroupEvents.objects.filter(sso=logged_in_user_sso)
        if search:
            events_query = events_query.filter(class_name__icontains=search)    
        grouped_events = (
            events_query
            .values('group_id', 'tutor_name', 'class_name', 'subject','is_sso_verified','target_test_date')
            .annotate(
                total_events=Count('event_id',distinct=True),
                total_students=Count('student', distinct=True),
                events_list=Count('id'),
                max_id=Max('id'),
            )
            .order_by('-max_id')
        )

        paginator = CustomPageNumberPagination()
        paginated_students = paginator.paginate_queryset(grouped_events, request)
        response_data = {'events_list': []}
        for group_event in paginated_students:
            events = (
                StudentGroupEvents.objects
                .filter(group_id=group_event['group_id'], sso=logged_in_user_sso)
                .values('event_id', 'class_name', 'tutor_name', 'subject', 'is_taken',
                        'is_sso_verified', 'target_test_date', 'group_id')       
            )
            
            group_info = {
                'group_id': group_event['group_id'],
                'total_events': group_event['total_events'],
                'total_students': group_event['total_students'],
                'tutor_name': group_event['tutor_name'],
                'class_name': group_event['class_name'],
                'subject': group_event['subject'],
                'is_sso_verified': group_event['is_sso_verified'],
                'target_test_date': group_event['target_test_date'],
                'events': list(events)
            }
            response_data['events_list'].append(group_info)

        response_data=paginator.get_paginated_response(response_data)#add
        return Response(
                response_data.data
            )

class AllotGroupClassBaseViewSet(BaseViewset):

    def allot_group_classes(self, request):
        try:
            subject = request.query_params.get('subject')
            group_id = request.query_params.get('group_id')
            student_ids = request.data.get('student_ids',[])

            for student_id in student_ids:
                StudentGroupEvents.objects.filter(student_id=student_id, is_sso_verified= False, subject=subject, group_id=group_id).update(is_sso_verified=True)

            return Response({
                "success": True,
                "status": "success",
                "message": "SSO Verfied all the Checked Students",
            })
        
        except Exception as e :
            print("Exception==========>",e)
            return Response({"message": "Something went wrong"})
        
class CheckStudentGroupBaseViewSet(BaseViewset):

    def check_student_group_assignment(self, request, student_id):
        try:
            subjects = ["English_Reading", "English_Writing", "Math"]

            results = {}
            for subject in subjects:
                group_class_assigned = StudentGroupEvents.objects.filter(student_id=student_id, subject=subject, is_sso_verified=True).exists()
                results[subject] = group_class_assigned

            return Response({
                "success": True,
                "status": "success",
                "message": "Student Status",
                "results": results
            })

        except StudentGroupEvents.DoesNotExist:
            return Response({
                "success": True,
                "status": "success",
                "message": "No group classes assigned for this student",
                "results": {subject: False for subject in subjects}
            })
        
class SsoStudentBaseViewSet(BaseViewset):

    def get_sso_students_by_group_id(self, request, group_id):
        try:
            student_events = StudentGroupEvents.objects.filter(group_id=group_id).order_by('-created_at')
            student_ids = student_events.values_list('student', flat=True)
            sso_id = student_events.first().sso_id
            group_subject = student_events.first().subject

            user_queryset = User.objects.filter(id__in=student_ids)

            student_type = student_events.first().student.isRepeater

            if student_type:
                user_queryset = user_queryset.filter(isRepeater=True)
            else:
                user_queryset = user_queryset.filter(isRepeater=False)

            subject = student_events.first().subject
            if subject == 'English':
                user_queryset = user_queryset.filter(english_category__name__in=['R', 'S', 'T'])
            elif subject == 'Math':
                user_queryset = user_queryset.filter(math_category__name__in=['R', 'S', 'T'])

            target_test_date = student_events.first().target_test_date
            print("test_date==>",target_test_date)
            if target_test_date:
                student_ids_with_target_date = StudentAvailability.objects.filter(
                    Q(target_test_date_1=target_test_date) |
                    Q(target_test_date_2=target_test_date) |
                    Q(target_test_date_3=target_test_date) |
                    Q(target_test_date_4=target_test_date)
                ).values_list('student', flat=True).distinct()
                user_queryset = user_queryset.filter(id__in=student_ids_with_target_date)
                print("user_queryset==========>",user_queryset)

            results = []
            category_counts = {category: 0 for category in ['R', 'S', 'T']}

            for user in user_queryset:
                user_group_event_status=student_events.filter(student=user).first().is_sso_verified
                categories_matched = []
                if subject == 'English_Reading' or subject == 'English_Writing' or subject == 'English' and hasattr(user, 'english_category') and user.english_category.name in ['R', 'S', 'T']:
                    categories_matched.append(user.english_category.name)
                    print("categories_matched==>",categories_matched)
                elif subject == 'Math' and hasattr(user, 'math_category') and user.math_category.name in ['R', 'S', 'T']:
                    categories_matched.append(user.math_category.name)

                if categories_matched:
                    user_info = UserMinimumSerializer(user).data
                    user_info['category'] = ', '.join(categories_matched)
                    user_info['subject'] = subject
                    user_info['is_sso_verified'] = user_group_event_status
                    results.append(user_info)
                    for category in categories_matched:
                        category_counts[category] += 1

            total_students = len(results)

            return Response({
                "success": True,
                "status": "success",
                "message": f"Filtered students for group ID: {group_id}",
                "results": results,
                "total_students": total_students,
                "category_counts": category_counts,
                "sso_id": sso_id,
                "group_subject": group_subject
            })
        except Exception as e:
            print("Exception=====>", e)
            return Response(
                {"success": False, "status": "error", "message": "Something went wrong"},
                status=500
            )


class ReportClassSerializer(serializers.ModelSerializer):
    class Meta:
        model = AppointmentReport
        fields = '__all__'

class ReportClassesViewSet(BaseViewset):

    def create(self, request, appointment_id):
        try:
            appointment = Appointments.objects.get(pk=appointment_id)
        except Appointments.DoesNotExist:
            return Response({'error': 'Invalid Appointment'}, status=status.HTTP_404_NOT_FOUND)
        
        is_student_joined = request.data.get('is_student_joined', False)
        is_tutor_joined = request.data.get('is_tutor_joined', False)

        try:
            appointment_report = AppointmentReport.objects.get(appointment=appointment)
            
            appointment_report.is_student_joined = is_student_joined or appointment_report.is_student_joined
            appointment_report.is_tutor_joined = is_tutor_joined or appointment_report.is_tutor_joined
            appointment_report.save()
            serializer = ReportClassSerializer(appointment_report)
            return Response({
                "success": True,
                "status": "success",
                "message": "Report for Appointment updated successfully",
                "results": serializer.data
            }, status=status.HTTP_200_OK)
        except AppointmentReport.DoesNotExist:

            appointment_report = AppointmentReport.objects.create(
                appointment=appointment,
                is_student_joined=is_student_joined,
                is_tutor_joined=is_tutor_joined
            )
            serializer = ReportClassSerializer(appointment_report)
            return Response({
                "success": True,
                "status": "success",
                "message": "Report for Appointment created successfully",
                "results": serializer.data
            }, status=status.HTTP_201_CREATED)  
        

# class StudentJourneySerializer(serializers.ModelSerializer):
#     class Meta:
#         model = StudentJourney
#         fields = '__all__'
        
# class StudentJourneyViewSet(BaseViewset):

    # def get_student_journey(self, request, student_id):
    #     student = StudentJourney.objects.filter(student_id=student_id)
    #     serializer = StudentJourneySerializer(student, many=True)
    #     return Response({
    #             "success": True,
    #             "status": "success",
    #             "message": "Student Journey Report",
    #             "results": serializer.data
    #         }, status=status.HTTP_201_CREATED)  
    


    # def create_student_journey(self, request, student_id):
    #     try:
    #         user = User.objects.get(id=student_id)
    #         print("user==>",user)
    #     except User.DoesNotExist:
    #         return HttpResponse("User not found", status=404)
        
    #     # user = User.objects.get(id=student_id)
    #     # english_reading_tutors_assigned = user.english_reading_tutors.exits()

    #     english_reading_tutors_assigned = user.english_reading_tutors.exists()
    #     english_writing_tutors_assigned = user.english_writing_tutors.exists()
    #     math_tutors_assigned = user.math_tutors.exists()

    #     student_session_plans = StudentSessionPlan.objects.filter(student_id=student_id)

        

    #     for session_plan in student_session_plans:
    #         subject_name = session_plan.mega_domain.name
    #         completion_date = None 

    #         if subject_name == 'Reading' and english_reading_tutors_assigned:
    #             # english_reading_assigned = True

    #             related_assignments = StudentAssignment.objects.filter(
    #                 student_id=student_id,
    #                 megadomain=session_plan.mega_domain,
    #                 type='HOME',
    #                 is_completed=False
    #             )

    #             english_reading_session_completed = not related_assignments.exists()
    #             if english_reading_session_completed:
    #                 completion_date = datetime.now().date()

    #         elif subject_name == 'Writing' and english_writing_tutors_assigned:
    #             # english_writing_assigned = True

    #             related_assignments = StudentAssignment.objects.filter(
    #                 student_id=student_id,
    #                 megadomain=session_plan.mega_domain,
    #                 type='HOME',
    #                 is_completed=False
    #             )
    #             english_writing_session_completed = not related_assignments.exists()
    #             if english_writing_session_completed:
    #                 completion_date = datetime.now().date()

    #         elif subject_name == 'Math' and math_tutors_assigned:
    #             # math_assigned = True

    #             related_assignments = StudentAssignment.objects.filter(
    #                 student_id=student_id,
    #                 megadomain=session_plan.mega_domain,
    #                 type='HOME',
    #                 is_completed=False
    #             )

    #             math_session_completed = not related_assignments.exists()
    #             if math_session_completed:
    #                 completion_date = datetime.now().date()

    #         if completion_date:
    #             completion_date = completion_date

    #             journey, _ = StudentJourney.objects.get_or_create(
    #                 student=user,
    #                 subject=subject_name,
    #                 # class_type=class_type,  
    #                 defaults={'status': 'Completed', 'completion_date': completion_date}
    #             )
    #             if journey.status != 'Completed':
    #                 journey.status = 'Completed'
    #                 journey.save()
    #     return Response({
    #             "success": True,
    #             "status": "success",
    #             "message": "Student Journey Report"
    #         }, status=status.HTTP_201_CREATED)  

class CpeaOverRideViewSet(BaseViewset): #added after merger

    def cpea_override(self, request, student_id, mega_domains):
        is_completed = request.data.get('is_completed')
        print("is_completed==>", is_completed)
        mega_domain_names = mega_domains.split(',')
        mega_domain_objects = MegaDomain.objects.filter(name__in=mega_domain_names)        
        student_session_plans = StudentSessionPlan.objects.filter(student_id=student_id, mega_domain__in=mega_domain_objects)
        student_session_plans.update(is_completed=is_completed)
        
        serializer = StudentSessionPlanSerializer(student_session_plans, many=True)
        
        return Response({
            "success": True,
            "status": "success",
            "message": "Student session plans updated successfully.",
            "data": serializer.data
        }, status=status.HTTP_200_OK)
    
   
    

class UnattendedClassesViewSet(BaseViewset):  #added after merging

    def list(self, request):    
        appointment_id = request.query_params.get('appointment_id',None)
        action = request.query_params.get('action', None)

        if request.user.role.lower() == "sso_manager" or 'admin' or 'manager' or 'prep_manager':

            if appointment_id and action in ['cancel', 'reschedule']:
                try:
                    appointment = Appointments.objects.get(id=appointment_id)
                    appointment.status = 'CANCELLED' if action == 'cancel' else 'RESCHEDULED'
                    appointment.is_active = False
                    appointment.save()
                    return Response({"sucess":True,"status":"sucess","message":"class canceled or rescheduled sucessfully.."}, status=status.HTTP_201_CREATED)
                except Appointments.DoesNotExist:
                    return Response({"error": "Appointment not found"}, status=status.HTTP_404_NOT_FOUND)
        else:
            return Response({"error": "You do not have permission to cancel the class"}, status=status.HTTP_403_FORBIDDEN)
        

        
    def counters_of_all_classes(self, request):    
        student_id = request.query_params.get('student_id','None')

        if student_id:
            current_time = datetime.now()
            completed_classes = Appointments.objects.filter(
                                is_completed=True,
                                student_id=student_id,
                                type__in=['cpea', 'coreprep', 'group_class']
                            ).exclude(
                                Q(appointment_reports__is_student_joined=False) |
                                Q(status='CANCELLED') |
                                Q(status='RESCHEDULED')
                            ).count()
            
            scheduled_classes = Appointments.objects.filter(
                            start_at__gt=current_time,
                            is_completed=False,
                            student_id=student_id,
                            type__in=['cpea', 'coreprep', 'group_class']
                        ).exclude(
                            Q(appointment_reports__is_student_joined=False) |
                            Q(status='CANCELLED') |
                            Q(status='RESCHEDULED')
                        ).count()

            student_no_show_classes = AppointmentReport.objects.filter(
                is_student_joined=False,appointment__student_id=student_id).exclude(
                                        Q(appointment__status='CANCELLED') |
                                        Q(appointment__status='RESCHEDULED')).count()
            
            cancelled_class = Appointments.objects.filter(status = 'CANCELLED',student_id=student_id,type__in=['cpea', 'coreprep', 'group_class']).exclude(
            appointment_reports__is_student_joined=False).count()

            reschedule_class = Appointments.objects.filter(status = 'RESCHEDULED',student_id=student_id,type__in=['cpea', 'coreprep', 'group_class']).exclude(
            appointment_reports__is_student_joined=True).count()

            data = {"scheduled_classes": scheduled_classes,
                    "completed_classes": completed_classes,
                    "no_show_classes": student_no_show_classes,
                    "canceled_classes":cancelled_class,
                    "reschedule_classes":reschedule_class,
                    #"unattended classes":unattended_classes,
                    }       
            return Response({
                "success": True,
                "status": "success",
                "message": "Class counters retrieved successfully",
                "results": data
            }, status=status.HTTP_200_OK)
                    



        
        
    
    