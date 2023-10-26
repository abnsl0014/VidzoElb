from django.http import HttpResponse
from rest_framework import serializers
# from django.core import serializers as core_serializers
from bharatMenuApp.models import City, Restaurant, MenuItem, Category, Order, OrderItems, Merchant, Profile, Query
from django.contrib.auth.models import User


class CitySerializer(serializers.ModelSerializer):
    class Meta:
        model = City
        fields = '__all__'


class RestaurantSerializer(serializers.ModelSerializer):
    # Pincode = serializers.PositiveIntegerField()
    # CityName = serializers.CharField()

    class Meta:
        model = Restaurant
        fields = '__all__'

    # def create(self, validated_data):
    #     CityName = validated_data.get('CityName')
    #     # city = validated_data.get('CityName')
    #     city_instance, created = City.objects.get_or_create(CityName=CityName)
    #     restaurant_instance = Restaurant.objects.create(
    #         **validated_data, CityName=city_instance)
    #     return restaurant_instance


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = '__all__'


class MenuItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = MenuItem
        fields = '__all__'


class OrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = '__all__'


class OrderItemsSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderItems
        fields = '__all__'


# User Serializer


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'password')
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        user = User(
            email=validated_data['email'],
            username=validated_data['username']
        )
        user.set_password(validated_data['password'])
        user.save()
        return user

# Register Serializer


class RegisterSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'password')
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        user = User.objects.create_user(
            validated_data['username'], validated_data['email'], validated_data['password'])

        return user


class MerchantSerializer(serializers.ModelSerializer):

    gst = serializers.CharField(
        required=False, allow_null=True, allow_blank=True)

    def validate_gst(self, value):
        if not value:
            return 0
        try:
            return int(value)
        except ValueError:
            raise serializers.ValidationError('You must supply an integer')

    CityName = serializers.CharField()
    Pincode = serializers.IntegerField()

    class Meta:
        model = Merchant
        fields = ['fullName', 'phoneNumber', 'email', 'ShopName', 'Address',
                  'CityName', 'Pincode', 'gst', 'password', 'userId', 'RestaurantId', 'ProfileId']
        # additional_fields = ['password', 'confirmPassword']
        # fields = '__all__'

        # extra_kwargs = {'password': {'write_only': True}}
        # exclude = ('CityName', 'Pincode')

    def create(self, validated_data):
        # pin = validated_data.pop('Pincode')
        # city_name = validated_data.pop('CityName')

        # if City.objects.filter(CityName=validated_data['CityName'], PinCode=validated_data['PinCode']).exists():
        #     city = City.objects.get(
        #         CityName=validated_data['CityName'], PinCode=validated_data['PinCode'])
        # else:
        #     city = City(**validated_data)
        #     city.save()

        # print(pin)
        # print(city_name)

        # Try to create a user if not existing
        # print(User.objects.get(username=validated_data.get('phoneNumber')))
        try:
            User.objects.get(username=validated_data.get('phoneNumber'))
            return HttpResponse("Username used already")
        except:

            user_instance = User.objects.create_user(
                username=validated_data.get('phoneNumber'), email=validated_data.get('email'), password=validated_data.get('password'))
            # user_instance.set_password(validated_data.get('password'))
            # print(validated_data.get('phoneNumber'))
            # print(validated_data.get('password'))

            profile_instance = Profile.objects.create(
                phoneNumber=validated_data.get('phoneNumber'), fullName=validated_data.get('fullName'), email=validated_data.get('email'))

            print(profile_instance)

            city, created = City.objects.get_or_create(
                CityName=validated_data.get('CityName'), Pincode=validated_data.get('Pincode'))

            print(city)

            restaurant_instance = Restaurant.objects.create(
                ShopName=validated_data.get('ShopName'), Address=validated_data.get('Address'), CityName=city)

            print(restaurant_instance)

            # user_serializer = UserSerializer(data=validated_data)

            # user_instance

            # if user_serializer.is_valid():
            #     user_instance = user_serializer.save()
            #     merchant_instance = Merchant.objects.create(
            #         ShopName=validated_data.get('ShopName'), fullName=validated_data.get('fullName'), Address=validated_data.get('Address'), phoneNumber=validated_data.get('phoneNumber'), email=validated_data.get('email'), gst=validated_data.get('gst'), CityName=validated_data.get('CityName'), Pincode=validated_data.get('Pincode'), userId=user_instance, RestaurantId=restaurant_instance, ProfileId=profile_instance)
            #     return merchant_instance

            # user_instance.save()

            merchant_instance = Merchant.objects.create(
                ShopName=validated_data.get('ShopName'), fullName=validated_data.get('fullName'), Address=validated_data.get('Address'), phoneNumber=validated_data.get('phoneNumber'), email=validated_data.get('email'), password=validated_data.get('password'), gst=validated_data.get('gst'), CityName=validated_data.get('CityName'), Pincode=validated_data.get('Pincode'), userId=user_instance, RestaurantId=restaurant_instance, ProfileId=profile_instance)
            return merchant_instance


class ProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = Profile
        fields = '__all__'


class QuerySerializer(serializers.ModelSerializer):

    phoneNumber = serializers.CharField(allow_blank=True, required=False)

    class Meta:
        model = Query
        fields = '__all__'
        # fields = ['QueryId', 'profileId', 'queryType', 'query', 'businessName', 'VideoAd',
        #           'TextAd', 'businessType', 'businessUrl', 'socialMediaUrl', 'status']
        # extra_kwargs = {'phoneNumber': {'write_only': True}}

    # def validate_phoneNumber(self, value):
    #     if value and len(value) > 0:
    #         raise serializers.ValidationError('Spam')
    #     return value

    def create(self, validated_data):

        profile_instance, created = Profile.objects.get_or_create(
            phoneNumber=validated_data['phoneNumber'])

        validated_data.pop('phoneNumber')

        query_instance = Query.objects.create(
            **validated_data,
            profileId=profile_instance
        )

        return query_instance


class QuerySerializerReadOnly(serializers.ModelSerializer):

    class Meta:
        model = Query
        fields = '__all__'
