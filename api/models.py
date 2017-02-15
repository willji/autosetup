# -*- coding: utf-8 -*-
from django.db import models
from django.conf import settings
from django.db.models.signals import post_save
from django.dispatch import receiver
from rest_framework.authtoken.models import Token


class Template(models.Model):
    name = models.CharField(max_length=40, unique=True)
    comment = models.CharField(max_length=200, null=True)
    created_date = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_date',]

    def __unicode__(self):
        return "{0}".format(self.name)

class Copy(models.Model):
    name = models.CharField(max_length=40, unique=True)
    vm_template = models.ForeignKey(Template)
    status = models.BooleanField(default=True)
    created_date = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_date',]

    def __unicode__(self):
        return "{0}".format(self.name)

class VmClone(models.Model):
    vcenter_server = models.CharField(max_length=40)
    vm_template = models.CharField(max_length=40)
    name = models.CharField(max_length=40)
    os = models.CharField(max_length=40)
    host_ips = models.CharField(max_length=40)
    ipaddresses = models.CharField(max_length=15)
    vlan_tags = models.CharField(max_length=40)
    comment = models.TextField(null=True)
    created_date = models.DateTimeField(auto_now_add=True)
    created_by = models.CharField(max_length=40, null=True)
    exit_code = models.IntegerField(null=True)
    cloned_vm_name = models.CharField(max_length=40, null=True)
    remark = models.CharField(max_length=40, null=True)

    class Meta:
        ordering = ['-created_date',]

    def __unicode__(self):
        return "{0}@{1}".format(self.vm_template, self.name)

class VmRelocate(models.Model):
    vcenter_server = models.CharField(max_length=40)
    name = models.CharField(max_length=40)
    host_ips = models.CharField(max_length=40)
    vlan_tags = models.CharField(max_length=40)
    comment = models.TextField(null=True)
    created_date = models.DateTimeField(auto_now_add=True)
    created_by = models.CharField(max_length=40, null=True)
    exit_code = models.IntegerField(null=True)

    class Meta:
        ordering = ['-created_date',]

    def __unicode__(self):
        return "{0}@{1}".format(self.name, self.host_ips)

class VmDelete(models.Model):
    vcenter_server = models.CharField(max_length=40)
    name = models.CharField(max_length=40)
    comment = models.TextField(null=True)
    created_date = models.DateTimeField(auto_now_add=True)
    created_by = models.CharField(max_length=40, null=True)
    exit_code = models.IntegerField(null=True)

    class Meta:
        ordering = ['-created_date',]

    def __unicode__(self):
        return "{0}".format(self.name)

class BatchClone(models.Model):
    vcenter_server = models.CharField(max_length=40)
    vm_template = models.CharField(max_length=40)
    host_ips = models.CharField(max_length=40)
    os = models.CharField(max_length=40)
    vlan_tags = models.CharField(max_length=40)
    vm_info = models.CharField(max_length=400)
    comment = models.TextField(null=True)
    created_date = models.DateTimeField(auto_now_add=True)
    created_by = models.CharField(max_length=40, null=True)
    exit_code = models.IntegerField(null=True)

    class Meta:
        ordering = ['-created_date',]

    def __unicode__(self):
        return "{0}@{1}".format(self.vm_template, self.vm_info)

class Clone(models.Model):
    data = models.CharField(max_length=10000)

class Relocate(models.Model):
    data = models.CharField(max_length=10000)

class Delete(models.Model):
    data = models.CharField(max_length=10000)

