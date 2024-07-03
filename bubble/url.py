
from django.urls import path,include
from bubble import views
urlpatterns = [
    path('',views.index,name="index"),
    path('testhome',views.testhome,name="testhome"),
    path('flowerhome',views.flowerhome,name="flowerhome"),
    path('login/', views.user_login, name='login'),
    path('signup/', views.user_signup, name='signup'),
    path('newlogin', views.newlogin, name='newlogin'),
    path('newsignup', views.newsignup, name='newsignup'),
    path('logout/', views.user_logout, name='logout'),
    path('favurl', views.favurl, name='favurl'),
    path('carturl', views.carturl, name='carturl'),
    path('cart', views.cart, name='cart'),
    path('updateCart', views.updateCart, name='updateCart'),
    path('favpage', views.favpage, name='favpage'),
    path('uploadPlants', views.uploadPlants, name='uploadPlants'),
    path('getSubCat', views.getSubCat, name='getSubCat'),
    path('geCat', views.geCat, name='geCat'),
    path('plantDetails', views.plantDetails, name='plantDetails'),
    path('checkout/', views.checkout, name='checkout'),
    path('callback/', views.callback, name='callback'),
    path('myorders', views.myorders, name='myorders'),
    path('test-404/', views.custom_404,name='custom_404'),
    
]