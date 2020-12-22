from django.urls import path
from .views import home, fy_data, del_fy_data, FilterOptionsApiView, process_filter, ChangePassword, ChartDataApiView

urlpatterns = [
    path('', home, name='home'),
    path('fy-data', fy_data, name='fy_data'),
    path('password-reset/', ChangePassword.as_view(), name='password_reset'),
    path('del-fy-data/<int:sumry_id>', del_fy_data, name='del_fy_data'),
    path('show-filter/<str:filename>', process_filter, name='show_filter'),
    path('api/filter-options', FilterOptionsApiView.as_view(),
         name='api-filter-options'),
    path('api/chart-data', ChartDataApiView.as_view(),
         name='api-chart-data'),
]
