import json
from .serializers import EntrySerializer, BatchEntrySerializer
from core.models import Entry
from django.db import transaction
from django.utils.timezone import now
from rest_framework import generics, status, viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
import requests

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

class SubmitEntryView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            data = json.loads(request.body)
            tracking = data.get('tracking')
            numerical_value = data.get('numerical_value')
            string_value = data.get('string_value', None)

            if not tracking or numerical_value is None:
                return Response({'error': 'Tracking and numerical_value are required'}, status=400)

            Entry.objects.create(
                user=request.user,
                date=now(),
                tracking=tracking,
                numerical_value=numerical_value,
                string_value=string_value,
                source="fitcypher"
            )

            return Response({'message': 'Entry created successfully'}, status=201)

        except json.JSONDecodeError:
            return Response({'error': 'Invalid JSON'}, status=400)

class TrackingDataView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, tracking_type):
        from collections import defaultdict
        from django.utils.timezone import localtime

        data = defaultdict(list)
        entries = Entry.objects.filter(user=request.user, tracking=tracking_type).order_by('date')

        for entry in entries:
            local_date = localtime(entry.date).strftime('%Y-%m-%d')
            data['labels'].append(local_date)
            data['values'].append(float(entry.numerical_value) if entry.numerical_value else None)

        return Response(data)

class EntryViewSet(viewsets.ModelViewSet):
    queryset = Entry.objects.all()
    serializer_class = EntrySerializer
    permission_classes = [IsAuthenticated]


# CARA_ENTRY_TYPE_MAPPING = {
#     'food': 'diet',
#     'stool': 'stool',
#     'workout': 'exercise',
#     # Add more mappings if needed
# }

# def get_bristol_text(numeral):
#     match numeral:
#         case 0:
#             return "no_stool"
#         case 14:
#             return "type1"
#         case 28:
#             return "type2"
#         case 42:
#             return "type3"
#         case 57:
#             return "type4"
#         case 71:
#             return "type5"
#         case 85:
#             return "type6"
#         case 100:
#             return "type7"


# # Download Cara Images

# image_folder = Path('ui', 'static', 'diet')


# def check_file_exists(file_path):
#     if os.path.exists(file_path):
#         print(f"The file '{file_path}' exists.")
#         return True
#     else:
#         print(f"The file '{file_path}' does not exist.")
#         return False

# def retrieve_image_id(url, headers, entry):
#     if entry["type"]=="food":
#         for mealItem in entry["mealItems"]:
#             if mealItem["hasImage"]:
#                 print(mealItem["realmIdString"])
#                 if not check_file_exists(Path(image_folder, mealItem["realmIdString"] + ".jpg")):
#                     download_image(url, headers, mealItem["realmIdString"])

# def download_image(url, headers, img_id):
#     url_image = "https://web.gohidoc.com/api/dashboard/me/images/"
#     food_img_file = Path(image_folder, img_id + ".jpg")
#     print(f"Attempting image download : {img_id}")
#     img_url_path = url_image + img_id + "/"
#     img_request = requests.get(img_url_path, headers=headers)
#     if img_request.status_code == 200:
#         img_data = img_request.content
#         with open(food_img_file, 'wb') as handler:
#             handler.write(img_data)
#         return True
#     else:
#         img_txt = Path(image_folder, img_id + ".txt")
#         file = open(img_txt,"w")
#         file.write("No image downloaded")
#         file.close()
#         return False

# @transaction.atomic
# def sync_cara_entries(request):
#     print("--- Syncing Cara Entries ---")

#     if not image_folder.exists():
#         image_folder.mkdir(parents=True, exist_ok=True)

#     user = request.user
#     cara_api_token = user.cara_api_token

#     if not cara_api_token:
#         print("No Cara token set in User Profile, skipping...")
#         # Handle case where user does not have a Cara API token
#         # You can redirect them to a page to input their token
#         return redirect('profile')

#     # Calculate start date and end date
#     end_date = datetime.date.today().strftime('%Y-%m-%d')
#     start_date = (datetime.date.today() - datetime.timedelta(days=180)).strftime('%Y-%m-%d')

#     # Make REST call to fetch Cara entries
#     url = f"https://web.gohidoc.com/api/dashboard/me/data-points/?start={start_date}&end={end_date}&limit=100&offset=0"
#     headers = {"x-token": cara_api_token}

#     try:
#         response = requests.get(url, headers=headers)
#         response.raise_for_status()  # Raise an error for unsuccessful status codes
#         data = response.json().get('results', [])
#         #sprint(json.dumps(data, indent=4))

#         # Save Cara entries into Entry model
#         for entry in data:
#             entry_type = entry['type']
#             group_name = CARA_ENTRY_TYPE_MAPPING.get(entry_type, entry_type)  # Use entry type if no mapping exists

#             # Get or create the ChecklistGroup instance
#             group, created = ChecklistGroup.objects.get_or_create(name=group_name.lower())
#             additional_information = ""
#             # Determine string_value based on entry type
#             if entry_type == "food":
#                 # Extract meal item name from mealItems
#                 meal_items = entry.get('mealItems', [])
#                 if meal_items:
#                     string_value = meal_items[0].get('name')
#                     for mealItem in entry["mealItems"]:
#                         if mealItem["hasImage"]:
#                             print(mealItem["realmIdString"])
#                             additional_information = mealItem["realmIdString"]
#                 else:
#                     string_value = None
#             elif entry_type == "stool":
#                 # Get Bristol text based on numerical value
#                 bristol_numeral = entry.get('value')
#                 string_value = get_bristol_text(bristol_numeral)
#             elif entry_type == "workout":
#                 # If the type is workout and text is null
#                 if entry.get('text') is None:
#                     # Set string_value to tags if tags is not None, otherwise set it to "workout"
#                     string_value = entry.get('tags') or "workout"
#                 else:
#                     # If text is not null, use it as string_value
#                     string_value = entry.get('text')
#             else:
#                 string_value = entry.get('text')

#             try:
#                 # Try to create the entry, but handle IntegrityError if it already exists
#                 with transaction.atomic():
#                     Entry.objects.create(
#                         user=user,
#                         date=entry['timestampEntry'],  # Use the timestampEntry from Cara's response
#                         string_value = string_value.lower() if string_value is not None else None,
#                         numerical_value=entry.get('value'),
#                         tags=entry.get('tags'),
#                         additional_information=additional_information,
#                         group=group,
#                         source="cara"
#                         # Add any other fields from the Cara response as needed
#                     )
#             except IntegrityError:
#                 # Handle case where the entry already exists (duplicate entry)
#                 pass

#         download_cara_meal_images = [retrieve_image_id(url, headers, x) for x in data]

#         # Redirect or render a page indicating successful sync
#         return redirect('profile')  # Redirect to the user's profile page
#     except requests.exceptions.RequestException as e:
#         # Handle error cases
#         print("Error:", e)
#         return redirect('error_page')  # Redirect to an error page