# -*- coding: utf-8 -*-
from django.db.models.signals import post_save
from django.dispatch import receiver
from api import models, tasks

@receiver(post_save, sender=models.VmClone)
def add_vmclone_job(sender, **kwargs):
    instance = kwargs['instance']
    return tasks.vm_clone.delay(instance)

@receiver(post_save, sender=models.VmRelocate)
def add_vmrelocate_job(sender, **kwargs):
    instance = kwargs['instance']
    tasks.vm_relocate.delay(instance)

@receiver(post_save, sender=models.VmDelete)
def add_vmdelete_job(sender, **kwargs):
    instance = kwargs['instance']
    tasks.vm_delete.delay(instance)

@receiver(post_save, sender=models.BatchClone)
def add_batchclone_job(sender, **kwargs):
    instance = kwargs['instance']
    tasks.batch_clone.delay(instance)

@receiver(post_save, sender=models.Clone)
def add_clone_job(sender, **kwargs):
    instance = kwargs['instance']
    tasks.clone.delay(instance)

@receiver(post_save, sender=models.Relocate)
def add_relocate_job(sender, **kwargs):
    instance = kwargs['instance']
    tasks.relocate.delay(instance)

@receiver(post_save, sender=models.Delete)
def add_delete_job(sender, **kwargs):
    instance = kwargs['instance']
    tasks.delete.delay(instance)

