from django.contrib import admin
from .models import Entry

@admin.register(Entry)
class EntryAdmin(admin.ModelAdmin):
    list_display = ('user', 'date', 'tracking', 'string_value', 'numerical_value', 'notes', 'tags', 'source')
    search_fields = ('user__username', 'tracking', 'tags', 'source')
    list_filter = ('date', 'tracking', 'source')

