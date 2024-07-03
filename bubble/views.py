from django.shortcuts import render,redirect,get_object_or_404
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from .models import Flowers,Favorits,Cart,Category,Subcategory,MyOrders,Transection
from django.contrib import messages
from django.contrib.auth import login, authenticate, logout
from .forms import LoginForm, SignupForm
from django.contrib.auth.models import User
from django.db.models import OuterRef, Subquery,Exists,When,Value,Case,CharField
from django.http import HttpResponse,HttpResponseBadRequest,JsonResponse
from django.db import models
from django.db.models import F, ExpressionWrapper, DecimalField,Sum,Q
from decimal import Decimal
from django.views.decorators.csrf import csrf_protect
from django.core.files.storage import FileSystemStorage
import requests
import hashlib
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.backends import default_backend
import jsons
import shortuuid
import base64
import time
import json
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
import os
from collections import defaultdict
from .phonepe import makepayment,phonepecallback
# Create your views here.
def index(request):
    return render(request,"test.html")

def testhome(request):
    return render(request,"testhome.html")
def flowerhome(request):
    catss=""
    subcatss=""
    category_id=request.GET.get('catId','')
    query =request.GET.get('q','')
    subcategory_id=request.GET.get('subcatId','')
    userid=request.user.id
    print(f"query is here {query}")
    fav_subquery=Favorits.objects.filter(userob_id=userid,flowerob_id=OuterRef('pk'))
    cart_subquery=Cart.objects.filter(userob_id=userid,flowerob_id=OuterRef('pk'))
    if query:
        print("hit 1")
        flowerList = Flowers.objects.filter( Q(name__icontains=query) | Q(details__icontains=query)).annotate(is_favorite=Case(When(Exists(fav_subquery),
                    then=Value("liked")),default=Value("not_liked"),output_field=CharField()),
                    is_carted=Case(When(Exists(cart_subquery),
                    then=Value("carted")),default=Value("not_carted"),output_field=CharField()),
                    new_price=F('price') * (1 - F('offvalue') / 100)
                    )
        query="q="+query+"&"
    elif category_id:
        print("hit 2")
        catss=Category.objects.get(id=category_id)
        flowerList = Flowers.objects.filter(cats__id=category_id).annotate(is_favorite=Case(When(Exists(fav_subquery),
                    then=Value("liked")),default=Value("not_liked"),output_field=CharField()),
                    is_carted=Case(When(Exists(cart_subquery),
                    then=Value("carted")),default=Value("not_carted"),output_field=CharField()),
                    new_price=F('price') * (1 - F('offvalue') / 100)
                    )
        category_id="catId="+category_id +"&"
    elif subcategory_id:
        print("hit 3")
        subcatss=Subcategory.objects.get(id=subcategory_id)
        catss=subcatss.category
        flowerList = Flowers.objects.filter(subcat__id=subcategory_id).annotate(is_favorite=Case(When(Exists(fav_subquery),
                    then=Value("liked")),default=Value("not_liked"),output_field=CharField()),
                    is_carted=Case(When(Exists(cart_subquery),
                    then=Value("carted")),default=Value("not_carted"),output_field=CharField()),
                    new_price=F('price') * (1 - F('offvalue') / 100)
                    )
        subcategory_id="subcatId="+subcategory_id +"&"
    else:
        print("hit 4")
        flowerList = Flowers.objects.annotate(is_favorite=Case(When(Exists(fav_subquery),
                then=Value("liked")),default=Value("not_liked"),output_field=CharField()),
                is_carted=Case(When(Exists(cart_subquery),
                then=Value("carted")),default=Value("not_carted"),output_field=CharField()),
                new_price=F('price') * (1 - F('offvalue') / 100)
                )
    p = Paginator(flowerList, 1)
    page_number = request.GET.get('page','')
    try:
        page_obj = p.get_page(page_number)  # returns the desired page object
    except PageNotAnInteger:
        # if page_number is not an integer then assign the first page
        page_obj = p.page(1)
    except EmptyPage:
        # if page is empty then return last page
        page_obj = p.page(p.num_pages)
    subquery=query+category_id+subcategory_id
    context = {'page_obj': page_obj,'catss':catss,'subcatss':subcatss,'subquery':subquery}
    
    return render(request,"flowerhome.html",context)
@csrf_protect
def newsignup(request):
    message={"text":"signup bad request","color_code":"danger"}
    if request.method == 'POST':
        uname = request.POST.get('sigup_username')
        fname = request.POST.get('sigup_fname')
        lname = request.POST.get('sigup_lname')
        email = request.POST.get('sigup_email')
        pass1 = request.POST.get('sigup_password')
        pass2 = request.POST.get('sigup_password2')
        if(uname==""):
            message={"text":"username should not be empty","color_code":"warning"}
        elif(pass1=="" or pass2==""):
            message={"text":"password should not be empty","color_code":"warning"}
        elif(fname==""):
            message={"text":"first name should not be empty","color_code":"warning"}
        elif(lname==""):
            message={"text":"lastname should not be empty","color_code":"warning"}
        elif(email==""):
            message={"text":"email should not be empty","color_code":"warning"}
        else:
            if(pass1==pass2):
                existing_user = User.objects.filter(username=uname).exists()
                if(existing_user):
                    message={"text":"user already exist with this user name","color_code":"warning"}
                else:
                    existing_email_user = User.objects.filter(email=email).exists()
                    if(existing_email_user):
                        message={"text":"email already exist with different user","color_code":"warning"}
                    else:
                        user=User.objects.create()
                        user.username=uname
                        user.first_name=fname
                        user.last_name=lname
                        user.email=email
                        user.set_password(pass1)
                        user.save()
                        message={"text":"signup successfully please login","color_code":"success"}
                        print("user registered")
            else:
                message={"text":"both password should be same","color_code":"danger"}
    context = {'message': message,'openpopup':'regpopup'}
    ##return render(request,"flowerhome.html",context)
    return JsonResponse(context)
@csrf_protect
def newlogin(request):
    message={"text":"login bad request","color_code":"danger"}
    if request.method == 'POST':
        username = request.POST.get('sigin_username')
        password = request.POST.get('sigin_password')
        if(username==""):
            message={"text":"username should not be empty","color_code":"warning"}
        elif(password==""):
            message={"text":"password should not be empty","color_code":"warning"}
        else:
            user = authenticate(request, username=username, password=password)
            if user:
                login(request, user)    
                message={"text":"logged in successfully","color_code":"success"}
            else:
                existing_user = User.objects.filter(username=username).exists()
                if existing_user:
                    message={"text":"password incorrect","color_code":"danger"}
                else:                           
                    message={"text":"user does not exist","color_code":"warning"}
    context = {'message': message,'openpopup':'loginpopup'}
    return JsonResponse(context)
            
# signup page
def user_signup(request):
    if request.method == 'POST':
        form = SignupForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('login')
    else:
        form = SignupForm()
    return render(request, 'signup.html', {'form': form})

# login page
def user_login(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(request, username=username, password=password)
            if user:
                login(request, user)    
                return redirect('flowerhome')
    else:
        form = LoginForm()
    return render(request, 'login.html', {'form': form})

# logout page
@login_required
def user_logout(request):
    logout(request)
    return redirect('flowerhome')

def favurl(request):
    message="unknown"
    if(request.user.is_authenticated):
        if request.method == 'POST':
            ##userob = request.POST.get('plantob')
            flowerob_id = request.POST.get('flowerob_id')
            userob_id = request.user.id
            fav, created = Favorits.objects.get_or_create(flowerob_id=flowerob_id,userob_id=userob_id)
            if(created):
                message="liked"
            else:
                fav.delete()
                message="like_removed"
    else:
        message="not_loggedin"
    context = {'message':message}
    return JsonResponse(context)

def carturl(request):
    message="unknown"
    if(request.user.is_authenticated):
        if request.method == 'POST':
            ##userob = request.POST.get('plantob')
            flowerob_id = request.POST.get('flowerob_id')
            userob_id = request.user.id
            cart, created = Cart.objects.get_or_create(flowerob_id=flowerob_id,userob_id=userob_id)
            if(created):
                message="carted"
            else:
                cart.delete()
                message="carted_removed"
            context = {'message':message}
            return JsonResponse(context)
    else:
        message="not_loggedin"
        context = {'message':message}
    return JsonResponse(context)
##cartpage
@login_required
def cart(request):
    message="unknown"
    if(request.user.is_authenticated):
        userid=request.user.id
        # Calculate new price as price - (price * offpercentage / 100)
        item_total=ExpressionWrapper(
        (F('flowerob__price') - (F('flowerob__price') * F('flowerob__offvalue') / 100))*F('quantity'),
        output_field=DecimalField(max_digits=10, decimal_places=2))
        new_price_expression = ExpressionWrapper(
        F('flowerob__price') - (F('flowerob__price') * F('flowerob__offvalue') / 100),output_field=DecimalField(max_digits=10, decimal_places=2))
        carts=Cart.objects.filter(userob_id=userid).select_related('flowerob').annotate(newprice=new_price_expression).annotate(itemtotal=item_total)
        # Calculate total price
        total_price = carts.aggregate(total=Sum('itemtotal'))['total']
        context={'carts':carts,'total_price':total_price}
        return render(request,"cart.html",context)
    else:
        message="not_loggedin"
        context = {'message':message}
    return JsonResponse(context)
@login_required
@require_POST
def updateCart(request):
    message="unknown"
    if(request.user.is_authenticated):
        userid=request.user.id
        doaction = request.POST.get('doaction')
        flowerId = request.POST.get('flowerId')
        try:
            cart_item = get_object_or_404(Cart, userob_id=userid, flowerob_id=flowerId)
            if doaction == 'plus':
                cart_item.quantity += 1
                cart_item.save()
                response = {'status': 'success', 'new_quantity': cart_item.quantity}
            elif doaction == 'minus':
                if(cart_item.quantity>1):
                    cart_item.quantity -= 1
                    cart_item.save()
                    response = {'status': 'success', 'new_quantity': cart_item.quantity}
                response = {'status': 'success', 'new_quantity': cart_item.quantity}
            else:
                response = {'status': 'failure', 'message': 'Invalid action'}
        except Cart.DoesNotExist:
            response = {'status': 'failure', 'message': 'Cart item does not exist'}
    else:
        message="not_loggedin"
        response = {'message':message}
    return JsonResponse(response)

@login_required
def favpage(request):
    message="unknown"
    if(request.user.is_authenticated):
        userid=request.user.id
        cart_subquery=Cart.objects.filter(userob_id=userid,flowerob_id=OuterRef('flowerob_id'))
        ##cart_subquery=Cart.objects.filter(userob_id=userid,flowerob_id=OuterRef('pk'))
        favs=Favorits.objects.filter(userob_id=userid).select_related('flowerob').annotate(is_carted=Case(When(Exists(cart_subquery),
                then=Value("carted")),default=Value("not_carted"),output_field=CharField()))
        p = Paginator(favs, 2)
        page_number = request.GET.get('page')
        try:
            page_obj = p.get_page(page_number)  # returns the desired page object
        except PageNotAnInteger:
            # if page_number is not an integer then assign the first page
            page_obj = p.page(1)
        except EmptyPage:
            # if page is empty then return last page
            page_obj = p.page(p.num_pages)
        context = {'page_obj': page_obj}
        return render(request,"favpage.html",context)
    else:
        message="not_loggedin"
        context = {'message':message}
    return JsonResponse(context)

@login_required
def uploadPlants(request):
    message="unknown"
    if(request.user.is_authenticated):
        if request.method == 'POST':
            name = request.POST.get('name')
            image = request.POST.get('image')
            myfile = request.FILES.get('image') if 'image' in request.FILES else None
            details = request.POST.get('details')
            price = request.POST.get('price')
            offvalue = request.POST.get('offvalue')
            cats = request.POST.get('cats')
            subcat = request.POST.get('subcat')
            adddate = request.POST.get('adddate')
            is_active = request.POST.get('is_active')

            # Validation flags and messages
            errors = []
            if not name:
                errors.append("Name is required.")
            if not myfile:
                errors.append("Image file is required.")
            if not details:
                errors.append("Details are required.")
            try:
                price = float(price)
                if price <= 0:
                    errors.append("Price must be a positive number.")
            except (TypeError, ValueError):
                errors.append("Invalid price format.")
            try:
                offvalue = float(offvalue)
                if offvalue < 0:
                    errors.append("Offvalue must be a non-negative number.")
            except (TypeError, ValueError):
                errors.append("Invalid offvalue format.")
            if not cats:
                errors.append("Category is required.")
            if not subcat:
                errors.append("Subcategory is required.")
            try:
                from datetime import datetime
                adddate = datetime.strptime(adddate, '%Y-%m-%d')
            except ValueError:
                errors.append("Invalid date format. Use YYYY-MM-DD.")
            if is_active not in ['True', 'False']:
                errors.append("Is_active must be 'True' or 'False'.")
            if errors:
                return render(request, "uploadplants.html", {'message': 'Error', 'errors': errors})

            custom_directory = 'flowerimages/'
            custom_path = os.path.join(settings.MEDIA_ROOT, custom_directory)
            if not os.path.exists(custom_path):
                os.makedirs(custom_path)
            fs = FileSystemStorage(location=custom_path, base_url=os.path.join(settings.MEDIA_URL, custom_directory))
            filename = fs.save(myfile.name, myfile)
            uploaded_file_url = fs.url(filename).strip('media/')
            
            flower = Flowers.objects.create(name=name,imagetitle=name,image=uploaded_file_url,details=details,
                                            cats_id=cats,subcat_id=subcat,
                                             price=price,offvalue=offvalue,adddate=adddate,is_active=is_active)
           
        return render(request,"uploadplants.html",{'message':'success'})
    else:
        return redirect('flowerhome')


@login_required
def getSubCat(request):
    catid = request.POST.get('catid')
    subCats=Subcategory.objects.filter(category_id=catid).all()
    subCats_list = list(subCats.values())
    context = {'subCats': subCats_list}
    return JsonResponse(context)
@login_required
def geCat(request):
    cats=Category.objects.all()
    cats_list = list(cats.values())
    ##print(cats_list)
    context = {'cats': cats_list}
    return JsonResponse(context)
@login_required
def plantDetails(request):
    if request.method == 'POST':
        flowerid = request.POST.get('flowerid')
        userid=request.user.id
        print(flowerid)
        print(userid)
        fav_subquery=Favorits.objects.filter(userob_id=userid,flowerob_id=OuterRef('pk'))
        cart_subquery=Cart.objects.filter(userob_id=userid,flowerob_id=OuterRef('pk'))
        flower = Flowers.objects.annotate(is_favorite=Case(When(Exists(fav_subquery),
                then=Value("liked")),default=Value("not_liked"),output_field=CharField()),
                is_carted=Case(When(Exists(cart_subquery),
                then=Value("carted")),default=Value("not_carted"),output_field=CharField()),
                new_price=F('price') * (1 - F('offvalue') / 100)
                ).get(id=flowerid)##this gate should be written at last to get the unique result
        print(flower)
        context = {'flower': flower}
    return render(request,"plantDetails.html",context)

def checkout(request):
    return makepayment(request)
def custom_404(request):
    return render(request, '404.html')
@csrf_exempt
def callback(request):
    return phonepecallback(request)
@login_required
def myorders(request):
    userid=request.user.id
    # Calculate new price as price - (price * offpercentage / 100)
    item_total=ExpressionWrapper(
    (F('amount') - (F('amount') * F('offvalue') / 100))*F('quantity'),
    output_field=DecimalField(max_digits=10, decimal_places=2))
    new_price_expression = ExpressionWrapper(
    F('amount') - (F('amount') * F('offvalue') / 100),output_field=DecimalField(max_digits=10, decimal_places=2))
    # Calculate total price
    orders = MyOrders.objects.filter(userob_id=userid).select_related('flowerob') \
        .annotate(newprice=new_price_expression, itemtotal=item_total).order_by('-orderDate')
        #.values('transactionId', 'newprice', 'itemtotal', 'quantity')
    #print(f"init orders is {orders}")
    grouped_orders = defaultdict(lambda: {'tritems': [], 'total_discounted_price': Decimal('0.00'),
                                          'total_mrp': float('0.00'),
                                          'total_discount': float('0.00'),
                                           'status': None,'transectiondate':None})

    for order in orders:
        transaction_id = order.transactionId
        status="unknown"
        transectiondate=""
        try:
            trob=Transection.objects.get(transactionId=transaction_id)
            transectiondate=trob.transectiondate
            if(trob.statusCode=="PAYMENT_SUCCESS"):
                status="payment done online successfully"
            else:
                status=trob.statusCode
        except Transection.DoesNotExist:
            status="no payment found please contact seller"
        print(f"Flower ID: {order.flowerob.id}")
    # We have no object! Do something...
        grouped_orders[transaction_id]['status']=status
        grouped_orders[transaction_id]['transectiondate']=transectiondate
        grouped_orders[transaction_id]['tritems'].append({
            'newprice': order.newprice,
            'itemtotal': order.itemtotal,
            'quantity': order.quantity,
            'offvalue':order.offvalue,
            'amount':order.amount,
            'flower': {
                'name': order.flowerob.name,
                'id': order.flowerob.id,
                'image': order.flowerob.image.url,
                'details': order.flowerob.details,
            }
        })
        grouped_orders[transaction_id]['total_discounted_price'] += ((order.newprice) * (order.quantity))
        grouped_orders[transaction_id]['total_mrp'] += ((order.amount) * (order.quantity))
        grouped_orders[transaction_id]['total_discount'] += (((order.amount)*(order.offvalue)/100) * (order.quantity))

    # Convert the grouped_orders to a list for the context
    grouped_orders_list = [{'transactionId': k, **v} for k, v in grouped_orders.items()]


    #print(grouped_orders_list)
    #total_price = orders.aggregate(total=Sum('itemtotal'))['total']
    context={'orders':grouped_orders_list}
    return render(request,"myorders.html",context)