# -*- coding: utf-8 -*-
import json
from api import models
from api import serializers
from api import tasks
from rest_framework import viewsets
from rest_framework import permissions
from django.shortcuts import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated


class VmCloneViewSet(viewsets.ModelViewSet):
    queryset = models.VmClone.objects.all()
    serializer_class = serializers.VmCloneSerializer
    permission_classes = (permissions.DjangoModelPermissions,)

class VmRelocateViewSet(viewsets.ModelViewSet):
    queryset = models.VmRelocate.objects.all()
    serializer_class = serializers.VmRelocateSerializer
    permission_classes = (permissions.DjangoModelPermissions,)

class VmDeleteViewSet(viewsets.ModelViewSet):
    queryset = models.VmDelete.objects.all()
    serializer_class = serializers.VmDeleteSerializer
    permission_classes = (permissions.DjangoModelPermissions,)

class TemplateViewSet(viewsets.ModelViewSet):
    queryset = models.Template.objects.all()
    serializer_class = serializers.TemplateSerializer
    permission_classes = (permissions.DjangoModelPermissions,)

class CopyViewSet(viewsets.ModelViewSet):
    queryset = models.Copy.objects.all()
    serializer_class = serializers.CopySerializer
    permission_classes = (permissions.DjangoModelPermissions,)

class BatchCloneViewSet(viewsets.ModelViewSet):
    queryset = models.BatchClone.objects.all()
    serializer_class = serializers.BatchCloneSerializer
    permission_classes = (permissions.DjangoModelPermissions,)

class CloneViewSet(viewsets.ModelViewSet):
    queryset = models.Clone.objects.all()
    serializer_class = serializers.CloneSerializer
    permission_classes = (permissions.DjangoModelPermissions,)

class RelocateViewSet(viewsets.ModelViewSet):
    queryset = models.Relocate.objects.all()
    serializer_class = serializers.RelocateSerializer
    permission_classes = (permissions.DjangoModelPermissions,)

class DeleteViewSet(viewsets.ModelViewSet):
    queryset = models.Delete.objects.all()
    serializer_class = serializers.DeleteSerializer
    permission_classes = (permissions.DjangoModelPermissions,)


@api_view(['POST',])
@permission_classes([IsAuthenticated,])
@csrf_exempt
def salt(request):
    data = request.POST.get('data')
    data = json.loads(data)
    for i in data:
        vcenter_server = i.get('vcenter_server')
        name = i.get('name')
        os = i.get('os')
        ipaddresses = i.get('ipaddresses')[0]
        env = i.get('env')
        tasks.salt.delay(vcenter_server, name, os, ipaddresses, env)
    return HttpResponse('ok')

