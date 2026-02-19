from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.contrib import messages
from django.core.mail import send_mail
from django.conf import settings
from django.contrib.auth import login, logout
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.views import LoginView as AuthLoginView
from django.urls import reverse_lazy
from Base_App.models import BookTable, AboutUs, Feedback, ItemList, Items, Cart


# ✅ Add to cart (DB-based)
def add_to_cart(request):
    if request.method == 'POST' and request.user.is_authenticated:
        item_id = request.POST.get('item_id')
        item = get_object_or_404(Items, id=item_id)

        # Save to DB Cart model
        cart_item, created = Cart.objects.get_or_create(user=request.user, item=item)
        if not created:
            cart_item.quantity += 1
            cart_item.save()

        return JsonResponse({'message': f'{item.Item_name} added to cart'})
    else:
        return JsonResponse({'error': 'Invalid request'}, status=400)

# ✅ Get cart items (from DB)
def get_cart_items(request):
    if request.user.is_authenticated:
        cart_items = Cart.objects.filter(user=request.user).select_related('item')
        items = [
            {
                'name': cart_item.item.Item_name,
                'quantity': cart_item.quantity,
                'price': cart_item.item.Price,
                'total': cart_item.quantity * cart_item.item.Price,
            }
            for cart_item in cart_items
        ]
        return JsonResponse({'items': items})
    return JsonResponse({'error': 'User not authenticated'}, status=401)

# ✅ Login
class LoginView(AuthLoginView):
    template_name = 'login.html'
    def get_success_url(self):
        if self.request.user.is_staff:
            return reverse_lazy('admin:index')
        return reverse_lazy('Home')

# ✅ Logout
def LogoutView(request):
    logout(request)
    messages.success(request, 'You have been logged out successfully.')
    return redirect('Home')

# ✅ Signup
def SignupView(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, f'Welcome, {user.username}!')
            return redirect('Home')
        else:
            messages.error(request, 'Error during signup. Please try again.')
    else:
        form = UserCreationForm()
    return render(request, 'login.html', {'form': form, 'tab': 'signup'})

# ✅ Home
def HomeView(request):
    items = Items.objects.all()
    list = ItemList.objects.all()
    review = Feedback.objects.all().order_by('-id')[:5]
    return render(request, 'home.html', {'items': items, 'list': list, 'review': review})

# ✅ About
def AboutView(request):
    data = AboutUs.objects.all()
    return render(request, 'about.html', {'data': data})

# ✅ Menu
def MenuView(request):
    items = Items.objects.all()
    list = ItemList.objects.all()
    return render(request, 'menu.html', {'items': items, 'list': list})

# ✅ Book Table
def BookTableView(request):
    google_maps_api_key = settings.GOOGLE_MAPS_API_KEY

    if request.method == 'POST':
        name = request.POST.get('user_name')
        phone_number = request.POST.get('phone_number')
        email = request.POST.get('user_email')
        total_person = request.POST.get('total_person')
        booking_data = request.POST.get('booking_data')

        # Simple validation
        if name and phone_number and total_person and booking_data:
            data = BookTable(
                Name=name,
                Phone_number=phone_number,
                Email=email,
                Total_person=total_person,
                Booking_date=booking_data
            )
            data.save()   # ✅ NOW DATA WILL SAVE

            subject = 'Booking Confirmation'
            message = f"""Hello {name},

Your booking has been successfully received.
Total persons: {total_person}
Booking date: {booking_data}

Thank you for choosing us!
"""
            send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [email])

            messages.success(request, 'Booking request submitted successfully!')
            return redirect('Book_Table')

        else:
            messages.error(request, 'Please fill all required fields.')

    return render(request, 'book_table.html', {'google_maps_api_key': google_maps_api_key})

# ✅ Feedback
def FeedbackView(request):
    if request.method == 'POST':
        name = request.POST.get('User_name')
        feedback = request.POST.get('Description')
        rating = request.POST.get('Rating')
        image = request.FILES.get('Selfie')

        if name != '':
            feedback_data = Feedback(
                User_name=name,
                Description=feedback,
                Rating=rating,
                Image=image
            )
            feedback_data.save()

            messages.success(request, 'Feedback submitted successfully!')
            return render(request, 'feedback.html', {'success': 'Feedback submitted successfully!'})

    return render(request, 'feedback.html')






from .models import Order, OrderItem
from django.utils import timezone

def place_order(request):
    if request.method == "POST" and request.user.is_authenticated:
        cart_items = Cart.objects.filter(user=request.user)

        if not cart_items:
            return redirect('Menu')

        total = 0
        bill_items = []

        for c in cart_items:
            item_total = c.item.Price * c.quantity
            total += item_total

            bill_items.append({
                'name': c.item.Item_name,
                'qty': c.quantity,
                'price': c.item.Price,
                'total': item_total
            })

        order = Order.objects.create(
            user=request.user,
            total_amount=total
        )

        for c in cart_items:
            OrderItem.objects.create(
                order=order,
                item=c.item,
                quantity=c.quantity,
                price=c.item.Price
            )

        cart_items.delete()

        return render(request, 'order_bill.html', {
            'order': order,
            'bill_items': bill_items,
            'date': timezone.now(),
            'total': total
        })

        # 👇 Bill page par redirect
        return render(request, 'order_bill.html', {
            'order': order,
            'order_items': order.items.all(),
            'date': timezone.now()
        })
        
        
        
def checkout(request):
    if not request.user.is_authenticated:
        return redirect('login')

    cart_items = Cart.objects.filter(user=request.user)

    total = 0
    for c in cart_items:
        total += c.item.Price * c.quantity

    return render(request, 'checkout.html', {
        'cart_items': cart_items,
        'total': total
    })

