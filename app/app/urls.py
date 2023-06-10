
from django.contrib import admin
from django.urls import path , include
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView
from rest_framework.routers import DefaultRouter
from app.product import views

router = DefaultRouter()
router.register(r"category", views.CategoryViewSet)
router.register(r"product", views.ProductViewSet)
router.register(r"product-new", views.ProductNewViewSet)
router.register(r"attribute-values", views.ProductAttributesValueViewSet)
router.register(r"attribute", views.ProductAttributesViewSet)

urlpatterns = [
    path('index/', views.index, name='index'),
    path('admin/', admin.site.urls),
    path('api/' , include(router.urls)),
    path("api/schema/", SpectacularAPIView.as_view(), name="schema"),
    path("api/schema/docs/", SpectacularSwaggerView.as_view(url_name="schema")),
   # path('category/<str:category>/custom-action/', ProductViewSet.list_product_by_category, name='list_product_by_category'),
]
