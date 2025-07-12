from django.urls import path
from . import views

urlpatterns=[
    path('',views.index,name='index'),
    path('home/',views.home,name='index'),
    # people
    path('people/', views.people, name='people'),
    path('people/<str:username>/', views.person, name='person-page'),
    
    path('research/', views.research, name='research'),
    path('research/<int:id>/', views.research_view, name='research'),
    path('news/', views.news, name='news'),
    path('news/<int:id>/', views.news_read, name='news'),
    path('publications/', views.publications, name='publications'),
    path('teaching/', views.teaching, name='teaching'),
    path('highlights/', views.highlights, name='highlights'),
    path('database/', views.database, name='database'),
    path('join/', views.join, name='join'),
    
]
from django.conf import settings
from django.conf.urls.static import static

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)