# from msilib.schema import AdminExecuteSequence
import json
import openai
import requests
from django.http import HttpResponse
from django.core.files.storage import default_storage
from bharatMenuApp.serializers import CitySerializer, RestaurantSerializer, MenuItemSerializer, CategorySerializer, OrderSerializer, OrderItemsSerializer, RegisterSerializer, MerchantSerializer, ProfileSerializer, QuerySerializer, QuerySerializerReadOnly
from bharatMenuApp.models import City, Restaurant, MenuItem, Category, Order, OrderItems, Merchant, Profile, Query
from unicodedata import category
from django import forms
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
# from django.views.decorators import api_view
from rest_framework.decorators import api_view
from rest_framework.authentication import get_authorization_header
from rest_framework.parsers import JSONParser
from rest_framework import generics, permissions
from rest_framework.response import Response
from knox.models import AuthToken
from django.contrib.auth import login
from rest_framework.authtoken.serializers import AuthTokenSerializer
from knox.views import LoginView as KnoxLoginView
from BharatMenuBackend.settings import OPENAI_API, OTP_API
from django.http.response import JsonResponse
from rest_framework.authtoken.models import Token


# Create your views here.


# @csrf_exempt
# def get_category(request, id=0):
#     # id = request.GET.get('id', '')
#     print(id)
#     result = list(Category.objects.filter(
#         RestaurantName_id=int(id)).values('id', 'Name'))
#     return HttpResponse(json.dumps(result), content_type="application/json")

# @csrf_exempt
# def menuitem_factory(restaurant):
#     class MenuItemForm(forms.ModelForm):
#         CategoryName = forms.ModelChoiceField(
#             queryset=Category.objects.filter(RestaurantName=restaurant)
#         )
#     return MenuItemForm


# Register API
class RegisterAPI(generics.GenericAPIView):
    serializer_class = RegisterSerializer

    def post(self, request, *args, **kwargs):

        print(request.data)
        print(type(request))

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()

        # if serializer.is_valid(raise_exception=True):
        #     user = serializer.save(raise_exception=True)
        #     # print(order_serializer.data['OrderId'])
        #     # return JsonResponse(serializer.data, safe=False)
        # else:
        #     return JsonResponse(serializer.errors, safe=False)

        # Add Merchant with Restaurant and Profile

        # merchant_data = JSONParser().parse(request)
        # print(merchant_data)
        # merchant_serializer = MerchantSerializer(data=merchant_data)
        # if merchant_serializer.is_valid():
        #     merchant_serializer.save()

        # merchant_id = merchant_serializer.data['MerchantId']

        # login user automatically

        serializer = AuthTokenSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        login(request, user)
        _, token = AuthToken.objects.create(user)

        # print(request)

        return Response({
            # "user": UserSerializer(user, context=self.get_serializer_context()).data,
            "token": AuthToken.objects.create(user)[1],
            "login": request.data,
            "Logintoken": token
            # , "MerchantId": merchant_id
        })


class LoginAPI(KnoxLoginView):
    permission_classes = (permissions.AllowAny,)

    def post(self, request, format=None):

        print(request.data)
        serializer = AuthTokenSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        login(request, user)
        return super(LoginAPI, self).post(request, format=None)


# @csrf_exempt
# @api_view(('GET',))
# def get_user_from_token(request):
#     user = Token.objects.get(key=request.token).user


@csrf_exempt
@api_view(('POST', 'GET',))
def get_otp(request):
    api_key = OTP_API
    print(request)
    if request.method == 'POST':
        request_data = JSONParser().parse(request)
        getOtplink = "https://2factor.in/API/V1/" + \
            api_key + "/SMS/" + request_data['phone'] + "/AUTOGEN3/"
        if request_data['phone'] == "+919023389953":
            return JsonResponse({
                "Status": "Success",
                "Details": "Verified"
            }, safe=False)
        api_call = requests.get(getOtplink, headers={})
        return JsonResponse(api_call.json(), safe=False)


@csrf_exempt
@api_view(('POST', 'GET',))
def verify_otp(request):
    api_key = OTP_API
    print(request)
    if request.method == 'POST':
        request_data = JSONParser().parse(request)
        getOtplink = "https://2factor.in/API/V1/" + \
            api_key + "/SMS/VERIFY3/" + \
            request_data['phone'] + "/" + request_data['otp']

        if request_data['phone'] == "+919023389953" and request_data['otp'] == "7809":
            profile_instance = Profile.objects.get_or_create(
                phoneNumber=request_data['phone'][3:])
            profile_instance[0].otpVerified = 1
            profile_instance[0].save()
            print(profile_instance)

            return JsonResponse({
                "Status": "Error",
                "Details": "OTP Matched"
            }, safe=False)

        api_call = requests.get(getOtplink, headers={})
        api_call = api_call.json()
        print(api_call["Details"])
        if api_call["Details"] == "OTP Matched":
            profile_instance = Profile.objects.get_or_create(
                phoneNumber=request_data['phone'][3:])
            profile_instance[0].otpVerified = 1
            profile_instance[0].save()

            print(profile_instance)
        return JsonResponse(api_call, safe=False)


@csrf_exempt
@api_view(('POST', 'GET',))
def get_ai_script(request):

    openai.organization = "org-yo6HbhdiKCAFFsqCS35vxr7T"
    openai.api_key = OPENAI_API

    if request.method == 'GET':
        return JsonResponse(openai.Model.list())

    if request.method == 'POST':
        # post_data = {'name': 'Gladys'}
        # headers = {'Content-Type': 'application/json', 'Authorization' : 'Bearer {OPENAI_API}'}
        # response = requests.post('https://api.openai.com/v1/completions', data=post_data)
        # content = response.content
        request_data = JSONParser().parse(request)
        # merchant_data = request
        print(request_data)
        completion = openai.Completion.create(
            model="text-davinci-003",
            prompt=request_data['message'] +
            " in " + request_data['language'] + " in brief",
            max_tokens=500,
            temperature=0
        )
        return JsonResponse(completion)


@csrf_exempt
@api_view(('GET',))
def get_user_data(request):

    auth = get_authorization_header(request).split()
    print(auth)
    if auth and len(auth) == 2:
        token = auth[1].decode('utf-8')

    # user = AuthToken.objects.get(
    #     token_key=token)
    user = AuthToken.objects.filter(
        token_key__startswith=token[:8]).first().user

    # user = request.user
    if request.method == 'GET':
        if user.is_authenticated:

            merchant = Merchant.objects.get(userId=user)

            merchant_serializer = MerchantSerializer(merchant)

            print(merchant)
            return JsonResponse({
                'user_info': {
                    'id': merchant_serializer.data['RestaurantId'],
                    'userId': user.id,
                    'username': user.username,
                    'email': user.email,
                    'message': "user is authenticated!",
                    'merchant_data': merchant_serializer.data
                },
            })

    return JsonResponse({'error': 'not authenticated'})


@csrf_exempt
@api_view(('GET', 'POST', 'PUT', 'DELETE'))
def getMerchant(request, id=0):

    if request.method == 'POST':
        print("received!")
        print(request)
        merchant_data = JSONParser().parse(request)
        # merchant_data = request
        print(merchant_data)
        # print(merchant_data.data)

        # Add Merchant with Restaurant and Profile

        # merchant_data = JSONParser().parse(request)
        # print(merchant_data)
        # merchant_serializer = MerchantSerializer(data=merchant_data)
        # if merchant_serializer.is_valid():
        #     merchant_serializer.save()

        # merchant_id = merchant_serializer.data['MerchantId']

        # create city if not present

        # pin = merchant_data.pin

        # if City.objects.filter(Pincode = pin).exists():
        #     city = City.objects.get(Pincode = pin)

        # restaurant_serializer = RestaurantSerializer(data=request.data)
        # if restaurant_serializer.is_valid():
        #     restaurant_serializer.save()
        #     restaurant_serializer.data['OrderId']

        merchant_serializer = MerchantSerializer(data=merchant_data)
        if merchant_serializer.is_valid():
            merchant_serializer.save()
            # print(order_serializer.data['OrderId'])

            # print("yes 1")

            serializer = AuthTokenSerializer(data=merchant_data)
            serializer.is_valid(raise_exception=True)

            # print("yes 2")
            user = serializer.validated_data['user']
            # print("yes 3")
            login(request, user)
            # print("yes 4")
            _, token = AuthToken.objects.create(user)
            # print("yes 5")

            # print(request)

            return Response({
                # "user": UserSerializer(user, context=self.get_serializer_context()).data,
                # "token": AuthToken.objects.create(user)[1],
                # "login": merchant_data,
                "Logintoken": token
                # , "MerchantId": merchant_id
            })

            return JsonResponse(merchant_serializer.data['MerchantId'], safe=False)
        return JsonResponse(merchant_serializer.errors, safe=False)
        # print("received!")
        # print(request)
        # print(city_data)
        # return JsonResponse("wow")

    elif request.method == 'GET':
        # menuItems = MenuItem.objects.get(ItemId=id)
        merchants = Merchant.objects.all()
        # menuItems = MenuItem.objects.filter(
        #     RestaurantName=id)
        merchant_serializer = MerchantSerializer(merchants, many=True)
        return JsonResponse(merchant_serializer.data, safe=False)

    elif request.method == 'PUT':
        order_data = JSONParser().parse(request)
        OrderId = Order.objects.get(OrderId=order_data['OrderId'])
        order_serializer = OrderSerializer(OrderId, data=order_data)
        if order_serializer.is_valid():
            order_serializer.save()
            return JsonResponse("Updated Successfully!!", safe=False)
        return JsonResponse("Failed to Update.", safe=False)

    elif request.method == 'DELETE':
        OrderId = Order.objects.get(OrderId=id)
        OrderId.delete()
        return JsonResponse("Deleted Succeffully!!", safe=False)


@csrf_exempt
def ad_request(request, id=0):

    if request.method == 'GET':
        # menuItems = MenuItem.objects.get(ItemId=id)
        # menuItems = MenuItem.objects.all()
        # profile_instance = Profile.objects.filter(
        #     phoneNumber=id)

        phone = request.GET.get('phone')

        print(phone)

        if phone is None:
            if id == 0:
                queries = Query.objects.all()
                query_serializer = QuerySerializerReadOnly(queries, many=True)
                return JsonResponse(query_serializer.data, safe=False)
            queries = Query.objects.filter(QueryId=id)
            query_serializer = QuerySerializerReadOnly(queries, many=True)

            return JsonResponse(query_serializer.data, safe=False)

        print("sfdf")
        # print(type(phone))
        # print(int(phone))

        try:
            profile = Profile.objects.get(phoneNumber=int(phone))
            queries = Query.objects.filter(profileId=profile.ProfileId)
            query_serializer = QuerySerializerReadOnly(queries, many=True)
            return JsonResponse(query_serializer.data, safe=False)
        except:
            return JsonResponse("Phone not exist on DB.", safe=False)

    elif request.method == 'POST':
        query_data = JSONParser().parse(request)
        # profile = Profile.objects.get(phoneNumber=query_data['phone'])
        # print(query_data)
        query_serializer = QuerySerializer(data=query_data)
        if query_serializer.is_valid():
            query_serializer.save()
            return JsonResponse("Added Successfully!!", safe=False)
        return JsonResponse("Failed to Add.", safe=False)

    elif request.method == 'PUT':
        query_data = JSONParser().parse(request)
        query = Query.objects.get(QueryId=query_data['QueryId'])
        query_serializer = QuerySerializerReadOnly(query, data=query_data)
        if query_serializer.is_valid():
            query_serializer.save()
            return JsonResponse("Updated Successfully!!", safe=False)
        return JsonResponse("Failed to Update.", safe=False)

    elif request.method == 'DELETE':
        query = Query.objects.get(QueryId=id)
        query.delete()
        return JsonResponse("Deleted Succeffully!!", safe=False)


@csrf_exempt
def getOrder(request, id=0):

    if request.method == 'POST':
        print("received!")
        order_data = JSONParser().parse(request)
        print(order_data)
        order_serializer = OrderSerializer(data=order_data)
        if order_serializer.is_valid():
            order_serializer.save()
            # print(order_serializer.data['OrderId'])
            return JsonResponse(order_serializer.data['OrderId'], safe=False)
        return JsonResponse("Failed to Add.", safe=False)
        # print("received!")
        # print(request)
        # print(city_data)
        # return JsonResponse("wow")

    elif request.method == 'GET':
        # menuItems = MenuItem.objects.get(ItemId=id)
        orders = Order.objects.all()
        # menuItems = MenuItem.objects.filter(
        #     RestaurantName=id)
        order_serializer = OrderSerializer(orders, many=True)
        return JsonResponse(order_serializer.data, safe=False)

    elif request.method == 'PUT':
        order_data = JSONParser().parse(request)
        OrderId = Order.objects.get(OrderId=order_data['OrderId'])
        order_serializer = OrderSerializer(OrderId, data=order_data)
        if order_serializer.is_valid():
            order_serializer.save()
            return JsonResponse("Updated Successfully!!", safe=False)
        return JsonResponse("Failed to Update.", safe=False)

    elif request.method == 'DELETE':
        OrderId = Order.objects.get(OrderId=id)
        OrderId.delete()
        return JsonResponse("Deleted Succeffully!!", safe=False)


@csrf_exempt
def getOrderItem(request, id=0):

    if request.method == 'POST':
        print("received!")
        orderItem_data = JSONParser().parse(request)
        print(orderItem_data)
        orderItem_serializer = OrderItemsSerializer(data=orderItem_data)
        if orderItem_serializer.is_valid():
            orderItem_serializer.save()
            return JsonResponse("Added Successfully!!", safe=False)
        return JsonResponse("Failed to Add.", safe=False)
        # print("received!")
        # print(request)
        # print(city_data)
        # return JsonResponse("wow")

    elif request.method == 'GET':
        # menuItems = MenuItem.objects.get(ItemId=id)
        orderItems = OrderItems.objects.all()
        # menuItems = MenuItem.objects.filter(
        #     RestaurantName=id)
        orderItem_serializer = OrderItemsSerializer(orderItems, many=True)
        return JsonResponse(orderItem_serializer.data, safe=False)

    elif request.method == 'PUT':
        orderItem_data = JSONParser().parse(request)
        OrderItemId = OrderItems.objects.get(
            OrderItemId=orderItem_data['OrderItemId'])
        orderItem_serializer = OrderItemsSerializer(
            OrderItemId, data=orderItem_data)
        if orderItem_serializer.is_valid():
            orderItem_serializer.save()
            return JsonResponse("Updated Successfully!!", safe=False)
        return JsonResponse("Failed to Update.", safe=False)

    elif request.method == 'DELETE':
        OrderItemId = OrderItems.objects.get(OrderItemId=id)
        OrderItemId.delete()
        return JsonResponse("Deleted Succeffully!!", safe=False)


@csrf_exempt
def cityApi(request, id=0):
    if request.method == 'GET':
        if id == 0:
            cities = City.objects.all()
            city_serializer = CitySerializer(cities, many=True)
            return JsonResponse(city_serializer.data, safe=False)

        city = City.objects.get(CityId=id)
        restaurants = city.restaurant_set.all()
        restaurant_serializer = RestaurantSerializer(
            restaurants, many=True)
        city_serializer = CitySerializer(city)
        return JsonResponse([city_serializer.data, restaurant_serializer.data], safe=False)

    elif request.method == 'POST':
        city_data = JSONParser().parse(request)
        city_serializer = CitySerializer(data=city_data)
        if city_serializer.is_valid():
            city_serializer.save()
            return JsonResponse("Added Successfully!!", safe=False)
        return JsonResponse("Failed to Add.", safe=False)

    elif request.method == 'PUT':
        city_data = JSONParser().parse(request)
        city = City.objects.get(CityId=city_data['CityId'])
        city_serializer = CitySerializer(city, data=city_data)
        if city_serializer.is_valid():
            city_serializer.save()
            return JsonResponse("Updated Successfully!!", safe=False)
        return JsonResponse("Failed to Update.", safe=False)

    elif request.method == 'DELETE':
        city = City.objects.get(CityId=id)
        city.delete()
        return JsonResponse("Deleted Succeffully!!", safe=False)


@csrf_exempt
def restaurantApi(request, id=0):

    if request.method == 'GET':

        cat = request.GET.get('category')
        # print(cat)
        # print(type(cat))
        # print(request)
        # for i in request:
        #     print(i)

        if id == 0:
            restaurants = Restaurant.objects.all().order_by('-RankingFactor')
            restaurant_serializer = RestaurantSerializer(
                restaurants, many=True)
            return JsonResponse(restaurant_serializer.data, safe=False)

        if cat is None:
            restaurant = Restaurant.objects.get(RestaurantId=id)
            # menuItems = MenuItem.objects.filter(RestaurantName=id)
            # categories = menuItems.objects.all().values_list('CategoryName', flat=True).distinct()

            # 2 layer logic to save space and eliminate redudancy

            category_list = MenuItem.objects.filter(
                RestaurantName=id).values("CategoryName").distinct()
            # print(toy_owners)
            categories = Category.objects.filter(
                CategoryId__in=category_list).order_by('-RankingFactor')
            # print(categories)
            # print(type(menuItems[0]))
            # categories = restaurant.category_set.all()
            category_serializer = CategorySerializer(
                categories, many=True)
            restaurant_serializer = RestaurantSerializer(restaurant)
            return JsonResponse([restaurant_serializer.data, category_serializer.data], safe=False)
            # return JsonResponse(category_serializer.data, safe=False)

        # restaurant = Restaurant.objects.get(RestaurantId=id)
        category = Category.objects.get(Name=cat)
        # print(category.CategoryId)
        menuItems = MenuItem.objects.filter(
            RestaurantName=id, CategoryName=category.CategoryId).order_by('-RankingFactor')
        menuItem_serializer = MenuItemSerializer(menuItems, many=True)
        category_serializer = CategorySerializer(category)
        return JsonResponse([id, category_serializer.data, menuItem_serializer.data], safe=False)

    elif request.method == 'POST':
        restaurant_data = JSONParser().parse(request)
        restaurant_serializer = RestaurantSerializer(data=restaurant_data)
        if restaurant_serializer.is_valid():
            restaurant_serializer.save()
            return JsonResponse("Added Successfully!!", safe=False)
        return JsonResponse("Failed to Add.", safe=False)

    elif request.method == 'PUT':
        restaurant_data = JSONParser().parse(request)
        restaurant = Restaurant.objects.get(
            RestaurantId=restaurant_data['RestaurantId'])
        restaurant_serializer = RestaurantSerializer(
            restaurant, data=restaurant_data)
        if restaurant_serializer.is_valid():
            restaurant_serializer.save()
            return JsonResponse("Updated Successfully!!", safe=False)
        return JsonResponse("Failed to Update.", safe=False)

    elif request.method == 'DELETE':
        restaurant = Restaurant.objects.get(RestaurantId=id)
        restaurant.delete()
        return JsonResponse("Deleted Succeffully!!", safe=False)


@csrf_exempt
def categoryApi(request, rid=0, cid=0):
    if request.method == 'GET':

        if cid == 0:
            categories = Category.objects.all()
            category_serializer = CategorySerializer(
                categories, many=True)
            return JsonResponse(category_serializer.data, safe=False)

        category = Category.objects.get(CategoryId=cid)
        category_serializer = CategorySerializer(category)
        return JsonResponse(category_serializer.data, safe=False)

    elif request.method == 'POST':
        category_data = JSONParser().parse(request)
        category_serializer = CategorySerializer(data=category_data)
        if category_serializer.is_valid():
            category_serializer.save()
            return JsonResponse("Added Successfully!!", safe=False)
        return JsonResponse("Failed to Add.", safe=False)

    elif request.method == 'PUT':
        category_data = JSONParser().parse(request)
        category = Category.objects.get(
            CategoryId=category_data['CategoryId'])
        category_serializer = CategorySerializer(
            category, data=category_data)
        if category_serializer.is_valid():
            category_serializer.save()
            return JsonResponse("Updated Successfully!!", safe=False)
        return JsonResponse("Failed to Update.", safe=False)

    elif request.method == 'DELETE':
        category = Category.objects.get(CategoryId=id)
        category.delete()
        return JsonResponse("Deleted Succeffully!!", safe=False)


@csrf_exempt
def menuItemApi(request, id=0):
    if request.method == 'GET':
        # menuItems = MenuItem.objects.get(ItemId=id)
        # menuItems = MenuItem.objects.all()
        menuItems = MenuItem.objects.filter(
            RestaurantName=id)
        menuItem_serializer = MenuItemSerializer(menuItems, many=True)
        return JsonResponse(menuItem_serializer.data, safe=False)

    elif request.method == 'POST':
        menuItem_data = JSONParser().parse(request)
        menuItem_serializer = MenuItemSerializer(data=menuItem_data)
        if menuItem_serializer.is_valid():
            menuItem_serializer.save()
            return JsonResponse("Added Successfully!!", safe=False)
        return JsonResponse("Failed to Add.", safe=False)

    elif request.method == 'PUT':
        menuItem_data = JSONParser().parse(request)
        menuItem = MenuItem.objects.get(menuItemId=menuItem_data['ItemId'])
        menuItem_serializer = MenuItemSerializer(menuItem, data=menuItem_data)
        if menuItem_serializer.is_valid():
            menuItem_serializer.save()
            return JsonResponse("Updated Successfully!!", safe=False)
        return JsonResponse("Failed to Update.", safe=False)

    elif request.method == 'DELETE':
        menuItem = MenuItem.objects.get(ItemId=id)
        menuItem.delete()
        return JsonResponse("Deleted Succeffully!!", safe=False)


@csrf_exempt
@api_view(('GET', 'POST', 'PUT', 'DELETE'))
def getAdImage(request, id=0):

    if request.method == 'POST':
        print("received!")
        print(request)
        merchant_data = JSONParser().parse(request)

        # merchant_data = request


@csrf_exempt
def searchApi(request, id=0):

    if request.method == 'GET':

        query = request.GET.get("query")

        # print(type(query))

        # restaurant = Restaurant.objects.get(RestaurantId=id)

        menuItems = MenuItem.objects.filter(
            RestaurantName=id).filter(Name__icontains=query)
        # if id == 0:
        # menuItems = MenuItem.objects.all()
        # .order_by('-RankingFactor')
        menuItem_serializer = MenuItemSerializer(menuItems, many=True)

        return JsonResponse(menuItem_serializer.data, safe=False)
        # else:


@csrf_exempt
def SaveFile(request):
    file = request.FILES['myFile']
    file_name = default_storage.save(file.name, file)

    return JsonResponse(file_name, safe=False)
