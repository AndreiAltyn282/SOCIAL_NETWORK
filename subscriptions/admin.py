from django.contrib import admin
from .models import Subscription

@admin.register(Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    list_display = ['subscriber', 'target', 'created_at']
    list_filter = ['created_at']
    search_fields = ['subscriber__username', 'target__username']
    readonly_fields = ['created_at']
