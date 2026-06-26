from django.contrib import admin
from .models import StartupPack, UserStartupPack

@admin.register(StartupPack)
class StartupPackAdmin(admin.ModelAdmin):
    list_display = ['name', 'subscribers_count', 'created_at']
    list_filter = ['created_at']
    search_fields = ['name', 'description']
    filter_horizontal = ['experts']
    readonly_fields = ['created_at', 'updated_at']

    def subscribers_count(self, obj):
        return obj.user_startup_packs.count()
    subscribers_count.short_description = 'Подписчиков'


@admin.register(UserStartupPack)
class UserStartupPackAdmin(admin.ModelAdmin):
    list_display = ['user', 'pack', 'subscribed_at']
    list_filter = ['subscribed_at']
    search_fields = ['user__username', 'pack__name']
    readonly_fields = ['subscribed_at']
