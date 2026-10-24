from rest_framework.routers import DefaultRouter
from .views import PostViewSet, CategoryViewSet
router = DefaultRouter()
router.register('posts', PostViewSet, basename='api-post')
router.register('categories', CategoryViewSet, basename='api-category')
urlpatterns = router.urls
