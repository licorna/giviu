from django.contrib import admin
from django.contrib.auth.hashers import make_password
from .models import Merchants, MerchantTabs
from giviu.models import Users
from hashlib import sha224


class UsersProxy(Users):
    class Meta:
        proxy = True
        verbose_name_plural = 'Merchant Users'
        verbose_name = 'Merchant User'


class MerchantUserAdmin(admin.ModelAdmin):
    fields = ('first_name', 'last_name', 'email', 'merchant', 'password')

    def save_model(self, request, obj, form, change):
        obj.is_merchant = 1
        if change:
            user = Users.objects.get(pk=obj.id)
            if 'password' in form.changed_data:
                obj.set_password(obj.password)
            else:
                obj.password = user.password
        else:
            obj.set_password(obj.password)
            obj.fbid = sha224(obj.email + '.' + obj.password).hexdigest()

        obj.save()

    def queryset(self, request):
        return self.model.objects.filter(is_merchant=1)


admin.site.register(Merchants)
admin.site.register(MerchantTabs)
admin.site.register(UsersProxy, MerchantUserAdmin)
