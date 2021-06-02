from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse

from .models import *

from django_admin_listfilter_dropdown.filters import (
    DropdownFilter, ChoiceDropdownFilter, RelatedDropdownFilter
)

from .models import *

def linkify(field_name):
    def _linkify(obj):
        linked_obj = getattr(obj, field_name)
        if linked_obj is None:
            return '-'
        app_label = linked_obj._meta.app_label
        model_name = linked_obj._meta.model_name
        view_name = f'admin:{app_label}_{model_name}_change'
        link_url = reverse(view_name, args=[linked_obj.pk])
        return format_html('<a href="{}">{}</a>', link_url, linked_obj)

    _linkify.short_description = field_name  # Sets column name
    return _linkify


class GenericAdmin(admin.ModelAdmin):

    def __init__(self, model, admin_site):
        self.list_display = []
        for field in model._meta.fields:
            if field.is_relation:
                self.list_display.append(linkify(field.name))
            elif field.name != "id":
                self.list_display.append(field.name)
        self.list_filter = [(str(field.name), RelatedDropdownFilter) for field in model._meta.fields if 'target_field' in dir(field) ]
        
        self.search_fields = [field.name for field in model._meta.fields ] # if field.name != 'id']
        super(GenericAdmin, self).__init__(model, admin_site)

admin.site.register(StreamUsers,GenericAdmin)
admin.site.register(ChatMessages, GenericAdmin)
admin.site.register(TextCommands, GenericAdmin)
admin.site.register(CommandUse, GenericAdmin)
admin.site.register(FalseCommands, GenericAdmin)
admin.site.register(FeatureRequest, GenericAdmin)
admin.site.register(ChatRoom, GenericAdmin)
admin.site.register(RoomsToMonitor, GenericAdmin)