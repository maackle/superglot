from django.conf.urls import patterns, include, url

from django.views.generic import TemplateView
from mockup.views import HomeView, AnyJadeView

urlpatterns = patterns('',
	url(r'^$', HomeView.as_view(), name='home'),
	url(r'^(?P<template_name>.+)$', AnyJadeView.as_view(), name='home'),
)
