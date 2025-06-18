from django.shortcuts import redirect, render, get_object_or_404
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db.models import Q, Avg, Count
from .models import Product, Category
from apps.cart.forms import CartAddProductForm

def product_list(request, category_slug=None):
    category = None
    categories = Category.objects.all()
    products = Product.objects.filter(available=True)
    
    # Filter by category
    if category_slug:
        category = get_object_or_404(Category, slug=category_slug)
        products = products.filter(category=category)

    # Search functionality
    search_query = request.GET.get('search', '')
    if search_query:
        products = products.filter(
            Q(name__icontains=search_query) | 
            Q(description__icontains=search_query) |
            Q(ingredients__icontains=search_query)
        ).distinct()

    # Category Filter
    selected_category = request.GET.get('category')
    if selected_category:
        products = products.filter(category_id=selected_category)

    # Sorting
    sort_by = request.GET.get('sort', 'name')
    if sort_by == 'price_low':
        products = products.order_by('price')
    elif sort_by == 'price_high':
        products = products.order_by('-price')
    elif sort_by == 'newest':
        products = products.order_by('-created_at')
    elif sort_by == 'name':
        products = products.order_by('name')

    # Pagination
    paginator = Paginator(products, 12)  # Show 12 products per page
    page = request.GET.get('page')
    
    try:
        products = paginator.page(page)
    except PageNotAnInteger:
        products = paginator.page(1)
    except EmptyPage:
        products = paginator.page(paginator.num_pages)
    
    context = {
        'category': category,
        'categories': categories,
        'products': products,
        'search_query': search_query,
        'sort_by': sort_by,
        'selected_category': selected_category,
    }
    
    return render(request, 'products/product_list.html', context)

def product_detail(request, id, slug):
    product = get_object_or_404(Product, id=id, slug=slug, available=True)
    
    # Get product images
    product_images = product.images.all()
    
    # Get reviews with statistics
    reviews = product.reviews.all()[:10]  # Show latest 10 reviews
    review_stats = product.reviews.aggregate(
        avg_rating=Avg('rating'),
        total_reviews=Count('id')
    )
    
    # Get related products (same category, excluding current product)
    related_products = Product.objects.filter(
        category=product.category,
        available=True
    ).exclude(id=product.id)[:4]
    
    # Get recommended products (featured products if no related products)
    if not related_products.exists():
        related_products = Product.objects.filter(
            featured=True,
            available=True
        ).exclude(id=product.id)[:4]
    
    cart_product_form = CartAddProductForm()
    
    context = {
        'product': product,
        'product_images': product_images,
        'reviews': reviews,
        'review_stats': review_stats,
        'related_products': related_products,
        'cart_product_form': cart_product_form,
    }
    
    return render(request, 'products/product_detail.html', context)

def search_products(request):
    query = request.GET.get('q', '')
    products = []
    
    if query:
        products = Product.objects.filter(
            Q(name__icontains=query) | 
            Q(description__icontains=query) |
            Q(short_description__icontains=query) |
            Q(ingredients__icontains=query),
            available=True
        ).distinct()
    
    # Pagination for search results
    paginator = Paginator(products, 12)
    page = request.GET.get('page')
    
    try:
        products = paginator.page(page)
    except PageNotAnInteger:
        products = paginator.page(1)
    except EmptyPage:
        products = paginator.page(paginator.num_pages)
    
    context = {
        'products': products,
        'query': query,
        'total_results': products.paginator.count if products else 0,
    }
    
    return render(request, 'products/search_results.html', context)

def cart_add(request, product_id):
    # Get the product by ID
    product = get_object_or_404(Product, id=product_id)
    
    # Here you would add logic to add the product to the user's cart
    # For example, you might use session to manage cart items
    cart = request.session.get('cart', {})
    cart[product_id] = cart.get(product_id, 0) + 1  # Increment quantity
    request.session['cart'] = cart

    # Redirect to the product detail page or cart page
    return redirect('products:product_detail', id=product.id, slug=product.slug)