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
        data = serializer.validated_data

        # Convert string fields to lowercase
        if "tracking" in data:
            data["tracking"] = data["tracking"].lower()
        if "string_value" in data and data["string_value"]:
            data["string_value"] = data["string_value"].lower()
        if "notes" in data and data["notes"]:
            data["notes"] = data["notes"].lower()
        if "tags" in data and data["tags"]:
            data["tags"] = data["tags"].lower()
        if "source" in data and data["source"]:
            data["source"] = data["source"].lower()

        serializer.save(user=self.request.user, **data)
