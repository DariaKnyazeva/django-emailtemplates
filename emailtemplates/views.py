from django.contrib import messages
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import PermissionDenied, ImproperlyConfigured
from django.core.urlresolvers import reverse
from django.http import Http404
from django.http.response import HttpResponseRedirect
from django.views.generic.detail import SingleObjectMixin
from django.views.generic.edit import DeleteView, UpdateView
from django.views.generic.list import ListView

from emailtemplates.forms import EmailTemplateForm
from emailtemplates.models import EmailMessageTemplate


class EmailObjectMixin(SingleObjectMixin):
    object_model = None    
    object_permissions = []
    
    def dispatch(self, *args, **kwargs):
        self.related_object = self.get_object()
        for perm in self.object_permissions:
            if not self.request.user.has_perm(perm, self.related_object):
                    raise PermissionDenied
        return super(EmailObjectMixin, self).dispatch(*args, **kwargs)
    
    def get_queryset(self):
        """
        Get the queryset to look an object up against. May not be called if
        `get_object` is overridden.
        """
        if self.queryset is None:
            if self.object_model:
                return self.object_model._default_manager.all()
            else:
                raise ImproperlyConfigured("%(cls)s is missing a object_model." % {
                                                'cls': self.__class__.__name__
                                            })
        return self.queryset._clone()
    
    def get_context_data(self, **kwargs):
        context = super(EmailObjectMixin, self).get_context_data(**kwargs)
        context['related_object'] = self.related_object
        return context  


class EmailTemplateMixin(EmailObjectMixin):   
    # list of template-related permissions, 
    # e.g. can_view_template, can_edit_template
    template_permissions = []    
     
    def dispatch(self, *args, **kwargs):
        self.generic_template = self.get_object()
        if not self.generic_template.can_override_per_object:
            raise Http404()
        for perm in self.template_permissions:
            if not self.request.user.has_perm(perm, self.generic_template):
                    raise PermissionDenied
        return super(EmailTemplateMixin, self).dispatch(*args, **kwargs)
    
    def get_success_url(self):
        if self.pk_url_kwarg is not None:            
            return reverse('email_message_templates', 
                            kwargs={'%s' % self.pk_url_kwarg: self.related_object.id})
        else:
            return reverse('email_message_templates', 
                            kwargs={'%s' % self.slug_url_kwarg: getattr(self.related_object, self.slug_field)}) 


class EmailMessageTemplateListView(EmailObjectMixin, ListView):
    """
    List of email message templates for the specified object
    """
    model = EmailMessageTemplate
    template_name = 'emailtemplates/list.html'    
    
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
    template_name = 'emailtemplates/edit.html'
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
    template_name = 'emailtemplates/edit.html'
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
    template_name = 'emailtemplates/revert_confirm.html'
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
