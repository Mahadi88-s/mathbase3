from rest_framework import serializers
from .models import QuestionP2, QuestionP1, QuestionP3

class Paper1serializer(serializers.ModelSerializer):
    class Meta:
        model = QuestionP1
        fields = ['number','year','topic','marks','img']

class Paper2serializer(serializers.ModelSerializer):
    class Meta:
        model = QuestionP2
        fields = ['number','year','topic','marks','img']

class Paper3serializer(serializers.ModelSerializer):
    class Meta:
        model = QuestionP3
        fields = ['number','year','topic','marks','img']