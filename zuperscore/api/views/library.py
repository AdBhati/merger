from datetime import timezone
import requests
from rest_framework.response import Response
from rest_framework import viewsets
from rest_framework import status
from rest_framework.views import APIView
from rest_framework import serializers
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework import filters as rest_filters
from django_filters import rest_framework as filters
from zuperscore.db.models.conduct import TimeAnalytics
from zuperscore.db.models.library import FileAsset, TutorAvailability
from zuperscore.db.models.library import Settings
from .base import BaseSerializer, BaseViewset
import boto3
from requests.exceptions import HTTPError

class FileAssetSerializer(serializers.ModelSerializer):

    

    class Meta:
        model = FileAsset
        fields = ["id", "asset", "attributes", "context", "created_at", "updated_at"]


class FileAssetEndpoint(APIView):

    parser_classes = (MultiPartParser, FormParser)

    """
    A viewset for viewing and editing task instances.
    """

    def get(self, request):
        files = FileAsset.objects.all()
        serializer = FileAssetSerializer(files, context={"request": request}, many=True)
        return Response(serializer.data)

    def post(self, request, *args, **kwargs):
        serializer = FileAssetSerializer(data=request.data)
        try:
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_201_CREATED)
        except Exception as e:
            print("Exception ====> ", e)
            return Response(
                {"success": False, "error": "Something went wrong"},
                status=status.HTTP_400_BAD_REQUEST,
            )


class SettingsSerializer(BaseSerializer):
    class Meta:
        model = Settings
        fields = ["disabled_mistake_analyzer"]

class SettingsViewSet(BaseViewset):
    serializer_class = SettingsSerializer
    model = Settings

    def list(self, request):
        serializer = SettingsSerializer(
            Settings.objects.all(), many=True
        )
        return Response(serializer.data)
    
class TimeZoneViewSet(BaseViewset):

    def convert_time_zone(self, request):
        from_time_zone = request.data.get('fromTimeZone')
        date_time = request.data.get('dateTime')
        to_time_zone = request.data.get('toTimeZone')
        dst_ambiguity = request.data.get('dstAmbiguity', "")  
        url = 'https://timeapi.io/api/Conversion/ConvertTimeZone'
        headers = {'Content-Type': 'application/json'}
        payload = {
            "fromTimeZone": from_time_zone,
            "dateTime": date_time,
            "toTimeZone": to_time_zone,
            "dstAmbiguity": dst_ambiguity
        }
        try:
            response = requests.post(url, json=payload, headers=headers)
            return Response(response.json(), status=status.HTTP_200_OK)
        except HTTPError as http_err:
            return Response({'error': str(http_err)}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as err:
            return Response({'error': str(err)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        

class TimeAnalyticsSerializer(serializers.ModelSerializer):
    class Meta:
        model = TimeAnalytics
        fields = "__all__"
    
class TimeAnalyticsViewSet(BaseViewset):
    serializer_class = TimeAnalyticsSerializer
    model = TimeAnalytics

    def list(self, request):
        serializer = TimeAnalyticsSerializer(TimeAnalytics.objects.all(), many=True)
        return Response(serializer.data)
    

class TutorAvailabilitySerializer(BaseSerializer):
    class Meta:
        model = TutorAvailability
        fields = "__all__"
    

# class TutorAvailabilityViewSet(BaseViewset):
#     def post(self, request, tutor_id):
#         slots = request.data.get("slots")
#         tutor_availability = TutorAvailability.objects.create(tutor_id=tutor_id, slot=slots)
        
#         # Calculate total_month_supply based on the slots 
#         tutor_availability.total_month_supply = (slots * 60 * 21) / 60
#         tutor_availability.save()

#         serializer = TutorAvailabilitySerializer(tutor_availability)
#         return Response(serializer.data, status=status.HTTP_200_OK)
    









    
# class TargetTestDateSerializer(BaseSerializer):
#     class Meta:
#         model = TargetTestDate
#         fields = "__all__"

# class AllTargetTestDate(BaseViewset):
#     def list(self, request):

#         current_date = timezone.now().date()

#         student_target_test_date = TargetTestDate.objects.filter(date__gt=current_date)
        
#         serializer = TargetTestDateSerializer(student_target_test_date, many=True)

#         return Response({
#                 "success": True,
#                 "status": "success",
#                 "message": "Target_test_date get successfully..",
#                 "results": serializer.data
#             }, status=status.HTTP_200_OK)
