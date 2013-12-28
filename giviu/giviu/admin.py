from django.contrib import admin
from models import (
    Users,
    GiftcardCategory,
    GiftcardDesign,
    Giftcard,
    Product,
    Service,
    Comuna,
    Provincia,
    Region,
    Friend,
    Likes,
    MerchantTabs,
    MerchantUsers,
    Merchants
)


admin.site.register(Users)
admin.site.register(GiftcardCategory)
admin.site.register(GiftcardDesign)
admin.site.register(Giftcard)
admin.site.register(Product)
admin.site.register(Service)
admin.site.register(Comuna)
admin.site.register(Provincia)
admin.site.register(Region)
admin.site.register(Friend)
admin.site.register(Likes)
admin.site.register(MerchantTabs)
admin.site.register(MerchantUsers)
admin.site.register(Merchants)
