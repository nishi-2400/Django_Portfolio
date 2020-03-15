from .models import Customer, Driver

def create_user_by_type(backend, user, request, response, *args, **kwargs):

    # プロフィール画像を取得
    # "https://platform-lookaside.fbsbx.com/platform/profilepic/?asid=" + response['id'] + "&height=100&width=100&ext=1583407488&hash=AeR2sqKETCLxbRBU"


    if request['user_type'] == 'customer' and not Customer.objects.filter(user_id=user.id):
        Customer.objects.create(user_id=user.id)
    elif not Driver.objects.filter(user_id=user.id):
        Driver.objects.create(user_id=user.id)
    
