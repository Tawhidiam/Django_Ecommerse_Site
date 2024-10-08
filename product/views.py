from django.db.models import Q
from django.shortcuts import render
from django.views import generic
from .models import Category,Product,Slider
from cart.carts import Cart
from django.core.paginator import InvalidPage,Paginator,EmptyPage,PageNotAnInteger
# Create your views here.

class Home(generic.TemplateView):
    template_name = 'home.html'
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(
            {
                "featured_categories": Category.objects.filter(featured=True),
                "featured_products": Product.objects.filter(featured=True),
                "sliders": Slider.objects.filter(show=True)
            }
        )
        return context


class ProductDetails(generic.DetailView):
    model = Product
    template_name = 'product/product-details.html'
    slug_url_kwarg = 'slug'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['related_products'] = self.get_object().related
        return context

class CategorytDetails(generic.DetailView):
    model = Category
    template_name = 'product/category-details.html'
    slug_url_kwarg = 'slug'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['products'] = self.get_object().products.all()
        return context

class CustomPaginator:
    def __init__(self, request, queryset, paginated_by) -> None:
        self.paginator = Paginator(queryset,paginated_by)
        self.paginated_by = paginated_by
        self.queryset = queryset
        self.page = request.GET.get('page',1)
        # queryset = Product.objects.all()  # Replace with your product queryset
        # self.paginator = Paginator(queryset, per_page=5)  # 5 items per page


    def get_queryset(self):
        try:
            queryset = self.paginator.page(self.page)
        except PageNotAnInteger:
            queryset = self.paginator.page(1)
        except EmptyPage:
            queryset = self.paginator.page(1)
        except InvalidPage:
            queryset = self.paginator.page(1)
        
        return queryset

class ProductList(generic.ListView):
    model = Product
    template_name = 'product/product-list.html'
    context_object_name = 'obj_list'
    paginate_by = 4



    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        page_obj = CustomPaginator( self.request, self.get_queryset(), self.paginate_by )
        paginator = page_obj.paginator
        queryset = page_obj.queryset
        context['obj_list'] = queryset
        context['paginator'] = paginator
        return context

class SearchProducts(generic.View):
    def get(self, *args, **kwargs):
        key = self.request.GET.get('key','')
        products = Product.objects.filter(
            Q(title__icontains=key) |
            Q(category__title__icontains=key)
        )
        context={
            "products":products,
            "key":key
        }
        return render(self.request, 'product/search-products.html',context)