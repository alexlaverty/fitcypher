import json
from .serializers import EntrySerializer, BatchEntrySerializer
from core.models import Entry
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from rest_framework import generics
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from django.utils.timezone import now


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

class BatchEntryImport(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        # Transform the incoming data to match the expected format
        transformed_data = {
            'entries': []
        }

        for entry_data in request.data:
            # Remove the nested user object and any existing ID
            entry_data.pop('user', None)
            entry_data.pop('id', None)
            transformed_data['entries'].append(entry_data)

        serializer = BatchEntrySerializer(data=transformed_data)

        if serializer.is_valid():
            try:
                with transaction.atomic():
                    entries = []
                    for entry_data in transformed_data['entries']:
                        # Convert string fields to lowercase
                        for field in ['tracking', 'string_value', 'notes', 'tags', 'source']:
                            if entry_data.get(field):
                                entry_data[field] = entry_data[field].lower()

                        entry = Entry.objects.create(
                            user=request.user,
                            **entry_data
                        )
                        entries.append(entry)

                    response_serializer = EntrySerializer(entries, many=True)
                    return Response(response_serializer.data, status=status.HTTP_201_CREATED)

            except Exception as e:
                return Response(
                    {'error': f'Error creating entries: {str(e)}'},
                    status=status.HTTP_400_BAD_REQUEST
                )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@csrf_exempt
@login_required
def api_submit_entry(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            tracking = data.get('tracking')
            numerical_value = data.get('numerical_value')
            string_value = data.get('string_value', None)

            if not tracking or numerical_value is None:
                return JsonResponse({'error': 'Tracking and numerical_value are required'}, status=400)

            Entry.objects.create(
                user=request.user,
                date=now(),
                tracking=tracking,
                numerical_value=numerical_value,
                string_value=string_value,
                source="fitcypher"
            )

            return JsonResponse({'message': 'Entry created successfully'}, status=201)

        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON'}, status=400)

    return JsonResponse({'error': 'Only POST requests allowed'}, status=405)

@csrf_exempt
@login_required
def api_get_tracking_data(request, tracking_type):
    from collections import defaultdict
    from django.utils.timezone import localtime

    data = defaultdict(list)
    entries = Entry.objects.filter(user=request.user, tracking=tracking_type).order_by('date')

    for entry in entries:
        local_date = localtime(entry.date).strftime('%Y-%m-%d')
        data['labels'].append(local_date)
        data['values'].append(float(entry.numerical_value) if entry.numerical_value else None)

    return JsonResponse(data, safe=False)