from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('', views.index, name='index'),
    path('login', views.login_view, name='login'),
    path('logout', views.logout_view, name='logout'),
    path('register', views.register, name='register'),

    path('addNote', views.addNoteView, name='addNote'),
    path('delete/', views.delete_images, name='deleteImages'),
    # path('get_image_url/<int:image_id>/', views.get_image_url, name='get_image_url'),
    path('get-temporary-image-url/<int:image_id>/', views.get_temporary_image_url, name='get_temporary_image_url'),
    path('get-image/<str:signed_value>/', views.get_image, name='get_image'),
]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)