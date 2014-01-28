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
    Campaign,
)


class UsersAdmin(admin.ModelAdmin):
    fields = ('first_name', 'last_name', 'email',
              'birthday', 'fbid')

    def queryset(self, request):
        return self.model.objects.filter(is_merchant=0)

admin.site.register(Users, UsersAdmin)
admin.site.register(GiftcardCategory)
admin.site.register(GiftcardDesign)
admin.site.register(Giftcard)
admin.site.register(Product)
admin.site.register(Service)
admin.site.register(Comuna)
admin.site.register(Provincia)
admin.site.register(Region)
admin.site.register(Friend)
admin.site.register(Campaign)
