from rest_framework.exceptions import APIException
from rest_framework import serializers
from rest_framework import viewsets
from rest_framework import status

class BaseSerializer(serializers.ModelSerializer):
    pass

class BaseViewset(viewsets.ModelViewSet):
    def get_queryset(self):
        try:
            return self.model.objects.all()
        except Exception as e:
            print(e)
            raise APIException("Please check the view", status.HTTP_400_BAD_REQUEST)
