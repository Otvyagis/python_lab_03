from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='home'),
    path('add/', views.add_task, name='add_task'),
    path('edit/<int:pk>/', views.edit_task, name='edit_task'),
    path('delete/<int:pk>/', views.delete_task, name='delete_task'),
    path('toggle/<int:pk>/', views.toggle_done, name='toggle_done'),
    path('plot/', views.plot_done_by_day, name='plot_done'),
]