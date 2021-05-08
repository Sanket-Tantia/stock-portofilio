from django.urls import path, re_path
from dashboard import views

urlpatterns = [

    # The home page
    path('home', views.home, name='home'),
    path('stock', views.add_stock, name='add-stock'),
    path('record', views.record_trade, name='record-trade'),

    # Matches any html file
    # re_path(r'^.*\.*', views.pages, name='pages'),

]
