from django.contrib import admin
from django.contrib.auth.hashers import make_password
from .models import Merchants, MerchantTabs
from giviu.models import Users
from api.models import ApiClientId
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


class MerchantAdmin(admin.ModelAdmin):
    fields = ('name', 'slug', 'address', 'country',
              'contact_name', 'contact_email', 'contact_phone',
              'contact_rut', 'rut', 'website', 'logo')

    def save_model(self, request, obj, form, change):
        obj.save()  # I need to save preemptive so I have an id later on.
        if not change:
            client_id = obj.contact_email + '.' + obj.slug
            client_id = sha224(client_id).hexdigest()
            c = ApiClientId(client_id=client_id, merchant=obj)
            c.save()


admin.site.register(Merchants, MerchantAdmin)
admin.site.register(MerchantTabs)
admin.site.register(UsersProxy, MerchantUserAdmin)
