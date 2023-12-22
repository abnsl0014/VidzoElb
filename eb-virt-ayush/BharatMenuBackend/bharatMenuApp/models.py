from email.policy import default
# from tkinter import PhotoImage
from django.db import models
from django.core.validators import *
from phonenumber_field.formfields import PhoneNumberField
from django.contrib.auth.models import User
from django.conf import settings
import tempfile
from django.core.files import File
import datetime
from gtts import gTTS
# Create your models here.


class City(models.Model):
    CityId = models.AutoField(primary_key=True)
    CityName = models.CharField(max_length=100)
    RankingFactor = models.IntegerField(default=1)
    Pincode = models.PositiveIntegerField(default=0)

    def __str__(self):
        return self.CityName


class Restaurant(models.Model):
    RestaurantId = models.AutoField(primary_key=True)
    ShopName = models.CharField(max_length=100)
    CityName = models.ForeignKey(
        'City', on_delete=models.CASCADE, default=None)
    Address = models.CharField(max_length=100)
    Rating = models.IntegerField(default=5, help_text='Value 1 to 10', validators=[MaxValueValidator(10),
                                                                                   MinValueValidator(1)])
    DateOfJoining = models.DateField(default=datetime.date.today)
    RankingFactor = models.IntegerField(default=1)
    RestaurantImage = models.ImageField(
        default='restaurant_default.png', blank=True)
    PhotoFileName = models.CharField(max_length=100, blank=True)

    def __str__(self):
        return self.ShopName


class Category(models.Model):
    CategoryId = models.AutoField(primary_key=True)
    Name = models.CharField(max_length=100)
    RankingFactor = models.IntegerField(default=1)
    CategoryImage = models.ImageField(
        default='category_default.png', blank=True)
    RestaurantName = models.ForeignKey(
        'Restaurant', on_delete=models.CASCADE, default=None)

    def __str__(self):
        return self.Name


class MenuItem(models.Model):
    ItemId = models.AutoField(primary_key=True)
    Name = models.CharField(max_length=100)
    Price = models.PositiveIntegerField()
    RestaurantName = models.ForeignKey(
        'Restaurant', on_delete=models.CASCADE, default=None)
    CategoryName = models.ForeignKey(
        'Category', on_delete=models.CASCADE, default=None)
    Rating = models.IntegerField(default=5, help_text='Value 1 to 10', validators=[MaxValueValidator(10),
                                                                                   MinValueValidator(1)])
    ItemPhotoName = models.CharField(max_length=100, blank=True)
    RankingFactor = models.IntegerField(default=1)
    ItemImage = models.ImageField(default='menuitem_default.png', blank=True)
    quantity = models.PositiveIntegerField(default=0)

    class Types(models.TextChoices):
        VEG = "1", "VEG"
        NONVEG = "2", "NONVEG"
    type = models.CharField(
        max_length=2,
        choices=Types.choices,
        default=Types.VEG
    )
    Combo = models.BooleanField(default=False)
    Popular = models.BooleanField(default=False)
    MustTry = models.BooleanField(default=False)
    Available = models.BooleanField(default=False)
    BestSeller = models.BooleanField(default=False)
    Description = models.CharField(max_length=25, default='')
    TodaysSpecial = models.BooleanField(default=False)

    def __str__(self):
        return self.Name


class Search(models.Model):
    ItemId = models.AutoField(primary_key=True)


class Order(models.Model):
    OrderId = models.AutoField(primary_key=True)
    RestaurantId = models.ForeignKey(
        'Restaurant', on_delete=models.CASCADE, default=None)
    ItemsNumber = models.PositiveIntegerField()
    UserName = models.CharField(max_length=25)
    UserPhone = models.PositiveBigIntegerField(default=0)
    OrderDateTime = models.DateTimeField(auto_now_add=True)
    TableNumber = models.PositiveIntegerField()
    TotalPrice = models.PositiveBigIntegerField()

    def __str__(self):
        return self.UserName


class OrderItems(models.Model):
    OrderItemId = models.AutoField(primary_key=True)
    OrderId = models.ForeignKey(
        'Order', on_delete=models.CASCADE, default=None)
    ItemName = models.CharField(max_length=100)
    Quantity = models.PositiveIntegerField()
    Price = models.PositiveBigIntegerField()

    def __str__(self):
        return self.ItemName


class Profile(models.Model):
    ProfileId = models.AutoField(primary_key=True)
    phoneNumber = models.PositiveBigIntegerField(default=0)
    fullName = models.CharField(max_length=100, default="")
    otpVerified = models.BooleanField(default=0)
    email = models.EmailField(default="")
    Note = models.CharField(max_length=350, default="")

    def __int__(self):
        return self.ProfileId


class Query(models.Model):
    QueryId = models.AutoField(primary_key=True)
    profileId = models.ForeignKey(
        'Profile', on_delete=models.CASCADE, default=None)
    # queryType = models.

    class VideoTypes(models.TextChoices):
        TEXT = "1", "TEXT"
        VIDEO = "2", "VIDEO"

    queryType = models.CharField(
        max_length=2,
        choices=VideoTypes.choices,
        default=VideoTypes.TEXT
    )

    query = models.CharField(max_length=5000, default="", blank=True)
    businessName = models.CharField(max_length=500, default="", blank=True)
    queryDateTime = models.DateTimeField(auto_now_add=True)

    VideoAd = models.FileField(upload_to='videos_uploaded', null=True, blank=True,
                               validators=[FileExtensionValidator(allowed_extensions=['MOV', 'avi', 'mp4', 'webm', 'mkv'])])
    AudioFile = models.FileField(upload_to='audios_uploaded/', null=True, blank=True)

    Image = models.ImageField(default='happy.png', blank=True)

    TextAd = models.CharField(max_length=5000, default="", blank=True)

    businessType = models.CharField(max_length=500, default="", blank=True)

    businessUrl = models.CharField(max_length=500, default="", blank=True)

    socialMediaUrl = models.CharField(max_length=500, default="", blank=True)

    class StatusTypes(models.TextChoices):
        NOT_STARTED = "1", "NOT_STARTED"
        IN_PROCESS = "2", "IN_PROCESS"
        DISCARDED = '3', "DISCARDED"
        DONE = '4', "DONE"

    status = models.CharField(
        max_length=4,
        choices=StatusTypes.choices,
        default=StatusTypes.NOT_STARTED
    )

    def __int__(self):
        return self.QueryId
        
    # def save(self, *args, **kwargs):
    #     audio = gTTS(text=self.query, lang='en', slow=True)

    #     with tempfile.TemporaryFile(mode='rb+') as f:
    #         audio.write_to_fp(f)
    #         file_name = '{}.mp3'.format(self.query)
    #         self.AudioFile.save(file_name, File(file=f))

    #     super(Query, self).save(*args, **kwargs)


# class VideoAd(models.Model):
    # VideoId = models.AutoField(primary_key=True)

    # QueryId = models.ForeignKey(
    #     'Query', on_delete=models.CASCADE, default=None)

    # Video = models.FileField(upload_to='videos_uploaded', null=True,
    #                          validators=[FileExtensionValidator(allowed_extensions=['MOV', 'avi', 'mp4', 'webm', 'mkv'])])

    # class StatusTypes(models.TextChoices):
    #     NOT_STARTED = "1", "NOT_STARTED"
    #     IN_PROCESS = "2", "IN_PROCESS"
    #     DISCARDED = '3', "DISCARDED"
    #     DONE = '4', "DONE"

    # status = models.CharField(
    #     max_length=4,
    #     choices=StatusTypes.choices,
    #     default=StatusTypes.NOT_STARTED
    # )

    # def __int__(self):
    #     return self.VideoId


# class TextAd(models.Model):
    # TextAdId = models.AutoField(primary_key=True)

    # QueryId = models.ForeignKey(
    #     'Query', on_delete=models.CASCADE, default=None)

    # Image = models.ImageField(default='menuitem_default.png', blank=True)

    # response = models.CharField(max_length=5000, default="")

    # class StatusTypes(models.TextChoices):
    #     NOT_STARTED = "1", "NOT_STARTED"
    #     IN_PROCESS = "2", "IN_PROCESS"
    #     DISCARDED = '3', "DISCARDED"
    #     DONE = '4', "DONE"

    # status = models.CharField(
    #     max_length=4,
    #     choices=StatusTypes.choices,
    #     default=StatusTypes.DONE
    # )

    # def __int__(self):
    #     return self.TextAdId


class Merchant(models.Model):
    MerchantId = models.AutoField(primary_key=True)
    ShopName = models.CharField(max_length=150)
    fullName = models.CharField(max_length=100)
    Address = models.CharField(max_length=100)
    phoneNumber = models.PositiveBigIntegerField(default=0)
    CityName = models.CharField(max_length=50, default="")
    email = models.EmailField()
    password = models.CharField(max_length=50, default="test")
    # userId = models.PositiveBigIntegerField(default=0)
    gst = models.PositiveBigIntegerField(default=0)
    Pincode = models.PositiveIntegerField(default=0)
    # userId = models.ForeignKey(User, on_delete=models.CASCADE, default=0)
    userId = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        default=1
    )
    RestaurantId = models.ForeignKey(
        'Restaurant', on_delete=models.CASCADE, default=None)
    ProfileId = models.ForeignKey(
        'Profile', on_delete=models.CASCADE, default=None)

    def __str__(self):
        return self.ShopName

class Reminder(models.Model):
    id = models.AutoField(primary_key=True)
    phone_number = models.CharField(max_length=15)
    message = models.TextField(default="")
    reminder_time = models.DateTimeField(default=None)

    def __int__(self):
        return self.id