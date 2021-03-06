# -*- coding: utf-8 *-*

# This file is part of Kumasta.
#
# Kumasta is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Kumasta is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License

from django.conf.urls import patterns, url
from django.core.urlresolvers import reverse_lazy
#from django.core.urlresolvers import reverse_lazy

from django.views.generic import TemplateView

from submission.views import (gym,
    state,
    bank_account,
    submissions,
    submission_gym,
    submission_judge,
    submissions_international,
    user,
    emails)


urlpatterns = patterns('submission.views',

    # The index page
    url(r'^$',
        TemplateView.as_view(template_name="index.html"),
        name="index"),

    # User actions
    url(r'^benutzer/registrieren$',
        user.registration,
        name='registration'),
    url(r'^abmelden/$',
        'user.logout',
        name="logout"),
    url(r'^abmelden/ok$',
        TemplateView.as_view(template_name="user/logout.html"),
        name="logout-page"),


    # Gyms
    url(r'^studio/(?P<pk>\d+)/details/$',
        gym.GymDetailView.as_view(),
        name='gym-view'),
    url(r'^studio/liste/alle/$',
        state.StateListView.as_view(template_name="gym/state_list.html"),
        name='gym-list'),
    url(r'^studio/liste/bundesland/(?P<state_pk>\d+)/$',
        gym.GymListView.as_view(),
        name='gym-list-state'),
    url(r'^studio/hinzufuegen/$',
        gym.GymCreateView.as_view(),
        name='gym-add'),
    url(r'^studio/(?P<pk>\d+)/bearbeiten/$',
        gym.GymUpdateView.as_view(),
        name="gym-edit"),
    url(r'^studio/(?P<pk>\d+)/loeschen/$',
        gym.GymDeleteView.as_view(),
        name="gym-delete"),


    # States
    url(r'^bundesland/liste/alle/$',
        state.StateListView.as_view(),
        name='state-list'),
    url(r'^bundesland/hinzufuegen/$',
        state.StateCreateView.as_view(),
        name='state-add'),
    url(r'^bundesland/(?P<pk>\d+)/bearbeiten/$',
        state.StateUpdateView.as_view(),
        name='state-edit'),
    url(r'^bundesland/(?P<pk>\d+)/loeschen/$',
        state.StateDeleteView.as_view(),
        name='state-delete'),


    # Bank account
    url(r'^bankkonto/liste/alle/$',
        bank_account.BankAccountListView.as_view(),
        name='bank-account-list'),
    url(r'^bankkonto/details/$',
        bank_account.BankAccountDetailView.as_view(),
        name='bank-account-view'),
    url(r'^bankkonto/hinzufuegen/$',
        bank_account.BankAccountCreateView.as_view(),
        name='bank-account-add'),
    url(r'^bankkonto/(?P<pk>\d+)/bearbeiten/$',
        bank_account.BankAccountUpdateView.as_view(),
        name='bank-account-edit'),


    # Emails
    url(r'^email/liste/alle/$',
        emails.EmailListView.as_view(),
        name='email-list'),
    #url(r'^email/(?P<pk>\d+)/details/$',
        #emails.EmailDetailView.as_view(),
        #name='email-view'),
    url(r'^email/hinzufuegen/$',
        emails.EmailCreateView.as_view(),
        name='email-add'),
    url(r'^email/(?P<pk>\d+)/bearbeiten/$',
        emails.EmailUpdateView.as_view(),
        name='email-edit'),
    url(r'^email/(?P<pk>\d+)/loeschen/$',
        emails.EmailDeleteView.as_view(),
        name='email-delete'),

    #
    # Submissions
    #

    # Starter
    url(r'^antrag/liste/alle/$',
        submissions.SubmissionListView.as_view(),
        name='submission-list'),
    url(r'^antrag/liste/(?P<year>\d+)/(?P<month>\d+)/$',
        submissions.SubmissionListMonthView.as_view(),
        name='submission-list-month'),
    url(r'^antrag/neu/(?P<type>(starter|kapmfrichter|studio))lizenz$',
        submissions.SubmissionCreateView.as_view(),
        name='submission-add'),
    url(r'^antrag/(?P<pk>\d+)/bearbeiten$',
        submissions.SubmissionUpdateView.as_view(),
        name='submission-edit'),
    url(r'^antrag/(?P<pk>\d+)/anzeigen$', # JS!
        submissions.SubmissionDetailView.as_view(),
        name='submission-view'),
    url(r'^antrag/(?P<pk>\d+)/loeschen$',
        submissions.SubmissionDeleteView.as_view(),
        name='submission-delete'),
    url(r'^antrag/(?P<pk>\d+)/bearbeiten/status$',
        submissions.SubmissionUpdateStatusView.as_view(),
        name='submission-edit-status'),
    url(r'^antrag/(?P<pk>\d+)/exportieren/serienbrief$',
        submissions.SubmissionCsvIndividualExportView.as_view(),
        name='submission-export-mailmerge'),
    url(r'^antrag/liste/exportieren/serienbrief$',
        submissions.SubmissionCsvExportView.as_view(),
        name='submission-export-mailmerge-new'),
    url(r'^antrag/suchen$',
        submissions.search,
        name='submission-search'),
                       
    # International
    url(r'^antrag-international/liste/alle/$',
        submissions_international.SubmissionListView.as_view(),
        name='submission-international-list'),
    url(r'^antrag-international/liste/(?P<year>\d+)/(?P<month>\d+)/$',
        submissions_international.SubmissionListMonthView.as_view(),
        name='submission-international-list-month'),
    url(r'^antrag-international/neu/lizenz$',
        submissions_international.SubmissionCreateView.as_view(),
        name='submission-international-add'),
    url(r'^antrag-international/(?P<pk>\d+)/bearbeiten$',
        submissions_international.SubmissionUpdateView.as_view(),
        name='submission-international-edit'),
    url(r'^antrag-international/(?P<pk>\d+)/anzeigen$', # JS!
        submissions_international.SubmissionDetailView.as_view(),
        name='submission-international-view'),
    url(r'^antrag-international/(?P<pk>\d+)/loeschen$',
        submissions_international.SubmissionDeleteView.as_view(),
        name='submission-international-delete'),
    url(r'^antrag-international/(?P<pk>\d+)/bearbeiten/status$',
        submissions_international.SubmissionUpdateStatusView.as_view(),
        name='submission-international-edit-status'),
    url(r'^antrag-international/(?P<pk>\d+)/exportieren/serienbrief$',
        submissions_international.SubmissionCsvIndividualExportView.as_view(),
        name='submission-international-export-mailmerge'),
    url(r'^antrag-international/liste/exportieren/serienbrief$',
        submissions_international.SubmissionCsvExportView.as_view(),
        name='submission-international-export-mailmerge-new'),
    url(r'^antrag-international/suchen$',
        submissions_international.search,
        name='submission-international-search'),

    # Gym
    url(r'^antrag-studio/liste/alle$',
        submission_gym.SubmissionListView.as_view(),
        name='submission-studio-list'),
    url(r'^antrag-studio/liste/(?P<year>\d+)/$',
        submission_gym.SubmissionListYearView.as_view(),
        name='submission-studio-list'),
    url(r'^antrag-studio/neu$',
        submission_gym.SubmissionCreateView.as_view(),
        name='submission-studio-add'),
    url(r'^antrag-studio/(?P<pk>\d+)/bearbeiten$',
        submission_gym.SubmissionUpdateView.as_view(),
        name='submission-studio-edit'),
    url(r'^antrag-studio/(?P<pk>\d+)/anzeigen$',
        submission_gym.SubmissionDetailView.as_view(),
        name='submission-studio-view'),
    url(r'^antrag-studio/(?P<pk>\d+)/loeschen$',
        submission_gym.SubmissionDeleteView.as_view(),
        name='submission-studio-delete'),
    url(r'^antrag-studio/(?P<pk>\d+)/bearbeiten/status$',
        submission_gym.SubmissionUpdateStatusView.as_view(),
        name='submission-studio-edit-status'),
    
    # Judge
    url(r'^antrag-kampfrichter/liste/alle$',
        submission_judge.SubmissionListView.as_view(),
        name='submission-judge-list'),
    url(r'^antrag-kampfrichter/neu$',
        submission_judge.SubmissionCreateView.as_view(),
        name='submission-judge-add'),
    url(r'^antrag-kampfrichter/(?P<pk>\d+)/bearbeiten$',
        submission_judge.SubmissionUpdateView.as_view(),
        name='submission-judge-edit'),
    url(r'^antrag-kampfrichter/(?P<pk>\d+)/anzeigen$',
        submission_judge.SubmissionDetailView.as_view(),
        name='submission-judge-view'),
    url(r'^antrag-kampfrichter/(?P<pk>\d+)/loeschen$',
        submission_judge.SubmissionDeleteView.as_view(),
        name='submission-judge-delete'),
    url(r'^antrag-kampfrichter/(?P<pk>\d+)/bearbeiten/status$',
        submission_judge.SubmissionUpdateStatusView.as_view(),
        name='submission-judge-edit-status'),
    url(r'^antrag-kampfrichter/(?P<pk>\d+)/exportieren/serienbrief$',
        submission_judge.SubmissionCsvIndividualExportView.as_view(),
        name='submission-judge-export-mailmerge'),
    url(r'^antrag-kampfrichter/liste/exportieren/serienbrief$',
        submission_judge.SubmissionCsvExportView.as_view(),
        name='submission-judge-export-mailmerge-new'),

    # Impressum
    url(r'^impressum$',
        TemplateView.as_view(template_name="misc/impressum.html"),
        name="impressum"),
    url(r'^rules$',
        TemplateView.as_view(template_name="misc/competition_rules.html"),
        name="competition_rules"),
)

# Password reset is implemented by Django, no need to cook our own soup here
# (besides the templates)
urlpatterns = urlpatterns + patterns('',
    url(r'^anmelden/$',
        'django.contrib.auth.views.login',
        {'template_name': 'user/login.html'},
        name='login'),

    url(r'^user/password/change$',
        'django.contrib.auth.views.password_change',
        {'template_name': 'user/change_password.html',
          'post_change_redirect': reverse_lazy('index')},
        name='change-password'),

    url(r'^user/password/reset/$',
        'django.contrib.auth.views.password_reset',
        {'template_name': 'user/password_reset_form.html'},
        name='password_reset'),

    url(r'^user/password/reset/done/$',
        'django.contrib.auth.views.password_reset_done',
        {'template_name': 'user/password_reset_done.html'},
        name='password_reset_done'),

    url(r'^user/password/reset/check/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})$',
        'django.contrib.auth.views.password_reset_confirm',
        {'template_name': 'user/password_reset_confirm.html'},
        name='password_reset_confirm'),

    url(r'^user/password/reset/complete/$',
        'django.contrib.auth.views.password_reset_complete',
        {'template_name': 'user/password_reset_complete.html'},
        name='password_reset_complete'),
    )

from django.conf import settings
urlpatterns = urlpatterns + patterns('',
    (r'^(?P<path>.*)$', 'django.views.static.serve', {'document_root': settings.MEDIA_ROOT}),
)
