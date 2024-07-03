from .models import Flowers,Favorits,Cart,Category,Subcategory
def allcatagories(request):
    categories = Category.objects.prefetch_related('subcategories').all()
    return {'categories': categories}