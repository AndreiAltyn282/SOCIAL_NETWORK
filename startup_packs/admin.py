from django.contrib import admin
from .models import StartupPack, UserStartupPack, StartupPackSource, PackPost

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


@admin.register(StartupPackSource)
class StartupPackSourceAdmin(admin.ModelAdmin):
    list_display = ['pack', 'name', 'is_active', 'last_fetched']
    list_filter = ['is_active', 'pack']
    search_fields = ['name', 'rss_url']
    readonly_fields = ['last_fetched']


@admin.register(PackPost)
class PackPostAdmin(admin.ModelAdmin):
    list_display = ['pack', 'title', 'source_name', 'published_at', 'is_ai_generated']
    list_filter = ['pack', 'source_name', 'is_ai_generated']
    search_fields = ['title', 'content']
    readonly_fields = ['created_at']
