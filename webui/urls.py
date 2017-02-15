# -*- coding: utf-8 -*-

"""
Definition of urls for webui.
"""

from django.conf.urls import patterns, url, include
from webui import views

urlpatterns = [
    url(r'^$', views.VmCloneItemView.as_view(), name='vmclone'),
    url(r'^relocate/$', views.VmRelocateItemView.as_view(), name='vmrelocate'),
    url(r'^delete/$', views.VmDeleteItemView.as_view(), name='vmdelete'),
    url(r'^about/$', views.AboutView.as_view(), name='about'),
]
