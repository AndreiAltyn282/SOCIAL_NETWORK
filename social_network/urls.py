from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

# Импорты твоих ViewSets
from users.views import UserViewSet
from posts.views import PostViewSet, CommentViewSet
from messages_app.views import ConversationViewSet, MessageViewSet
from subscriptions.views import SubscriptionViewSet
from startup_packs.views import StartupPackViewSet, PackPostViewSet
from notifications.views import NotificationViewSet

# Импорт из core
from core.views import index

router = DefaultRouter()
router.register(r'users', UserViewSet)
router.register(r'posts', PostViewSet)
router.register(r'comments', CommentViewSet)
router.register(r'conversations', ConversationViewSet)
router.register(r'messages', MessageViewSet)
router.register(r'subscriptions', SubscriptionViewSet)
router.register(r'startup-packs', StartupPackViewSet)
router.register(r'pack-posts', PackPostViewSet)
router.register(r'notifications', NotificationViewSet)

urlpatterns = [
    path('', index, name='index'),
    path('admin/', admin.site.urls),
    path('api/', include(router.urls)),
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
]

# Раздача медиафайлов в режиме разработки
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
