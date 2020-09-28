from django.contrib import admin
from .models import * 
from stor.models import UserProfile
# Register your models here.

def make_refund_accepted(modelsamin,request,queryset):
    queryset.update(refund_request=False,refund_granted=True)

make_refund_accepted.short_description = 'updeate order to refund granted'

class OrderAdmin(admin.ModelAdmin):
    list_display = ['user' ,'ordered','Bing_deliverd','recived','refund_granted','refund_request','billing_address','shipping_address','payment','coupon']

    list_display_links=['user','billing_address','shipping_address','payment','coupon']



    list_filter =['ordered','Bing_deliverd','recived','refund_granted','refund_request']
    search_fields = [
        'user__username','red_code'
    ]
    actions=[make_refund_accepted]
    actions_on_top=[make_refund_accepted]

class AddressAdmin(admin.ModelAdmin):
    list_display =['user','street_address','apartment_address','country','zip','address_type','default']
    list_filter = ['default','address_type','country']
    search_fields = ['user','street_address','apartment_address','zip']


class ItemAdmin(admin.ModelAdmin):
    prepopulated_fields = {'slug' : ('title',)} 
    

class CategoryAdmin(admin.ModelAdmin):
    prepopulated_fields = {'slug' : ('categoryn',)} 
   # prepopulated_fields = {'tag' : ('parent',)} 


    


admin.site.register(Category,CategoryAdmin)

admin.site.register(Item,ItemAdmin)
admin.site.register(OrderItem)
admin.site.register(Order,OrderAdmin)
admin.site.register(Address,AddressAdmin)
admin.site.register(slide)

admin.site.register(Payment)

admin.site.register(Refund)
admin.site.register(Coupon)

admin.site.register(UserProfile)


 