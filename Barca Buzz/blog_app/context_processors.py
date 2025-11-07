from .models import Category

def global_categories(request):
    try:
        return {'categories': Category.objects.all()}
    except Exception:
        return {'categories': []}
