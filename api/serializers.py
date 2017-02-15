# -*- coding: utf8 -*-
from rest_framework import serializers
from api import models

class VmCloneSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = models.VmClone

class VmRelocateSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = models.VmRelocate

class VmDeleteSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = models.VmDelete

class TemplateSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = models.Template

class CopySerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = models.Copy

class BatchCloneSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = models.BatchClone

class CloneSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = models.Clone

class RelocateSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = models.Relocate

class DeleteSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = models.Delete

