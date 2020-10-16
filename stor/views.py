from django.shortcuts import render ,get_list_or_404,get_object_or_404,redirect
from .models import *
from django.views.generic import ListView ,DetailView,View
from django.utils import timezone
from django.contrib import messages
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from .forms import CheckoutForm,couponFotm,RefundForm,PaymentForm
from django.conf import settings
from django.contrib.auth.models import User
from django.db.models import Q 
from django.core.paginator import EmptyPage, PageNotAnInteger,Paginator
from operator import attrgetter



import string
import stripe
import random
stripe.api_key = settings.STRIPE_SECRET_KEY

  



# Create your views here.
def create_ref_code():
    return ''.join(random.choice(string.ascii_lowercase + string.digits , k=20 ))


def prodecut(request):
    context ={
        "item":Item.objects.all()
    }
    return render(request,'stor/product-page.html',context)



def is_valid_form(values):
    valid = True
    for field in values:
        if field == '':
            valid = False
    return valid




class CheckoutView(View):


    def get(self , *args, **kwargs):

        try:
            order = Order.objects.get(user=self.request.user ,ordered=False)
            
            form = CheckoutForm()

            context ={
                'form': form,
                'couponFotm':couponFotm(),
                
                'order':order,
                'DISPLAY_COUPON_FORM':True,
            }

            shipping_address_qs = Address.objects.filter(
                user=self.request.user,
                address_type='S',
                default=True
                )
            if shipping_address_qs.exists():
                context.update({'default_shipping_address':shipping_address_qs[0]})


            billing_address_qs = Address.objects.filter(
                user=self.request.user,
                address_type='B',
                default=True
                )
            if billing_address_qs.exists():
                context.update({'default_billing_address':billing_address_qs[0]})


            return render(self.request,'stor/checkout-page.html',context)

    
        except ObjectDoesNotExist:
            messages.info(self.request,'You dont have active order..')

            return redirect('stor:checkout')
        

        
        
    def post(self, *args, **kwargs):
        form = CheckoutForm(self.request.POST or None)
        try:
            order = Order.objects.get(user=self.request.user, ordered=False)
            if form.is_valid():

                use_default_shipping = form.cleaned_data.get(
                    'use_default_shipping')
                if use_default_shipping:
                    print("Using the defualt shipping address")
                    address_qs = Address.objects.filter(
                        user=self.request.user,
                        address_type='S',
                        default=True
                    )
                    if address_qs.exists():
                        shipping_address = address_qs[0]
                        order.shipping_address = shipping_address
                        order.save()
                    else:
                        messages.info(
                            self.request, "No default shipping address available")
                        return redirect('stor:checkout')
                else:
                    print("User is entering a new shipping address")
                    shipping_address1 = form.cleaned_data.get(
                        'shipping_address')
                    shipping_address2 = form.cleaned_data.get(
                        'shipping_address2')
                    shipping_country = form.cleaned_data.get(
                        'shipping_country')
                    shipping_zip = form.cleaned_data.get('shipping_zip')

                    if is_valid_form([shipping_address1, shipping_country, shipping_zip]):
                        shipping_address = Address(
                            user=self.request.user,
                            street_address=shipping_address1,
                            apartment_address=shipping_address2,
                            country=shipping_country,
                            zip=shipping_zip,
                            address_type='S'
                        )
                        shipping_address.save()

                        order.shipping_address = shipping_address
                        order.save()

                        set_default_shipping = form.cleaned_data.get(
                            'set_default_shipping')
                        if set_default_shipping:
                            shipping_address.default = True
                            shipping_address.save()

                    else:
                        messages.info(
                            self.request, "Please fill in the required shipping address fields")

                use_default_billing = form.cleaned_data.get(
                    'use_default_billing')
                same_billing_address = form.cleaned_data.get(
                    'same_billing_address')

                if same_billing_address:
                    billing_address = shipping_address
                    billing_address.pk = None
                    billing_address.save()
                    billing_address.address_type = 'B'
                    billing_address.save()
                    order.billing_address = billing_address
                    order.save()

                elif use_default_billing:
                    print("Using the defualt billing address")
                    address_qs = Address.objects.filter(
                        user=self.request.user,
                        address_type='B',
                        default=True
                    )
                    if address_qs.exists():
                        billing_address = address_qs[0]
                        order.billing_address = billing_address
                        order.save()
                    else:
                        messages.info(
                            self.request, "No default billing address available")
                        return redirect('stor:checkout')
                else:
                    print("User is entering a new billing address")
                    billing_address1 = form.cleaned_data.get(
                        'billing_address')
                    billing_address2 = form.cleaned_data.get(
                        'billing_address2')
                    billing_country = form.cleaned_data.get(
                        'billing_country')
                    billing_zip = form.cleaned_data.get('billing_zip')

                    if is_valid_form([billing_address1, billing_country, billing_zip]):
                        billing_address = Address(
                            user=self.request.user,
                            street_address=billing_address1,
                            apartment_address=billing_address2,
                            country=billing_country,
                            zip=billing_zip,
                            address_type='B'
                        )
                        billing_address.save()

                        order.billing_address = billing_address
                        order.save()

                        set_default_billing = form.cleaned_data.get(
                            'set_default_billing')
                        if set_default_billing:
                            billing_address.default = True
                            billing_address.save()

                    else:
                        messages.info(
                            self.request, "Please fill in the required billing address fields")

                payment_option = form.cleaned_data.get('payment_option')

                if payment_option == 'S':
                    return redirect('stor:Payment', payment_option='stripe')
                elif payment_option == 'P':
                    return redirect('stor:Payment', payment_option='paypal')
                else:
                    messages.warning(
                        self.request, "Invalid payment option selected")
                    return redirect('stor:checkout')
        except ObjectDoesNotExist:
            messages.warning(self.request, "You do not have an active order")
            return redirect("stor:order-summary")





class PaymentView(View):
    def get(self, *args, **kwargs):
        order = Order.objects.get(user=self.request.user, ordered=False)
        if order.billing_address:
            context = {
                'order': order,
                'DISPLAY_COUPON_FORM': False
            }
           # userprofile = self.request.user.userprofile
            #userprofile = self.request.user.userprofile
            try:
                userprofile = self.request.user.userprofile
            except UserProfile.DoesNotExist:
                userprofile = UserProfile(user=self.request.user)
            




            if userprofile.one_click_purchasing :
                # fetch the users card list
                cards = stripe.Customer.list_sources(
                    userprofile.stripe_customer_id,
                    limit=3,
                    object='card'
                )
                card_list = cards['data']
                if len(card_list) > 0:
                    # update the context with the default card
                    context.update({
                        'card': card_list[0]
                    })
            return render(self.request, "stor/Payment.html", context)
        else:
            messages.warning(
                self.request, "You have not added a billing address")
            return redirect("stor:checkout")

    def post(self, *args, **kwargs):
        order = Order.objects.get(user=self.request.user, ordered=False)
        form = PaymentForm(self.request.POST)
        #userprofile = UserProfile.objects.get(user=self.request.user)
        userprofile = UserProfile(user=self.request.user)
        if form.is_valid():
            token = form.cleaned_data.get('stripeToken')
            save = form.cleaned_data.get('save')
            use_default = form.cleaned_data.get('use_default')

            if save:
                if userprofile.stripe_customer_id != '' and userprofile.stripe_customer_id is not None:
                    customer = stripe.Customer.retrieve(
                        userprofile.stripe_customer_id)
                    customer.sources.create(source=token)

                else:
                    customer = stripe.Customer.create(
                        email=self.request.user.email,
                    )
                    customer.sources.create(source=token)
                    userprofile.stripe_customer_id = customer['id']
                    userprofile.one_click_purchasing = True
                    userprofile.save()

            amount = int(order.get_total() * 100)

            try:

                if use_default or save:
                    # charge the customer because we cannot charge the token more than once
                    charge = stripe.Charge.create(
                        amount=amount,  # cents
                        currency="usd",
                        customer=userprofile.stripe_customer_id
                    )
                else:
                    # charge once off on the token
                    charge = stripe.Charge.create(
                        amount=amount,  # cents
                        currency="usd",
                        source=token
                    )

                # create the payment
                payment = Payment()
                payment.stripe_charge_id = charge['id']
                payment.user = self.request.user
                payment.amount = order.get_total()
                payment.save()

                # assign the payment to the order

                order_items = order.items.all()
                order_items.update(ordered=True)
                for item in order_items:
                    item.save()

                order.ordered = True
                order.payment = payment
                order.ref_code = create_ref_code()
                order.save()

                messages.success(self.request, "Your order was successful!")
                return redirect("/")

            except stripe.error.CardError as e:
                body = e.json_body
                err = body.get('error', {})
                messages.warning(self.request, f"{err.get('message')}")
                return redirect("/")

            except stripe.error.RateLimitError as e:
                # Too many requests made to the API too quickly
                messages.warning(self.request, "Rate limit error")
                return redirect("/")

            except stripe.error.InvalidRequestError as e:
                # Invalid parameters were supplied to Stripe's API
                print(e)
                messages.warning(self.request, "Invalid parameters")
                return redirect("/")

            except stripe.error.AuthenticationError as e:
                # Authentication with Stripe's API failed
                # (maybe you changed API keys recently)
                messages.warning(self.request, "Not authenticated")
                return redirect("/")

            except stripe.error.APIConnectionError as e:
                # Network communication with Stripe failed
                messages.warning(self.request, "Network error")
                return redirect("/")

            except stripe.error.StripeError as e:
                # Display a very generic error to the user, and maybe send
                # yourself an email
                messages.warning(
                    self.request, "Something went wrong. You were not charged. Please try again.")
                return redirect("/")

            except Exception as e:
                # send an email to ourselves
                messages.warning(
                    self.request, "A serious error occurred. We have been notifed.")
                return redirect("/")

        messages.warning(self.request, "Invalid data received")
        return redirect("stor:Payment")











class HomeView(ListView):
    model = Item
    paginate_by=10
    template_name = 'stor/home-page.html'

    



class OrederSummeryView(LoginRequiredMixin,View):


    def get(self,*arge,**kwargs):
        try:

            order = Order.objects.get(user=self.request.user ,ordered=False)
            context = {
                'object' : order
            }
            return render(self.request ,"stor/order_summery.html",context)

        except ObjectDoesNotExist:
            messages.error(self.request,"Youe dont have active order")
            return redirect('/')









class ItemDetaleView(DetailView):
    model = Item
    template_name = 'stor/product-page.html'
 




@login_required
def add_to_cart(request,slug):
    item = get_object_or_404(Item,slug=slug)
    order_item,created = OrderItem.objects.get_or_create(
        item=item,
        user=request.user,
        ordered=False
        )
    order_qs = Order.objects.filter(user=request.user, ordered=False)
    if order_qs.exists():
        order = order_qs[0]
        if order.items.filter(item__slug=item.slug).exists():
            order_item.quantity += 1
            order_item.save()
            messages.info(request,'This item quantity was updeated ')
            return redirect('stor:Oreder-Summery')

            

        else:
            order.items.add(order_item)
            messages.info(request,'This item was added to your cart')

            return redirect('stor:Oreder-Summery')

    else:
        order_date =timezone.now()
        order = Order.objects.create(user=request.user,order_date=order_date)
        order.items.add(order_item)
        messages.info(request,'This item was added to your cart..')

    return redirect('stor:Oreder-Summery')

@login_required
def remove_from_cart(request,slug):
    item = get_object_or_404(Item,slug=slug)
    order_qs = Order.objects.filter(
        user=request.user,
        ordered=False
    )
    if order_qs.exists():

        order = order_qs[0]
        if order.items.filter(item__slug=item.slug).exists():

            order_item = OrderItem.objects.filter(
                item=item,
                user=request.user,
                ordered=False
            )[0]
            order.items.remove(order_item)
            order_item.delete()


            messages.info(request,'This item was removed from your cart..')
            return redirect('stor:Oreder-Summery')


            
        else:
            messages.info(request,'This item was not in your cart..')

            return redirect('stor:prodeuts',slug= slug)
    else:
        messages.info(request,'You dont have active order..')

        return redirect('stor:prodeuts',slug= slug)




@login_required
def remove_single_item_from_cart(request,slug):
    item = get_object_or_404(Item,slug=slug)
    order_qs = Order.objects.filter(
        user=request.user,
        ordered=False
    )
    if order_qs.exists():

        order = order_qs[0]
        if order.items.filter(item__slug=item.slug).exists():

            order_item = OrderItem.objects.filter(
                item=item,
                user=request.user,
                ordered=False
            )[0]
            if order_item.quantity > 1:
                order_item.quantity -= 1
                order_item.save()

            else:
                order.items.remove(order_item)



            messages.info(request,'This item Quantitiy was updaeted..')
            return redirect('stor:Oreder-Summery')


            
        else:
            messages.info(request,'This item was not in your cart..')

            return redirect('stor:prodeuts',slug= slug)
    else:
        messages.info(request,'You dont have active order..')

        return redirect('stor:prodeuts',slug= slug)






def get_coupon(request, code):
    try:
        coupon = Coupon.objects.get(code=code)
        messages.success(request, "Successfully added coupon")
        return coupon
    except ObjectDoesNotExist:
        messages.info(request, "This coupon does not exist")
        return redirect("stor:checkout")


class add_coupon_view(View):
    def post(self, *args, **kwargs):
        form = couponFotm(self.request.POST or None)
        if form.is_valid():
            try:
                code = form.cleaned_data.get('code')
                order = Order.objects.get(
                    user=self.request.user, ordered=False)
                order.Coupon = get_coupon(self.request, code)
                order.save()
                
                return redirect("stor:checkout")
            except ObjectDoesNotExist:
                messages.info(self.request, "You do not have an active order")
                return redirect("stor:checkout")




class Refund_Request_View(View):
    def get(self, *args , **kwargs):
        form = RefundForm()
        context={'form':form}

        return render(self.request,'stor/Refund-Request.html',context)

    def post(self, *args , **kwargs):
        form =RefundForm(self.request.POST)
        if form.is_valid():
            ref_code = form.cleaned_data.get('ref_code')
            message = form.cleaned_data.get('message')
            email = form.cleaned_data.get('email')


            try:
                order = Order.objects.get(ref_code=ref_code)
                order.refund_request = True
                order.save()


                refund=Refund()
                refund.order = order
                refund.reason = message
                refund.email=email
                message.save()

                messages.info(self.request, "Your request was received.")
                return redirect('stor:Refund_Request_View')


                


            except ObjectDoesNotExist:
                messages.info(self.request,"This order is not Exisit")
                return redirect('stor:Refund_Request_View')




def get_item_queryset(query=None):
    queryset = []
    queries = query.split(" ")
   
    for word in queries: 
        products = Item.objects.filter(Q(title__icontains=word) | 
        Q(description__icontains=word) | 
        #Q(categories__icontains=word) |
        Q(price__icontains=word) | 
        Q(labals__icontains=word)   
         ).distinct()


        for item in products:
            queryset.append(item)
    return list(set(queryset))
	



ITEM_POST_PER_PAGE = 9


def home_search_view(request,*args, **kwargs):
    context = {}

    query = ""
    if request.GET:
        query = request.GET.get('q' ,'')
        context['query'] = str(query)
    item_list = sorted(get_item_queryset(query),key=attrgetter('price'),reverse=True)

    page =request.GET.get('page',1)
    item_list_paginator = Paginator(item_list,ITEM_POST_PER_PAGE)
    try:
        item_list=item_list_paginator.page(page)
    except PageNotAnInteger:
        item_list = item_list_paginator.page(ITEM_POST_PER_PAGE)
    except EmptyPage:
        item_list = item_list_paginator.page(item_list_paginator.num_pages)
    context['item_lists']=item_list
    cat_menu_list = Category.objects.all()
    context['cat_menu_list']=cat_menu_list
    

    slide_nav = slide.objects.all()
    context['Slide_Nav']=slide_nav 


    return render(request, 'stor/home-page.html',context)
"""  

def category_View(request,cats):
    category_item = Item.objects.filter(categories__categoryn=cats)


    return render(request,'stor/category.html',{'cats':cats.replace('-',' ') ,'category_item':category_item })
 """

def category_View(request,cats):

    category_item = Item.objects.filter(categories__slug=cats.replace('-',''))
    category =Category.objects.all()

    


    return render(request,'stor/category.html',{'cats':cats.title ,'category_item':category_item ,'category':category})



def category_List_View(request):
    cat_menu_list = Item.objects.all()
    
    #slides = Slidesimage.objects.all()
   
    
    return render(request,'stor/carouselpp.html',{'cat_menu_list':cat_menu_list})  


        

