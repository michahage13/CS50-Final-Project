from django.urls import path
from django.views.generic.base import TemplateView
from django.conf import settings
from django.conf.urls import url
from django.conf.urls.static import static

from . import views
from .views import macrosListView


urlpatterns = [
    path("", views.index, name="index"),
    #path("welcome", views.index_first, name="welcome"),
    path("macros_list", macrosListView.as_view(), name="macros-view"),
    path("signup/", views.SignUp.as_view(), name='signup'),
    #path("dashboard", views.user_dashboard, name="user_dashboard"),
    path("<int:day_id>", views.macro),
    path("macroslist", views.macroslist),
    path("delete/<int:id>", views.delete_record, name='delete_confirm'),
    path("meal_display/<int:id>", views.meal_display, name='meal_display'),
    path("rotateright/<int:id>", views.image_rotate_right, name='rotate_right'),
    path("rotateleft/<int:id>", views.image_rotate_left, name='rotate_left'),
    path("search_entry", views.search_entry),
    path("account", views.account, name="account_page"),
    path("change_pw", views.change_pw, name="change_pw"),
    path("delete", views.del_user, name="delete-user"),
    path("delete_confirm", views.del_user_confirm, name="delete_confirm"),
    path("about", views.about_page, name="about_page")
]

if settings.DEBUG: # new
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
