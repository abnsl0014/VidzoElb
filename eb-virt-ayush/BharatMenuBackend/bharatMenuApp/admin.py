from django import forms
from django.contrib import admin
from .models import City
from .models import Restaurant
from .models import MenuItem
from .models import Category
from .models import Search
from .models import Order
from .models import OrderItems
from .models import Profile
from .models import Merchant
from .models import Query
from .models import Reminder

# Register your models here.


# class MenuItemAdmin():
#     change_form_template = 'change_form.html'

# class MenuItemAdmin(admin.ModelAdmin):
#     def formfield_for_foreignkey(self, db_field, request, **kwargs):
#         print(request)
#         if db_field.name == "CategoryName":
#             kwargs["queryset"] = Category.objects.filter(
#                 RestaurantName=request)
#         return super().formfield_for_foreignkey(db_field, request, **kwargs)


# class CustomMenuItemModelForm(forms.ModelForm):
#     class Meta:
#         model = MenuItem
#         fields = '__all__'

#     def __init__(self, obj=None, *args, **kwargs):
#         super(CustomMenuItemModelForm, self).__init__(*args, **kwargs)
#         # print(self.fields['RestaurantName'])
#         # print("hey")
#         # for arg in args:
#         #     print("Next argument through *argv :", arg)
#         # for key, value in self.fields.items():
#         #     print("%s == %s" % (key, value))
#         # print(request)
#         print(obj)
#         self.fields['CategoryName'].queryset = Category.objects.filter(
#             RestaurantName=1)  # or something else

# # # Use it in your modelAdmin


# class MenuItemAdmin(admin.ModelAdmin):
#     form = CustomMenuItemModelForm


# def menuitemform_factory(restaurant):
#     class MenuItemForm(forms.ModelForm):
#         CategoryName = forms.ModelChoiceField(
#             queryset=Category.objects.filter(RestaurantName=1)
#         )
#     return MenuItemForm


# class MenuItemAdmin(admin.ModelAdmin):

#     def get_form(self, request, obj=None, **kwargs):
#         if obj is not None and obj.type is not None:
#             kwargs['form'] = menuitemform_factory(obj.type)
#         return super(MenuItemAdmin, self).get_form(request, obj, **kwargs)


admin.site.register(City)
admin.site.register(Restaurant)
admin.site.register(MenuItem)
admin.site.register(Category)
admin.site.register(Search)
admin.site.register(Order)
admin.site.register(OrderItems)
admin.site.register(Profile)
admin.site.register(Merchant)
admin.site.register(Query)
admin.site.register(Reminder)
# admin.site.register(MenuItem, MenuItemAdmin)
