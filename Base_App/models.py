from django.db import models
from django.contrib.auth.models import User

# ✅ Category Model
class ItemList(models.Model):
    Category_name = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return self.Category_name
    

# ✅ Items Model
class Items(models.Model):
    Item_name = models.CharField(max_length=100)
    description = models.TextField()
    Price = models.DecimalField(max_digits=10, decimal_places=2)  # 💡 More precise than Integer
    Category = models.ForeignKey(ItemList, related_name='items', on_delete=models.CASCADE)
    Image = models.ImageField(upload_to='items/')

    def __str__(self):
        return self.Item_name


# ✅ About Us (CMS text)
class AboutUs(models.Model):
    Description = models.TextField()

    def __str__(self):
        return f"AboutUs (id={self.id})"


# ✅ Feedback / Reviews
class Feedback(models.Model):
    User_name = models.CharField(max_length=50)
    Description = models.TextField()
    Rating = models.PositiveIntegerField()  # Ensures only +ve values
    Image = models.ImageField(upload_to='feedback/', blank=True, null=True)

    def __str__(self):
        return f"{self.User_name} - {self.Rating}★"


# ✅ Table Booking
class BookTable(models.Model):
    Name = models.CharField(max_length=50)
    Phone_number = models.CharField(max_length=15)  # 💡 string so country code store thai shake
    Email = models.EmailField()
    Total_person = models.PositiveIntegerField()
    Booking_date = models.DateField()

    def __str__(self):
        return f"{self.Name} ({self.Total_person} persons)"


# ✅ Cart
class Cart(models.Model):
    user = models.ForeignKey(User, related_name='cart', on_delete=models.CASCADE)
    item = models.ForeignKey(Items, related_name='cart_items', on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)

    def __str__(self):
        return f"{self.user.username} - {self.item.Item_name} ({self.quantity})"

    # 💡 Helper method for cart total price
    @property
    def total_price(self):
        return self.quantity * self.item.Price







class Order(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    total_amount = models.IntegerField()
    status = models.CharField(max_length=20, default="Pending")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Order {self.id} - {self.user.username}"

class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="items")
    item = models.ForeignKey(Items, on_delete=models.CASCADE)
    quantity = models.IntegerField(default=1)
    price = models.IntegerField()

    def __str__(self):
        return self.item.Item_name
