from rest_framework import serializers
from core.models import Entry
from django.contrib.auth.models import User

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username']

class EntrySerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)

    class Meta:
        model = Entry
        fields = ['id', 'user', 'date', 'tracking', 'string_value', 'numerical_value', 'notes', 'tags', 'source']