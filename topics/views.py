# -*- coding: utf-8 -*-
import json
from django.http import HttpResponse, HttpResponseRedirect
from django.utils.translation import ugettext as _
from django.core.urlresolvers import reverse
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import View, DetailView
from django.views.generic.edit import UpdateView
from django.views.decorators.http import require_http_methods
from django.contrib.auth.decorators import login_required
from places_core.mixins import LoginRequiredMixin
from .models import Discussion, Entry
from .forms import DiscussionForm, ReplyForm


class DiscussionDetailView(DetailView):
    """
    Single discussion page as forum page.
    """
    model = Discussion

    def get_context_data(self, **kwargs):
        topic = super(DiscussionDetailView, self).get_object()
        context = super(DiscussionDetailView, self).get_context_data(**kwargs)
        replies = Entry.objects.filter(discussion=topic)
        paginator = Paginator(replies, 25)
        page = self.request.GET.get('page')
        try:
            context['replies'] = paginator.page(page)
        except PageNotAnInteger:
            context['replies'] = paginator.page(1)
        except EmptyPage:
            context['replies'] = paginator.page(paginator.num_pages)
        context['form'] = ReplyForm(initial={
            'discussion': topic.slug
        })
        context['title'] = topic.question
        context['location'] = topic.location
        return context


class DiscussionUpdateView(LoginRequiredMixin, UpdateView):
    """
    Allow owner user to update and change their discussions.
    """
    model = Discussion
    form_class = DiscussionForm

    def get_context_data(self, **kwargs):
        obj = super(DiscussionUpdateView, self).get_object()
        context = super(DiscussionUpdateView, self).get_context_data(**kwargs)
        context['title'] = obj.question
        context['subtitle'] = _('Edit this topic')
        context['location'] = obj.location
        return context


class EntryUpdateView(LoginRequiredMixin, UpdateView):
    """
    Update entry in static form.
    """
    model = Entry
    form_class = ReplyForm
    template_name = 'topics/reply_update.html'

    def get_context_data(self, **kwargs):
        obj = super(EntryUpdateView, self).get_object()
        context = super(EntryUpdateView, self).get_context_data(**kwargs)
        self.success_url = reverse('discussion:details',
                    kwargs={'slug': obj.discussion.slug})
        context['title'] = _('Edit entry')
        return context

    def form_valid(self, form):
        obj = form.instance
        obj.save()
        return redirect(reverse('discussion:details',
                kwargs={'slug': obj.discussion.slug}))


class TopicAjaxView(LoginRequiredMixin, View):
    """
    Use this view as REST out for discussion models.
    For now it works only for DELETE requests made
    in global 'place forum topic list'.
    FIXME: "This is forbidden when an 'atomic' block is active" error.
    """
    http_method_names = [u'delete']

    def delete(self, request, slug=None):
        if slug == None:
            return HttpResponse(json.dumps({
                'success': False,
                'message': _("No entry ID provided"),
                'level': 'danger',
            }))

        try:
            topic = Discussion.objects.get(slug=slug)
        except Discussion.DoesNotExist as ex:
            return HttpResponse(json.dumps({
                'success': False,
                'message': str(ex),
                'level': 'danger',
            }))

        if request.user != topic.creator and not request.user.is_superadmin():
            return HttpResponse(json.dumps({
                'success': False,
                'message': _("Permission required!"),
                'level': 'danger',
            }))

        try:
            topic.delete()
            return HttpResponse(json.dumps({
                'success': True,
                'message': _("Entry deleted"),
                'level': 'success',
            }))
        except Exception as ex:
            return HttpResponse(json.dumps({
                'success': False,
                'message': str(ex),
                'level': 'danger',
            }))


def reply(request, slug):
    """
    Create forum reply.
    """
    if request.method == 'POST' and request.POST:
        post = request.POST
        topic = Discussion.objects.get(slug=post['discussion'])
        if not topic.status:
            return HttpResponse(_('This discussion is closed.'))
        entry = Entry(
            content = post['content'],
            creator = request.user,
            discussion = topic,
        )
        try:
            entry.save()
        except:
            return HttpResponse(_('An error occured'))
    return HttpResponseRedirect(reverse('discussion:details',
                                kwargs={'slug': topic.slug,}))
