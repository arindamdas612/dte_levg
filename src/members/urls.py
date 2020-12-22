from django.urls import path
from .views import members, switch_role, activate_user, del_user, reset_password

urlpatterns = [
    path('', members, name='members'),
    path('switch-role/<int:id>/<int:role>',
         switch_role, name='switch_user_role'),
    path('activate-deactivate/<int:user_id>',
         activate_user, name='act_deact'),
    path('delete-member/<int:user_id>',
         del_user, name='delete_member'),
    path('member-reset/<int:user_id>',
         reset_password, name='member_reset'),

]
