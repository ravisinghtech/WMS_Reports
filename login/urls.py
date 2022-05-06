from django.urls import path
from . import views
urlpatterns = \
    [
        path('', views.home, name='home'),
        path('login', views.login, name='login'),
        path('reportsHome', views.reportsHome, name='reportsHome'),
        path('logout', views.logout, name='logout'),
        path('inventory', views.inventory, name='inventory'),
        path('InventoryReports', views.InventoryReports, name='InventoryReports'),
        path('downloadReport', views.downloadReport, name='downloadReport'),
        path('GetSummary', views.GetSummary, name='GetSummary')
    ]