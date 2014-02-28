from django.shortcuts import get_object_or_404, render_to_response
from giviu.models import Users
from api.models import ApiClientId


def daily_nl(request):
    users = Users.objects.filter(
        is_active=True,
        is_receiving=False,
        is_merchant=False
    )
    client_id = request.GET['client_id']
    get_object_or_404(ApiClientId,
                      client_id=client_id,
                      merchant__slug='giviu')

    return render_to_response('user_list.html',
                              {'users': users})
