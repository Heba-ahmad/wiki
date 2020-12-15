from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("create_new", views.create, name="create_new"),
    path("wiki/<str:title>", views.entry, name="entry"),
    path("random", views.randompage, name="randompage"),
    path("search", views.search, name="searchpage"),
    path("wiki/<str:title>/edit", views.editEntryForm, name="editEntryForm"),
    path("wiki/<str:title>/submit", views.editPage, name="editPage")

]
