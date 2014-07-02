from django.contrib import messages
from django.contrib.contenttypes.models import ContentType
from django.http import Http404
from django.shortcuts import get_object_or_404
from django.views.generic.edit import DeleteView, UpdateView
from django.views.generic.list import ListView

from emailtemplates.forms import EmailTemplateForm
from emailtemplates.models import EmailMessageTemplate
from django.http.response import HttpResponseRedirect
from django.core.urlresolvers import reverse

# TODO: check object permissions
class EmailObjectMixin(object):
    object_model = None
    
    def dispatch(self, *args, **kwargs):
        if self.object_model is None:
            raise Http404()
        self.related_object = get_object_or_404(self.object_model,
                                                id=kwargs.get('object_id'))
        return super(EmailMessageTemplateListView, self).dispatch(*args, **kwargs)
    
    def get_context_data(self, **kwargs):
        context = super(EmailObjectMixin, self).get_context_data(**kwargs)
        context['object'] = self.related_object
        return context  


class EmailTemplateMixin(object):    
    def dispatch(self, *args, **kwargs):
        self.generic_template = get_object_or_404(EmailMessageTemplate, 
                                                  id=kwargs.get('template_id'))
        if not self.generic_template.can_override_per_object():
            raise Http404()
        return super(EmailTemplateMixin, self).dispatch(*args, **kwargs)
    
    def get_success_url(self):
        return reverse('email_message_templates', 
                       kwargs={'object_id': self.related_object.id})


class EmailMessageTemplateListView(EmailObjectMixin, ListView):
    """
    List of email message templates for the specified object
    """
    model = EmailMessageTemplate    
    
    def get_queryset(self, **kwargs):
        tpl = []
        names = EmailMessageTemplate.objects.values('name').distinct()
        for name in names:
            tpl.append(EmailMessageTemplate.objects.get_template(name['name'], 
                                                                 self.related_object))
        ids = [t.id for t in tpl]
        return EmailMessageTemplate.objects.filter(id__in=ids)


class EmailMessageTemplateCustomizeView(EmailTemplateMixin, EmailObjectMixin, UpdateView):
    """
    Creates a new template that is a copy of the generic template 
    but associated to the specified object
    """
    model = EmailMessageTemplate 
    object_model = None
    template_name = 'emailtemplates/emailtemplate_edit.html'
    form_class = EmailTemplateForm
    
    def get_object(self):
        email, _created = EmailMessageTemplate.objects.get_or_create(name=self.generic_template.name,
                                                                     description=self.generic_template.description,
                                                                     subject_template=self.generic_template.subject_template,
                                                                     body_template=self.generic_template.body_template,
                                                                     object_id=self.related_object.id,
                                                                     content_type=ContentType.objects.get_for_model(self.related_object))
        return email
    
    def form_valid(self, form):
        self.object = form.save(user=self.request.user)
        messages.add_message(self.request, messages.SUCCESS, 
                             'Event Template has been customized.')
        return super(EmailMessageTemplateCustomizeView, self).form_valid(form)   
    
    
class EmailMessageTemplateEditView(EmailTemplateMixin, EmailObjectMixin, UpdateView):
    """
    If there is an object-specific (customized) version of a generic template,
    it can be edited.
    """
    model = EmailMessageTemplate
    pk_url_kwarg = 'template_id' 
    template_name = 'emailtemplates/email_template_edit.html'
    form_class = EmailTemplateForm
    
    def form_valid(self, form):
        self.object = form.save(user=self.request.user)
        messages.add_message(self.request, messages.SUCCESS, 'Event Template has been updated.')
        return super(EmailMessageTemplateEditView, self).form_valid(form)
    
    
class EmailMessageTemplateDeleteView(EmailTemplateMixin, EmailObjectMixin, DeleteView):
    """
    Delete the object-specific template 
    so that users fall back to the generic one. 
    """
    model = EmailMessageTemplate 
    template_name = 'emailtemplates/email_template_revert_confirm.html'
    pk_url_kwarg = 'template_id'
    
    def post(self, request, *args, **kwargs):
        tpl = self.get_object()
        if tpl.object_id is not None:
            tpl.delete()
        messages.add_message(self.request, messages.SUCCESS, 'Email Template has been reverted to default.')
        return HttpResponseRedirect(self.get_success_url())
    
    def get_context_data(self, **kwargs):
        context = super(EmailMessageTemplateDeleteView, self).get_context_data(**kwargs)
        context['cancel_url'] = self.get_success_url()
        return context