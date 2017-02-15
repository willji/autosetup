# -*- coding: utf-8 -*-

from vanilla import ListView
from django.views.generic import TemplateView
from api import models
from webui import forms
from datetime import datetime


class AboutView(TemplateView):

    template_name = u'webui/about.html'

    def get_context_data(self, **kwargs):

        context = super(AboutView, self).get_context_data(**kwargs)

        context['title'] = u'关于'
        # page footer
        context['year'] = datetime.now().year
        
        return context

class VmCloneItemView(ListView):
    model = models.VmClone
    form_class = forms.SearchForm
    queryset = None
    lookup_field = 'name'
    paginate_by = 15

    def get_context_data(self, **kwargs):
        context = super(VmCloneItemView, self).get_context_data(**kwargs)

        # add search form
        context['form'] = self.get_form()
        context['title'] = u'虚拟机克隆'
        context['introduction'] = u'包含了克隆完成，正在克隆，以及已加入克隆队列的克隆任务。'

        # login partial and commons
        context['year'] = datetime.now().year

        return context

    def get_queryset(self):
        # support search
        try:
            keyword = self.request.GET['keyword']
        except:
            keyword = ''

        if keyword == '':
            return models.VmClone.objects.all()
        else:
            return models.VmClone.objects.filter(name=keyword)

class VmRelocateItemView(ListView):
    model = models.VmRelocate
    form_class = forms.SearchForm
    queryset = None
    lookup_field = 'name'
    paginate_by = 15

    def get_context_data(self, **kwargs):
        context = super(VmRelocateItemView, self).get_context_data(**kwargs)

        # add search form
        context['form'] = self.get_form()
        context['title'] = u'虚拟机迁移'
        context['introduction'] = u'包含了迁移完成，正在迁移，以及已加入迁移队列的克隆任务。'

        # login partial and commons
        context['year'] = datetime.now().year

        return context

    def get_queryset(self):
        # support search
        try:
            keyword = self.request.GET['keyword']
        except:
            keyword = ''

        if keyword == '':
            return models.VmRelocate.objects.all()
        else:
            return models.VmRelocate.objects.filter(name=keyword)

class VmDeleteItemView(ListView):
    model = models.VmDelete
    form_class = forms.SearchForm
    queryset = None
    lookup_field = 'name'
    paginate_by = 15

    def get_context_data(self, **kwargs):
        context = super(VmDeleteItemView, self).get_context_data(**kwargs)

        # add search form
        context['form'] = self.get_form()
        context['title'] = u'虚拟机删除'
        context['introduction'] = u'包含了删除完成，正在删除，以及已加入删除队列的克隆任务。'

        # login partial and commons
        context['year'] = datetime.now().year

        return context

    def get_queryset(self):
        # support search
        try:
            keyword = self.request.GET['keyword']
        except:
            keyword = ''

        if keyword == '':
            return models.VmDelete.objects.all()
        else:
            return models.VmDelete.objects.filter(name=keyword)

