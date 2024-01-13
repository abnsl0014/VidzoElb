from django.urls import re_path
from bharatMenuApp import views

from django.conf.urls.static import static
from django.conf import settings
from knox import views as knox_views

urlpatterns = [
    re_path(r'^city$', views.cityApi),
    re_path(r'^city/([0-9]+)$', views.cityApi),

    re_path(r'^restaurant$', views.restaurantApi),
    re_path(r'^restaurant/([0-9]+)/$', views.restaurantApi),

    re_path(r'^search/([0-9]+)/', views.searchApi),

    re_path(r'^cart/([0-9]+)/', views.menuItemApi),

    re_path(r'^restaurant/([0-9]+)/(?P<category>\w+)/$', views.restaurantApi),
    re_path(r'^restaurant/([0-9]+)/category/([0-9]+)$', views.restaurantApi),

    # re_path(r'^category/(?P<username>\w{1,50})/$', views.categoryApi),
    # re_path(r'^getCategory/$', views.get_category),
    # re_path(r'^search/([0-9]+)$/(?P<query>\w+)/$', views.searchApi),
    re_path(r'getOrder/', views.getOrder),
    re_path(r'^getOrderItem/', views.getOrderItem),

    re_path(r'^menuItem$', views.menuItemApi),
    re_path(r'^menuItem/([0-9]+)$', views.menuItemApi),

    re_path(r'api/register/', views.RegisterAPI.as_view(), name='register'),
    re_path(r'api/script/', views.get_ai_script, name='script'),
    re_path(r'api/login/', views.LoginAPI.as_view(), name='login'),
    # re_path(r'api/auth/', views.authenticate_user, name='auth'),
    re_path(r'api/user/', views.get_user_data, name='user'),
    re_path(r'api/merchant/', views.getMerchant, name='merchant'),
    re_path(r'api/otp/', views.get_otp, name='otp'),
    re_path(r'api/verifyotp/', views.verify_otp, name='verifyotp'),
    re_path(r'api/callresponse/$', views.call_response, name='callresponse'),
    re_path(r'api/callresponse/process-input/$', views.process_input, name='process-input'),
    re_path(r'process-input/', views.process_input, name='process-input'),
    re_path(r'api/video$', views.getAvatarVideo, name='video'),
    re_path(r'api/video/([0-9]+)/$', views.getAvatarVideo, name='video'),
    re_path(r'api/adimage/', views.getAdImage, name='adimage'),
    re_path(r'api/adrequest$', views.ad_request, name='adrequest'),
    re_path(r'api/adrequest/([0-9]+)/$', views.ad_request, name='adrequest'),
    re_path(r'api/adrequest/(?P<phone>\d+)/$', views.ad_request),
    re_path(r'api/logout/', knox_views.LogoutView.as_view(), name='logout'),
    re_path(r'api/logoutall/', knox_views.LogoutAllView.as_view(), name='logoutall'),

    re_path(r'^menuItem/SaveFile$', views.SaveFile),

    #Habitly

    re_path(r'api/get_reminders/([0-9]+)/$', views.get_reminders),
    re_path(r'api/get-tasks', views.get_tasks),
    re_path(r'api/make-reminder/', views.make_reminder, name='make-reminder'),
    re_path(r'api/make-tasks/', views.make_tasks, name='make-tasks'),


    re_path(r'api/public', views.public),
    
    re_path(r'api/private-scoped', views.private_scoped),



] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
