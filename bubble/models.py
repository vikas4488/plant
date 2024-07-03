from django.db import models
from django.contrib.auth.models import User
from datetime import datetime 

class Category(models.Model):
    name = models.CharField(max_length=255)
    def __str__(self):
        return self.name
    class Meta:
            db_table = 'aa_category'
class Subcategory(models.Model):
    name = models.CharField(max_length=255)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='subcategories')
    def __str__(self):
        return self.name
    class Meta:
        db_table = 'aa_subcategory'
class Flowers(models.Model):
    name = models.CharField(max_length=200)
    imagetitle = models.CharField(max_length=200)
    image = models.ImageField(upload_to='flowerimages')
    details = models.CharField(max_length=400)
    price=models.IntegerField()
    offvalue=models.FloatField()
    cats=models.ForeignKey(Category, on_delete=models.CASCADE,default=3)
    subcat=models.ForeignKey(Subcategory,on_delete=models.CASCADE,default=2)
    adddate = models.DateField(default=datetime.now, blank=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.name
    class Meta:
        db_table = 'aa_flowers'  # Set a custom table name
class Favorits(models.Model):
    userob = models.ForeignKey(User, on_delete=models.CASCADE)
    flowerob = models.ForeignKey(Flowers, on_delete=models.CASCADE)
    adddate = models.DateField(default=datetime.now, blank=True)

    def __str__(self):
        return "fav "+str(self.adddate)
    class Meta:
        db_table = 'aa_fav'
class Cart(models.Model):
    userob = models.ForeignKey(User, on_delete=models.CASCADE)
    flowerob = models.ForeignKey(Flowers, on_delete=models.CASCADE)
    adddate = models.DateField(default=datetime.now, blank=True)
    quantity=models.IntegerField(default=1)

    def __str__(self):
        return "cart "+str(self.adddate)
    class Meta:
        db_table = 'aa_cart'

class Transection(models.Model):
    userob = models.ForeignKey(User, on_delete=models.CASCADE)
    transectiondate = models.DateTimeField(default=datetime.now, blank=True)
    statusCode = models.CharField(max_length=400)
    transactionId = models.CharField(max_length=400)
    providerReferenceId = models.CharField(max_length=400)
    amount=models.FloatField()
    def __str__(self):
        return "transection "+str(self.transectiondate)
    class Meta:
        db_table = 'aa_transection'
class MyOrders(models.Model):
    userob = models.ForeignKey(User, on_delete=models.CASCADE)
    flowerob = models.ForeignKey(Flowers, on_delete=models.CASCADE)
    transactionId = models.CharField(max_length=400)
    orderDate = models.DateTimeField(default=datetime.now, blank=True)
    quantity=models.IntegerField(default=1)
    amount=models.FloatField()
    offvalue=models.FloatField()
    def __str__(self):
        return "transection "+str(self.transactionId)
    class Meta:
        db_table = 'aa_myorder'
