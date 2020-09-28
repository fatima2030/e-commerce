from django.db import models
from django.contrib.auth.models import User
from django.conf import settings
from django.shortcuts import reverse
from django_countries.fields import CountryField
from django.conf import settings
from django.db.models.signals import post_save
from django.db.models import Sum
from django.contrib.auth.decorators import login_required
from django.dispatch import receiver
from django.utils import timezone







# Create your models here.
 
   
CAEGORY_CHOICES = (
    ('man','man'),
    ('women','women'),
    ('chiled','chiled'),
    ('sport','sport'),
   
)


LABLE_CHOICES = (
    ('P','primary'),
    ('S','secondary'),
    ('D','danger')
)
ADDRESS_CHOICES = (
    ('B','Billing'),
    ('S','shipping'),
)



class UserProfile (models.Model):
    

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    stripe_customer_id = models.CharField(max_length=50, blank=True, null=True)
    one_click_purchasing = models.BooleanField(default=False)

    def __str__(self):
        return self.user.username




class Category(models.Model): 
    categoryn = models.CharField(choices=CAEGORY_CHOICES,max_length=17)
    slug = models.SlugField(max_length=50)
    parent = models.ForeignKey('self',blank=True,null=True,on_delete=models.SET_NULL,related_name='children')

   
   
    def __str__(self):
        full_path = [self.categoryn]
        k = self.parent

        while k is not None:

            full_path.append(k.categoryn)
            k=k.parent
        return ' -> '.join(full_path[::-1]) 


    @property
    def is_parent(self):
        if self.parent is not None:
            return False
        return True
    def __str__(self):
        return self.categoryn


class Item(models.Model):
    title = models.CharField(max_length=200,null=True)
    price = models.FloatField()
    discount_price = models.FloatField(null=True,blank=True)
    image = models.ImageField(null=True)
    categories = models.ForeignKey(Category ,null=True,blank=True , on_delete=models.SET_NULL,related_name='cates') 
    labals = models.CharField(choices=LABLE_CHOICES,max_length=17 ,null=True,blank=True)
    slug   =   models.SlugField(max_length=255, unique=True,)
    description = models.TextField()


    def __str__(self):
        return self.title 


    def get_absolute_url(self):
        return reverse('stor:prodeuts' ,kwargs={
            'slug' : self.slug
        })

    def get_add_to_cart_url(self):
        return reverse('stor:add_to_cart',kwargs={
            'slug' : self.slug
        })
   
    def get_remove_from_cart_url(self):
        return reverse("stor:remove_from_cart", kwargs={
            'slug': self.slug
        })

    def get_cat_list(self):
        k= self.categories
        breadcrumb = ['dummy']

        while k is not None:
            breadcrumb.append(k.slug)
            k = k.parent
        for i in range(len(breadcrumb)-1):
            breadcrumb[i] = '/'.join(breadcrumb[-1:i-1:-1])
        return breadcrumb[-1:0:-1]

class slide(models.Model):
    ads = models.CharField(max_length=200,null=True)
    image = models.ImageField(null=True)


    def __str__(self):
        return self.ads 





class OrderItem(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.CASCADE)
    ordered = models.BooleanField(default=False,null=True,blank=True)

    item = models.ForeignKey(Item,on_delete=models.CASCADE)
    quantity = models.IntegerField(default=1)

    def __str__(self):
        return f"{self.quantity} of {self.item.title}"

    def get_total_item_price(self):
        return self.quantity * self.item.price


    def get_total_discount_item_price(self):
        return self.quantity * self.item.discount_price

    def get_amount_saved(self):

        return self.get_total_item_price() - self.get_total_discount_item_price()

    def get_final_price(self):
        if self.item.discount_price:
            return self.get_total_discount_item_price()
        return self.get_total_item_price()








   


class Order(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.CASCADE)
    red_code = models.CharField(max_length=20,null=True,blank=True)
    start_date = models.DateTimeField(auto_now_add=True)
    order_date = models.DateTimeField()

    ordered = models.BooleanField(default=False,null=True,blank=True)
    items = models.ManyToManyField(OrderItem)
    billing_address = models.ForeignKey('Address', on_delete=models.SET_NULL, blank=True,null=True,related_name='billing_address')
    shipping_address = models.ForeignKey('Address', on_delete=models.SET_NULL, blank=True,null=True ,related_name='shipping_address')
 
    payment = models.ForeignKey('Payment', on_delete=models.SET_NULL, blank=True,null=True)
    coupon = models.ForeignKey('Coupon', on_delete=models.SET_NULL, blank=True,null=True)
    Bing_deliverd = models.BooleanField(default=False,null=True,blank=True)
    recived = models.BooleanField(default=False,null=True,blank=True)
    refund_request = models.BooleanField(default=False,null=True,blank=True)
    refund_granted = models.BooleanField(default=False,null=True,blank=True)






    def __str__(self):
        return self.user.username

    def get_total(self):
        total = 0
        for order_item in self.items.all():
            total += order_item.get_final_price()

        if self.coupon:
            total -= self.coupon.amount
        return total


class Address(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL,
                             on_delete=models.CASCADE)
    street_address = models.CharField(max_length=100)
    apartment_address = models.CharField(max_length=100)
    country = CountryField(multiple=False)
    zip = models.CharField(max_length=100)
    address_type = models.CharField(max_length=1, choices=ADDRESS_CHOICES)
    default = models.BooleanField(default=False)

    def __str__(self):
        return self.user.username

    class Meta:
        verbose_name_plural = 'Addresses'


class Payment(models.Model):
    stripe_charge_id= models.CharField(max_length=50)
    user = models.ForeignKey(settings.AUTH_USER_MODEL,
                             on_delete=models.SET_NULL, blank=True, null=True)    
    amount = models.FloatField()
    timstamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.user.username



class Coupon(models.Model):
    code = models.CharField(max_length=15)
    amount = models.FloatField()
    num =models.CharField(max_length=15)
    num1 =models.CharField(max_length=15)

    num2 =models.CharField(max_length=15)

    num3 =models.CharField(max_length=15)
    num4 =models.CharField(max_length=15)


    def __str__(self):
        return self.code


class Refund(models.Model):
    order = models.ForeignKey(Order,on_delete=models.CASCADE)
    reason = models.TextField()
    accepted = models.BooleanField(default=False)
    email = models.EmailField(default=True)

    def __str__(self):
        return f"{self.pk}"

@receiver(post_save,sender=User,dispatch_uid='save_new_user_profile')
def save_profile(sender, instance, created, **kwargs):
    user=instance
    if created:
        userprofile=UserProfile(user=user)
        userprofile.save



#post_save.connect(userprofile_receiver, sender=settings.AUTH_USER_MODEL)






