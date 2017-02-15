# -*- coding: utf-8 -*-
from django.conf.urls import url, include
from rest_framework import routers
from api import views, signals
from rest_framework.authtoken import views as token_views

router = routers.DefaultRouter(trailing_slash=False)

router.register(r'vmclone', views.VmCloneViewSet, base_name='vmclone')
#router.register(r'vmrelocate', views.VmRelocateViewSet, base_name='vmrelocate')
router.register(r'vmdelete', views.VmDeleteViewSet, base_name='vmdelete')
router.register(r'batchclone', views.BatchCloneViewSet)
router.register(r'template', views.TemplateViewSet, base_name='template')
router.register(r'copy', views.CopyViewSet)
router.register(r'clone', views.CloneViewSet)
#router.register(r'relocate', views.RelocateViewSet)
#router.register(r'delete', views.DeleteViewSet)

urlpatterns = router.urls
urlpatterns.append(url(r'salt', views.salt))
urlpatterns.append(url(r'token/', token_views.obtain_auth_token))
urlpatterns.append(url(r'api-auth/', include('rest_framework.urls', namespace='rest_framework')))
