from django.contrib import admin
from models import (
    Users,
    GiftcardCategory,
    GiftcardDesign,
    GiftcardMedia,
    Giftcard,
    Product,
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
admin.site.register(GiftcardMedia)
admin.site.register(Giftcard)
admin.site.register(Product)
admin.site.register(Campaign)
