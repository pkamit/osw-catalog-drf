from rest_framework import serializers
from .models import (
    Brand,
    Category,
    Product,
    ProductLine,
    ProductImage,
    Attribute,
    AttributeValue,
    ProductType,
    ProductTypeAttribute,
    ProductLineAttributeValue,
    ProductAttributeValue
)


class CategorySerializer(serializers.ModelSerializer):
    category = serializers.CharField(source="name")

    class Meta:
        model = Category
        fields = ["category", "slug" ,"id"]
        # exclude = ("id",)


class BrandSerializer(serializers.ModelSerializer):
    class Meta:
        model = Brand
        # fields = "__all__"
        exclude = ("id",)


class ProductImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductImage
        exclude = (
            "id",
            "product_line",
        )


class ProductLineCategorySerializer(serializers.ModelSerializer):
    product_image = ProductImageSerializer(many=True)

    class Meta:
        model = ProductLine
        fields = ("price", "product_image")


class ProductCategorySerializer(serializers.ModelSerializer):
    product_line = ProductLineCategorySerializer(many=True)

    class Meta:
        model = Product
        fields = ("name", "slug", "pid",  "created_at", "product_line")


    def to_representation(self, instance):
        data = super().to_representation(instance)
        x = data.pop("product_line")

        if x:
            price = x[0]["price"]
            image = x[0]["product_image"]
            data.update({"price": price})
            data.update({"image": image})

        return data
class AttributeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Attribute
        fields = (
            "name",
            "id",
        )


class AttributeValueSerializer(serializers.ModelSerializer):
    attribute = AttributeSerializer(many=False)

    class Meta:
        model = AttributeValue
        fields = (
            "attribute",
            "attribute_value",
            #"id"

        )


class ProductLineSerializer(serializers.ModelSerializer):
    product_image = ProductImageSerializer(many=True)
    attribute_value = AttributeValueSerializer(many=True)

    class Meta:
        model = ProductLine
        # fields = "__all__"
        fields = [
            "price",
            "sku",
            "stock_qty",
            "order",
            "product_image",
            "attribute_value",
        ]

    def to_representation(self, instance):
        data = super().to_representation(instance)
        av_data = data.pop("attribute_value")
        attr_values = {}
        for key in av_data:
            attr_values.update({key["attribute"]["name"]: key["attribute_value"]})
        data.update({"specification": attr_values})
        return data


class ProductSerializer(serializers.ModelSerializer):
    # brand = BrandSerializer()
    category = CategorySerializer()
    product_line = ProductLineSerializer(many=True)
    attribute_value = AttributeValueSerializer(many=True)

    class Meta:
        model = Product
        fields = (
            "name",
            "slug",
            "description",
            "product_line",
            "attribute_value",
            "category"

        )

    def to_representation(self, instance):
        data = super().to_representation(instance)
        av_data = data.pop("attribute_value")
        attr_values = {}
        for key in av_data:
            attr_values.update({key["attribute"]["name"]: key["attribute_value"]})
        data.update({"attribute": attr_values})

        return data

class ProductCategoryFilterSerializer(serializers.ModelSerializer):
    # brand = BrandSerializer()
  #  category = ProductSerializer()
   # product_line = ProductLineSerializer(many=True)
   # attribute_value = AttributeValueSerializer(many=True)

    class Meta:
        model = Category
        fields = (
            "__all__",


        )

class AttributeValueNewSerializer(serializers.ModelSerializer):
    attribute = AttributeSerializer(many=False)

    class Meta:
        model = AttributeValue
        fields = (
            "attribute",
            "attribute_value",

        )
    def to_representation(self, instance):
        data = super().to_representation(instance)
        av_data = data.pop("attribute")

        attr_values = {}
        for key in av_data:
            #attr_values.update({key["attribute"]["name"]: key["attribute_value"]})
            print(key)
        data.update({"specification": av_data})
        return data

""""""
class FilterAttributeValueSerializer(serializers.ModelSerializer):
    attribute = AttributeSerializer(many=False)
    class Meta:
        model = AttributeValue
        fields = '__all__'
    def to_representation(self, instance):
        data = super().to_representation(instance)
        av_data = data.pop("attribute")
        id = data.pop("id")
        data['attribute_value_id'] = id
        return data


class NewAttributeSerializer(serializers.ModelSerializer):
    attribute_values = AttributeValueSerializer(many=True)

    class Meta:
        model = Attribute
        fields = '__all__'


class ProductAttributeSerializer(serializers.ModelSerializer):
    attribute = NewAttributeSerializer()

    class Meta:
        model = ProductAttributeValue
        fields = '__all__'



class ProductTypeAttributeSerializer(serializers.ModelSerializer):
    #attribute = AttributeSerializer(many=False)
    #attribute_value = AttributeValueSerializer(many=True)
    class Meta:
        model = ProductTypeAttribute
        fields = ['attribute' , ]




class AttributeFilterSerializer(serializers.Serializer):
    search_term = serializers.CharField(required=False)
    attribute_name = serializers.CharField(required=False)

    def filter_queryset(self, queryset):

        attribute_name = self.validated_data.get('attribute_name')

        if attribute_name:
            queryset = queryset.prefetch_related('attribute_values')

            queryset = queryset.filter(
                attribute_values__attribute__name=attribute_name,
               # attribute_values__value__icontains=search_term
            )

        return queryset

class FilterAttributeSerializer(serializers.ModelSerializer):
    attribute_values = AttributeValueSerializer(many=True)

    class Meta:
        model = Attribute
        fields = ['id', 'name', 'attribute_values']