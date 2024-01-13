# from msilib.schema import AdminExecuteSequence
import django
django.setup()
import json
import io
import os
import openai
import requests
from django.http import HttpResponse
from django.core.files.storage import default_storage
from bharatMenuApp.serializers import CitySerializer, RestaurantSerializer, MenuItemSerializer, CategorySerializer, OrderSerializer, OrderItemsSerializer, RegisterSerializer, MerchantSerializer, ProfileSerializer, QuerySerializer, QuerySerializerReadOnly, ReminderSerializer, TaskSerializer
from bharatMenuApp.models import City, Restaurant, MenuItem, Category, Order, OrderItems, Merchant, Profile, Query, Reminder, Task
from unicodedata import category
from django import forms
from django import db
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
# from django.views.decorators import api_view
from rest_framework.decorators import api_view
from rest_framework.decorators import permission_classes
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
from gtts import gTTS
from django.core.files.base import ContentFile
import replicate
from multiprocessing import Process
from twilio.rest import Client
from .tasks import send_reminder
from twilio.twiml.voice_response import VoiceResponse, Gather
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import exception_handler
from functools import wraps
import jwt
from rest_framework.permissions import AllowAny
from authlib.integrations.django_oauth2 import ResourceProtector
from . import utils

AUTH0_DOMAIN = "dev-2hnipz5fgv5putia.us.auth0.com"
AUTH0_AUDIENCE = "https://dev-2hnipz5fgv5putia.us.auth0.com/api/v2/"

require_auth = ResourceProtector()
validator = utils.Auth0JWTBearerTokenValidator(
    "dev-2hnipz5fgv5putia.us.auth0.com",
    "https://dev-2hnipz5fgv5putia.us.auth0.com/api/v2/"
)
require_auth.register_token_validator(validator)



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
def call_response(request):

    if request.method == 'GET':
        message = request.GET.get('message', 'Default message')

        response = VoiceResponse()
        response.say(message)

        # response.gather()

        with response.gather(numDigits=1, action='/process-input') as gather:
            gather.say("Press 1 to confirm.")

        # response.say("Let's do this, Press 1 to confirm")

        print(response)

        response.say("Have a Good Day!")

        return HttpResponse(str(response), content_type='application/xml')
        # return HttpResponse(response)


@csrf_exempt
def process_input(request):

    digit_pressed = request.GET.get('Digits', None)
    caller_id = request.GET.get('CallSid', None)

    reminder = Reminder.objects.get(call_sid=caller_id)

    response = VoiceResponse()

    if digit_pressed == '1':
        response.say("You pressed 1. Confirmation successful")
        reminder.user_response = digit_pressed
        reminder.save()
        # response.say(caller_id)
    else:
        response.say("Invalid input.")

    # if 'Digits' in request.values:

    # response.say("Your pressed key is: " + digit_pressed)
    # response.say(request.values['From'])
        
    # response.say("Your caller id is: " + caller_id)
    response.say("Thankyou!")

    return HttpResponse(str(response), content_type='application/xml')




@csrf_exempt
@api_view(('POST', 'GET',))
@require_auth(None)
def make_reminder(request):

    # url = "http://127.0.0.1:8000/api/callresponse"
    url = "https://backend.bharatmenu.com/api/callresponse/?message=Hi"

    if request.method == 'GET':
        account_sid = "AC1027c48a892cea337d9d28fae752a186"
        auth_token = "7dee7fd1aff03e05b31f2500d4f1183c"
        client = Client(account_sid, auth_token)

        # response_text = "Hello, Ayush this is a TwiML response."
        # twiml_response = f"""
        #     <Response>
        #         <Say>{response_text}</Say>
        #     </Response>
        # """

        call = client.calls.create(
                                url=url,
                                to='+919023389953',
                                from_='+14152879886'
                            )
        print(call.sid)
        return JsonResponse(call.sid, safe=False)
    

    if request.method == 'POST':
        # Assuming you receive timestamp and message in the request data
        reminder_data = JSONParser().parse(request)

        print(reminder_data)
    
        reminder_serializer = ReminderSerializer(data=reminder_data)

        if reminder_serializer.is_valid():
            reminder = reminder_serializer.save()
            # Schedule the reminder immediately
            send_reminder.apply_async(args=[reminder.id], eta=reminder.reminder_time)
            return Response({'success': 'Reminder scheduled successfully'})
        else:
            return Response({'fail': 'Reminder scheduled failed'})


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
    #only phone is mandatory field
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


def ReplicateVideo(id):
    query = Query.objects.get(QueryId=id)
    # output = replicate.run(
    #     "cjwbw/sadtalker:3aa3dac9353cc4d6bd62a8f95957bd844003b401ca4e4a9b33baa574c549d376",
    #     input={
    #         "still": True,
    #         "enhancer": "gfpgan",
    #         "preprocess": "crop",
    #         "driven_audio": query.AudioFile.url,
    #         "source_image": query.Image.url
    #     }
    # )
    output = "https://replicate.delivery/pbxt/oYxiMuenVfsJV0278l5k53xJmrSLSZfwvzd2SfBNJOr15DwHB/out.mp4"
    print(output)

    response = requests.get(output)

    print(response)

    if response.status_code == 200:
        # Save the video content to the model
        query.VideoAd.save(f'{query.QueryId}_video.mp4', ContentFile(response.content))    


@csrf_exempt
def getAvatarVideo(request, id=0):

    if request.method == 'GET':
        if id != 0:
            queries = Query.objects.filter(QueryId=id)
            query_serializer = QuerySerializerReadOnly(queries, many=True)
            return JsonResponse(query_serializer.data, safe=False)
        else:
            return JsonResponse("Failed", safe=False)
        

    if request.method == 'POST':
        query_data = JSONParser().parse(request)
        query_serializer = QuerySerializer(data=query_data)
        if query_serializer.is_valid():
            query = query_serializer.save()
            text_to_convert = query.TextAd
            if text_to_convert != "":

                # generate audio

                tts = gTTS(text=text_to_convert, lang='en', slow=False)
                audio_content_io = io.BytesIO()
                tts.write_to_fp(audio_content_io)
                query.AudioFile.save(f'{query.QueryId}_output.mp3', ContentFile(audio_content_io.getvalue()))
                audio_content_io.close()

                #generate video

                REPLICATE_API_TOKEN="r8_cPOPQV3iVxK3H8twxhWCrLfbkdXzhi23uR44s"

                # replicate = replicate.Client(api_token=REPLICATE_API_TOKEN)

                os.environ["REPLICATE_API_TOKEN"] = REPLICATE_API_TOKEN

                print(query.AudioFile.url)
                print(query.Image.url)

                db.connections.close_all()

                p = Process(target=ReplicateVideo, args=(query.QueryId,))
                p.start()
                
                # output = replicate.run(
                #     "cjwbw/sadtalker:3aa3dac9353cc4d6bd62a8f95957bd844003b401ca4e4a9b33baa574c549d376",
                #     input={
                #         "still": True,
                #         "enhancer": "gfpgan",
                #         "preprocess": "crop",
                #         "driven_audio": query.AudioFile.url,
                #         "source_image": query.Image.url
                #     }
                # )
                # print(output)

                # output = "http://commondatastorage.googleapis.com/gtv-videos-bucket/sample/SubaruOutbackOnStreetAndDirt.mp4"
                # print(output)

                # response = requests.get(output)

                # print(response)

                # if response.status_code == 200:
                #     # Save the video content to the model
                #     query.VideoAd.save(f'{query.QueryId}_video.mp4', ContentFile(response.content))
                # else:
                #     return JsonResponse({"message": f"Failed to download video. Status code: {response.status_code}"}, safe=False)
            return JsonResponse("message Video downloaded and saved successfully!", safe=False)
        return JsonResponse("Failed to Update.", safe=False)

    if request.method == 'PUT':
        query_data = JSONParser().parse(request)
        query = Query.objects.get(QueryId=query_data['QueryId'])
        query_serializer = QuerySerializerReadOnly(query, data=query_data)
        if query_serializer.is_valid():
            query_serializer.save()
            # text_to_convert = query.TextAd
            # tts = gTTS(text=text_to_convert, lang='en', slow=False)
            # audio_content_io = io.BytesIO()
            # tts.write_to_fp(audio_content_io)
            # query.AudioFile.save(f'{query.QueryId}_output.mp3', ContentFile(audio_content_io.getvalue()))
            # audio_content_io.close()
            return JsonResponse("Updated Successfully!!", safe=False)
        return JsonResponse("Failed to Update.", safe=False)
        

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

@csrf_exempt
def api_exception_handler(exc, context=None):
    response = exception_handler(exc, context=context)
    if response and isinstance(response.data, dict):
        response.data = {'message': response.data.get('detail', 'API Error')}
    else:
        response.data = {'message': 'API Error'}
    return response

# @permission_classes([IsAuthenticated])
# @api_view(('GET', 'POST', 'PUT', 'DELETE'))
# def authenticate_user(request):
#     print("Endpoint hit")
#     print(request)
#     data = JSONParser().parse(request)
#     token = request.headers.get('Authorization')
#     print(data)
#     print(token)

#     # permission_classes = [IsAuthenticated]

#     # print(permission_classes)

#     return JsonResponse(data, safe=False) 


# def get_token_auth_header(request):
#     """Obtains the Access Token from the Authorization Header
#     """
#     auth = request.META.get("HTTP_AUTHORIZATION", None)
#     parts = auth.split()
#     token = parts[1]

#     return token

# def requires_scope(required_scope):
#     """Determines if the required scope is present in the Access Token
#     Args:
#         required_scope (str): The scope required to access the resource
#     """
#     def require_scope(f):
#         @wraps(f)
#         def decorated(*args, **kwargs):
#             token = get_token_auth_header(args[0])
#             print(token)
#             decoded = jwt.decode(token, verify=False)
#             if decoded.get("scope"):
#                 token_scopes = decoded["scope"].split()
#                 for token_scope in token_scopes:
#                     if token_scope == required_scope:
#                         return f(*args, **kwargs)
#             response = JsonResponse({'message': 'You don\'t have access to this resource'})
#             response.status_code = 403
#             return response
#         return decorated
#     return require_scope


# @api_view(['GET'])
# @permission_classes([AllowAny])
# def public(request):
#     return JsonResponse({'message': 'Hello from a public endpoint! You don\'t need to be authenticated to see this.'})

# @api_view(['GET'])
# def private(request):
#     print("dasds")
#     # data = JSONParser().parse(request)
#     print(request)
#     print(request.headers)
#     return JsonResponse({'message': 'Hello from a private endpoint! You need to be authenticated to see this.'})

# @api_view(['GET'])
# @requires_scope('read:messages')
# def private_scoped(request):
#     # data = JSONParser().parse(request)
#     print(request.data)
#     print("sqsq")
#     return JsonResponse({'message': 'Hello from a private endpoint! You need to be authenticated and have a scope of read:messages to see this.'})


@csrf_exempt
def public(request):
    """No access token required to access this route
    """
    response = "Hello from a public endpoint! You don't need to be authenticated to see this."
    return JsonResponse(dict(message=response))


def getProfileId(auth):

    url = 'https://dev-2hnipz5fgv5putia.us.auth0.com/userinfo'

    resp = requests.get(url, headers={'Authorization': auth})

    # print(resp.json().get('email'))

    email = resp.json().get('email')
    name = resp.json().get('name')

    profile_instance = Profile.objects.get_or_create(email=email)
    if profile_instance[0].fullName == "":
        profile_instance[0].fullName = name
    profile_instance[0].save()

    # print(profile_instance)

    id = profile_instance[0].ProfileId

    return id



@csrf_exempt
@require_auth(None)
def get_tasks(request):
    """A valid access token is required to access this route
    """

    auth = request.headers.get('Authorization')

    id = getProfileId(auth)

    tasks_for_user = Task.objects.filter(profileId=id)

    task_serializer = TaskSerializer(tasks_for_user, many=True)

    return JsonResponse(task_serializer.data, safe=False)


@csrf_exempt
@api_view(('POST', 'GET',))
@require_auth(None)
def make_tasks(request):
    """A valid access token is required to access this route
    """

    if request.method == 'POST':

        auth = request.headers.get('Authorization')

        id = getProfileId(auth)

        task_data = JSONParser().parse(request)

        # print(task_data)

        task_data['profileId'] = id

        # print(task_data)
    
        task = TaskSerializer(data=task_data)

        if task.is_valid():
            task.save()
            return Response({'success': 'Task saved successfully'})
        else:
            return Response({'fail': 'Task saving failed'})


        

    return JsonResponse(task_serializer.data, safe=False)


@csrf_exempt
@require_auth(None)
def get_reminders(request, id=0):
    """A valid access token is required to access this route
    """

    # taskId = request.GET.get('taskId')

    reminders_for_task = Reminder.objects.filter(taskId=id)

    reminder_serializer = ReminderSerializer(reminders_for_task, many=True)

    return JsonResponse(reminder_serializer.data, safe=False)


@csrf_exempt
@require_auth("read:messages")
def private_scoped(request):
    """A valid access token and an appropriate scope are required to access this route
    """
    response = "Hello from a private endpoint! You need to be authenticated and have a scope of read:messages to see this."
    return JsonResponse(dict(message=response))


#API's for habit app


# @csrf_exempt
# @require_auth(None)
# def getTasks(request):
#     """A valid access token is required to access this route
#     """

#     # print(request.headers)

#     url = 'https://dev-2hnipz5fgv5putia.us.auth0.com/userinfo'

#     #get user data from token 

#     headers = {'Authorization': 'Bearer your_token'}



#     response = "Hello from a private endpoint! You need to be authenticated to see this."
#     return JsonResponse(dict(message=response))