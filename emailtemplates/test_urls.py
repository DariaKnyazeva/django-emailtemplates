from django.conf.urls import patterns, url
from django.contrib.sites.models import Site

from emailtemplates.views import EmailMessageTemplateListView,\
    EmailMessageTemplateCustomizeView, EmailMessageTemplateEditView,\
    EmailMessageTemplateDeleteView


urlpatterns = patterns('',
    url(r'^(?P<object_id>\d+)/email_templates/$', 
        EmailMessageTemplateListView.as_view(object_model=Site, 
                                             object_pk_url_kwarg='object_id'), 
                                             name="email_message_templates"),
    url(r'^(?P<object_id>\d+)/(?P<template_id>\d+)/customize/$', 
        EmailMessageTemplateCustomizeView.as_view(object_model=Site, 
                                                  object_pk_url_kwarg='object_id'), 
        name="email_message_template_customize"),
    url(r'^(?P<object_id>\d+)/(?P<template_id>\d+)/edit/$', 
        EmailMessageTemplateEditView.as_view(object_model=Site, 
                                             object_pk_url_kwarg='object_id'), 
        name="email_message_template_edit"),
    url(r'^(?P<object_id>\d+)/(?P<template_id>\d+)/revert/$', 
        EmailMessageTemplateDeleteView.as_view(object_model=Site, 
                                               object_pk_url_kwarg='object_id'), 
        name="email_message_template_revert_to_default"),
                       
    url(r'^(?P<object_id>\d+)/(?P<template_id>\d+)/edit/tpl-perm/$', 
        EmailMessageTemplateEditView.as_view(object_model=Site, 
                                             object_pk_url_kwarg='object_id',
                                             template_permissions=['can_edit_template',]), 
        name="email_message_template_edit_tpl_perm"),
                       
    url(r'^(?P<object_id>\d+)/(?P<template_id>\d+)/edit/obj-perm/$', 
        EmailMessageTemplateEditView.as_view(object_model=Site, 
                                             object_pk_url_kwarg='object_id',
                                             object_permissions=['can_edit_site',]), 
        name="email_message_template_edit_obj_perm"),
)