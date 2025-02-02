from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import generics
from core.models import Entry
from .serializers import EntrySerializer
from rest_framework.permissions import IsAuthenticated

class EntryList(generics.ListCreateAPIView):
    queryset = Entry.objects.all()
    serializer_class = EntrySerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)