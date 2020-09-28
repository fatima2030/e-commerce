from django.urls import path
from .views import (HomeView,ItemDetaleView,prodecut,add_to_cart,remove_from_cart,OrederSummeryView,
remove_single_item_from_cart,CheckoutView,PaymentView,
add_coupon_view,Refund_Request_View,home_search_view,
category_View,category_List_View,)
app_name = 'stor'


urlpatterns = [
    #path('',HomeView.as_view(), name='home'),
    path('',home_search_view,name='home'),


    path('prodeuts/<slug>/',ItemDetaleView.as_view(),name='prodeuts'),
    path('checkout/',CheckoutView.as_view(),name='checkout'),


   # path('prodeut/',prodecut,name='prodeut'),
    path('add_to_cart/<slug>/',add_to_cart,name='add_to_cart'),
    path('remove_from_cart/<slug>/',remove_from_cart,name='remove_from_cart'),
    path('remove_single_item_from_cart/<slug>/',remove_single_item_from_cart,name='remove_single_item_from_cart'),

    path('Oreder-Summery/',OrederSummeryView.as_view(),name='Oreder-Summery'),
    path('Payment/<payment_option>/',PaymentView.as_view(),name='Payment'),
    path('add_coupon_view/',add_coupon_view.as_view(),name='add_coupon_view'),
    path('Refund_Request_View/',Refund_Request_View.as_view(),name='Refund_Request_View'),
    path('category/<str:cats>/',category_View,name='category'),

    path('category_List_View/',category_List_View,name='category_List_View'),





  
]

