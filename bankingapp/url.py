from django.urls import path
from .views import *
from django.conf import settings
from django.conf.urls.static import static


urlpatterns=[
    path('create/',create_account),
    path('showinfo/',show_info),
    path('withdrawmoney/',Withdraw_money),
    path('addmoney/',Add_money),
]

# if settings.DEBUG:
#     urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)