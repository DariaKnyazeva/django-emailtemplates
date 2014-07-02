from django.conf.urls import patterns, url

from emailtemplates.views import EmailMessageTemplateListView,\
    EmailMessageTemplateCustomizeView, EmailMessageTemplateEditView,\
    EmailMessageTemplateDeleteView


urlpatterns = patterns('',
    url(r'^(?P<object_id>\d+)/account/$', EmailMessageTemplateListView.as_view(), name="email_message_templates"),
    url(r'^(?P<object_id>\d+)/(?P<template_id>\d+)/customize/$', EmailMessageTemplateCustomizeView.as_view(), 
        name="email_message_template_customize"),
    url(r'^(?P<object_id>\d+)/(?P<template_id>\d+)/edit/$', EmailMessageTemplateEditView.as_view(), 
        name="email_message_template_edit"),
    url(r'^(?P<object_id>\d+)/(?P<template_id>\d+)/revert/$', EmailMessageTemplateDeleteView.as_view(), 
        name="email_message_template_revert_to_default"),
)