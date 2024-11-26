from django.urls import path
from .views import addtodo, updatetodo, deletetodo, showtodos, showtodo

urlpatterns = [
    path('', showtodos, name='showtodos'),
    path('addtodo/', addtodo, name='addtodo'),
    path('updatetodo/<int:id>/', updatetodo, name='updatetodo'),
    path('deletetodo/<int:id>/', deletetodo, name='deletetodo'),
    path('<int:id>', showtodo, name='showtodo')
]
