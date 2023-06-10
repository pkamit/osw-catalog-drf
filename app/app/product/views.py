from django.db.models import Prefetch, Q
from django.shortcuts import render

from drf_spectacular.utils import (
    extend_schema_view,
    extend_schema,
    OpenApiParameter,
    OpenApiTypes,
)

from django.db.models import Count
from app.product.forms import ProductNameFilterForm
from drf_spectacular.utils import extend_schema
from rest_framework.pagination import PageNumberPagination
from rest_framework.decorators import action
from rest_framework.viewsets import ViewSet
from rest_framework import viewsets
from rest_framework.response import Response
from .models import (
    Category,
    Brand,
    Product,
    ProductLine,
    ProductImage,
    Attribute,
    AttributeValue,
    ProductAttributeValue,
    ProductTypeAttribute,
    ProductType,
)
from .serializers import (
    CategorySerializer,
    ProductSerializer,
    ProductCategorySerializer,
    # ProductCategoryFilterSerializer,
    AttributeSerializer,
    # AttributeValueNewSerializer,
    # ProductTypeAttributeSerializer,
    # AttributeValueSerializer,

    # NewAttributeSerializer,

    # AttributeFilterSerializer,
    # FilterAttributeSerializer,
    FilterAttributeValueSerializer,

    ProductTypeAttributeSerializer,
)
from django_filters.rest_framework import DjangoFilterBackend


class StandardResultsSetPagination(PageNumberPagination):
    page_size = 1
    page_size_query_param = "page_size"
    max_page_size = 1000


def index(request):
    context = {
        "form": ProductNameFilterForm(),
        "products": Product.objects.all().is_active(),
    }
    return render(request, "index.html", context)


class CategoryViewSet(viewsets.ViewSet):
    """
    A simple viewset to see all categories
    """

    queryset = Category.objects.all().is_active()

    @extend_schema(responses=CategorySerializer)
    def list(self, request):
        serializer = CategorySerializer(self.queryset, many=True)
        return Response(serializer.data)

class ProductAttributesViewSet(viewsets.ModelViewSet):
    serializer_class = AttributeSerializer
    queryset = Attribute.objects.all()


@extend_schema_view(
    list=extend_schema(
        parameters=[
            OpenApiParameter(
                "slug",
                OpenApiTypes.STR,
                description="slug to filter",
            ),
            OpenApiParameter("pid", OpenApiTypes.STR, description="pid to filter"),
        ]
    )
)

class ProductAttributesValueViewSet(viewsets.ModelViewSet):
    serializer_class = FilterAttributeValueSerializer
    queryset = AttributeValue.objects.all()
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ["attribute"]

class ProductViewSet(viewsets.ModelViewSet):
    """
    A simple viewset to see all products
    """

    pagination_class = StandardResultsSetPagination
    queryset = Product.objects.all().is_active()
    lookup_field = "slug"

    def retrieve(self, request, slug=None):
        serializer = ProductSerializer(
            self.queryset.filter(slug=slug)
            .prefetch_related(Prefetch("attribute_value__attribute"))
            .prefetch_related(Prefetch("product_line__product_image"))
            .prefetch_related(Prefetch("product_line__attribute_value__attribute")),
            many=True,
        )
        return Response(serializer.data)

    # @extend_schema(responses=ProductSerializer)
    # def list(self, request):
    #     serializer = ProductSerializer(self.queryset, many=True)
    #     return Response(serializer.data)

    @action(
        methods=["get"],
        detail=False,
        url_path=r"category/(?P<slug>[\w-]+)",
    )
    def list_product_by_category(self, request, slug=None):
        queryset = self.get_queryset()
        print(queryset)
        serializer = ProductCategorySerializer(
            self.queryset.filter(category__slug=slug)
            .prefetch_related(
                Prefetch("product_line", queryset=ProductLine.objects.order_by("order"))
            )
            .prefetch_related(
                Prefetch(
                    "product_line__product_image",
                    queryset=ProductImage.objects.filter(order=1),
                )
            ),
            many=True,
        )
        return Response(serializer.data)

    @action(
        methods=["get"],
        detail=False,
        url_path=r"search/(?P<keyword>[\w-]+)",
    )
    def list_product_by_keyword(self, request, keyword=None):
        slug = self.request.query_params.get("slug")
        pid = self.request.query_params.get("pid")
        price = self.request.query_params.get("price")
        queryset = self.queryset
        if slug:
            # tag_ids = self._params_to_ints(tags)
            queryset = queryset.filter(slug=slug)
        if pid:
            # ingredients_ids =  self._params_to_ints(ingredients)
            queryset = queryset.filter(pid=pid)
        if price:
            queryset = queryset.filter(product_line__price__gt=price)
        # paginator = self.pagination_class()
        queryset = self.filter_queryset(
            queryset.filter(Q(name__icontains=keyword))
            .prefetch_related(
                Prefetch("product_line", queryset=ProductLine.objects.order_by("order"))
            )
            .prefetch_related(
                Prefetch(
                    "product_line__product_image",
                    queryset=ProductImage.objects.filter(order=1),
                )
            )
        )
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = ProductCategorySerializer(
                page,
                many=True,
            )
            return self.get_paginated_response(serializer.data)

        serializer = ProductCategorySerializer(
            queryset,
            many=True,
        )
        return Response(serializer.data)











    # @action(
    #     methods=["get"],
    #     detail=False,
    #     url_path=r"category_filters/(?P<keyword>[\w-]+)",
    # )
    # def list_product_by_category_filters(self, request, keyword=None):
    #     if keyword:
    #         queryset = Product.objects.filter(name__icontains=keyword)
    #         categories = queryset.values_list('category', flat=True)
    #         return Response(Category.objects.filter(id__in=categories))
    #         serializer = CategorySerializer(categories, many=True)

    #     else:
    #         return Response(CategorySerializer(categories, many=True))


class ProductNewViewSet(viewsets.ModelViewSet):
    serializer_class = ProductSerializer
    queryset = Product.objects.all()
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ["category", "product_line__price", "attribute_value"]


# class ProductAttributesViewSet(viewsets.ModelViewSet):
#     """
#     A simple viewset to see all categories
#     """

#     # queryset = AttributeValue.objects.all()

#     # @extend_schema(responses=AttributeValueSerializer)
#     # def list(self, request):
#     #     serializer = AttributeValueSerializer(self.queryset, many=True)
#     #     return Response(serializer.data)
#     serializer_class = ProductTypeAttributeSerializer
#     queryset = (
#         ProductTypeAttribute.objects.filter().prefetch_related(
#                 Prefetch(
#                     "attribute__product_image",
#                     queryset=ProductImage.objects.filter(order=1),
#                 )
#             )
#  #       .annotate(count=Count("attribute__id"))
#   #      .order_by("attribute__name")
#     )
#     filter_backends = [DjangoFilterBackend]
#     filterset_fields = ["attribute"]


# class ProductAttributesViewSet(viewsets.ViewSet):
#     serializer_class = AttributeValueSerializer
#     queryset = AttributeValue.objects.all()
#     filter_backends = [DjangoFilterBackend]
#     filterset_fields = ["attribute__name"]