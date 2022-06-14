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

# Django
import django
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth.views import (
    LoginView,
    PasswordChangeView,
    PasswordResetCompleteView,
    PasswordResetConfirmView,
    PasswordResetDoneView,
    PasswordResetView,
)
from django.urls import (
    path,
    re_path,
    reverse_lazy,
)
from django.views.generic import TemplateView

# dbfv
from submission.views import (
    bank_account,
    emails,
    gym,
    state,
    submission_gym,
    submission_judge,
    submissions,
    submissions_international,
    user,
)


urlpatterns = [

    # The index page
    path('', TemplateView.as_view(template_name="index.html"), name="index"),

    # User actions
    path('benutzer/registrieren', user.registration, name='registration'),
    path('abmelden', user.logout, name="logout"),
    path('abmelden/ok', TemplateView.as_view(template_name="user/logout.html"), name="logout-page"),

    # Gyms
    path('studio/<int:pk>/details/', gym.GymDetailView.as_view(), name='gym-view'),
    path(
        'studio/liste/alle/',
        state.StateListView.as_view(template_name="gym/state_list.html"),
        name='gym-list'
    ),
    path(
        'studio/liste/bundesland/<int:state_pk>/', gym.GymListView.as_view(), name='gym-list-state'
    ),
    path('studio/hinzufuegen/', gym.GymCreateView.as_view(), name='gym-add'),
    path('studio/<int:pk>/bearbeiten/', gym.GymUpdateView.as_view(), name="gym-edit"),
    path('studio/<int:pk>/loeschen/', gym.GymDeleteView.as_view(), name="gym-delete"),

    # States
    path('bundesland/liste/alle/', state.StateListView.as_view(), name='state-list'),
    path('bundesland/hinzufuegen/', state.StateCreateView.as_view(), name='state-add'),
    path('bundesland/<int:pk>/bearbeiten/', state.StateUpdateView.as_view(), name='state-edit'),
    path('bundesland/<int:pk>/loeschen/', state.StateDeleteView.as_view(), name='state-delete'),

    # Bank account
    path(
        'bankkonto/liste/alle/',
        bank_account.BankAccountListView.as_view(),
        name='bank-account-list'
    ),
    path(
        'bankkonto/details/',
        bank_account.BankAccountDetailView.as_view(),
        name='bank-account-view'
    ),
    path(
        'bankkonto/hinzufuegen/',
        bank_account.BankAccountCreateView.as_view(),
        name='bank-account-add'
    ),
    path(
        'bankkonto/<int:pk>/bearbeiten/',
        bank_account.BankAccountUpdateView.as_view(),
        name='bank-account-edit'
    ),

    # Emails
    path('email/liste/alle/', emails.EmailListView.as_view(), name='email-list'),
    # path(r'^email/(?P<pk>\d+)/details/$',
    # emails.EmailDetailView.as_view(),
    # name='email-view'),
    path('email/hinzufuegen/', emails.EmailCreateView.as_view(), name='email-add'),
    path('email/<int:pk>/bearbeiten/', emails.EmailUpdateView.as_view(), name='email-edit'),
    path('email/<int:pk>/loeschen/', emails.EmailDeleteView.as_view(), name='email-delete'),

    #
    # Submissions
    #

    # Starter
    path('antrag/<int:pk>/pdf', submissions.pdf, name='submission-pdf'),
    path('antrag/liste/alle/', submissions.SubmissionListView.as_view(), name='submission-list'),
    path(
        'antrag/liste/<int:year>/<int:month>/',
        submissions.SubmissionListMonthView.as_view(),
        name='submission-list-month'
    ),
    re_path(
        r'^antrag/neu/(?P<type>(starter|kapmfrichter|studio))lizenz$',
        submissions.SubmissionCreateView.as_view(),
        name='submission-add'
    ),
    path(
        'antrag/<int:pk>/bearbeiten',
        submissions.SubmissionUpdateView.as_view(),
        name='submission-edit'
    ),
    path(
        'antrag/<int:pk>/anzeigen',  # JS!
        submissions.SubmissionDetailView.as_view(),
        name='submission-view'
    ),
    path(
        'antrag/<int:pk>/loeschen',
        submissions.SubmissionDeleteView.as_view(),
        name='submission-delete'
    ),
    path(
        r'antrag/<int:pk>/bearbeiten/status',
        submissions.SubmissionUpdateStatusView.as_view(),
        name='submission-edit-status'
    ),
    path(
        'antrag/<int:pk>/exportieren/serienbrief',
        submissions.SubmissionCsvIndividualExportView.as_view(),
        name='submission-export-mailmerge'
    ),
    path(
        'antrag/liste/exportieren/serienbrief',
        submissions.SubmissionCsvExportView.as_view(),
        name='submission-export-mailmerge-new'
    ),
    path('antrag/suchen', submissions.search, name='submission-search'),

    # International
    path(
        'antrag-international/liste/alle/',
        submissions_international.SubmissionListView.as_view(),
        name='submission-international-list'
    ),
    re_path(
        r'^antrag-international/liste/(?P<year>\d+)/(?P<month>\d+)/$',
        submissions_international.SubmissionListMonthView.as_view(),
        name='submission-international-list-month'
    ),
    path(
        'antrag-international/neu/lizenz',
        submissions_international.SubmissionCreateView.as_view(),
        name='submission-international-add'
    ),
    path(
        'antrag-international/<int:pk>/bearbeiten',
        submissions_international.SubmissionUpdateView.as_view(),
        name='submission-international-edit'
    ),
    path(
        'antrag-international/<int:pk>/anzeigen',  # JS!
        submissions_international.SubmissionDetailView.as_view(),
        name='submission-international-view'
    ),
    path(
        'antrag-international/<int:pk>/loeschen',
        submissions_international.SubmissionDeleteView.as_view(),
        name='submission-international-delete'
    ),
    path(
        'antrag-international/<int:pk>/bearbeiten/status',
        submissions_international.SubmissionUpdateStatusView.as_view(),
        name='submission-international-edit-status'
    ),
    path(
        'antrag-international/<int:pk>/exportieren/serienbrief',
        submissions_international.SubmissionCsvIndividualExportView.as_view(),
        name='submission-international-export-mailmerge'
    ),
    path(
        'antrag-international/liste/exportieren/serienbrief',
        submissions_international.SubmissionCsvExportView.as_view(),
        name='submission-international-export-mailmerge-new'
    ),
    path(
        'antrag-international/suchen',
        submissions_international.search,
        name='submission-international-search'
    ),

    # Gym
    path(
        'antrag-studio/liste/alle',
        submission_gym.SubmissionListView.as_view(),
        name='submission-studio-list'
    ),
    path(
        'antrag-studio/liste/<int:year>/',
        submission_gym.SubmissionListYearView.as_view(),
        name='submission-studio-list'
    ),
    path(
        'antrag-studio/neu',
        submission_gym.SubmissionCreateView.as_view(),
        name='submission-studio-add'
    ),
    path(
        'antrag-studio/<int:pk>/bearbeiten',
        submission_gym.SubmissionUpdateView.as_view(),
        name='submission-studio-edit'
    ),
    path(
        'antrag-studio/<int:pk>/anzeigen',
        submission_gym.SubmissionDetailView.as_view(),
        name='submission-studio-view'
    ),
    path(
        'antrag-studio/<int:pk>/loeschen',
        submission_gym.SubmissionDeleteView.as_view(),
        name='submission-studio-delete'
    ),
    path(
        'antrag-studio/<int:pk>/bearbeiten/status',
        submission_gym.SubmissionUpdateStatusView.as_view(),
        name='submission-studio-edit-status'
    ),

    # Judge
    path(
        'antrag-kampfrichter/liste/alle',
        submission_judge.SubmissionListView.as_view(),
        name='submission-judge-list'
    ),
    path(
        'antrag-kampfrichter/neu',
        submission_judge.SubmissionCreateView.as_view(),
        name='submission-judge-add'
    ),
    path(
        'antrag-kampfrichter/<int:pk>/bearbeiten',
        submission_judge.SubmissionUpdateView.as_view(),
        name='submission-judge-edit'
    ),
    path(
        'antrag-kampfrichter/<int:pk>/anzeigen',
        submission_judge.SubmissionDetailView.as_view(),
        name='submission-judge-view'
    ),
    path(
        'antrag-kampfrichter/<int:pk>/loeschen',
        submission_judge.SubmissionDeleteView.as_view(),
        name='submission-judge-delete'
    ),
    path(
        'antrag-kampfrichter/<int:pk>/bearbeiten/status',
        submission_judge.SubmissionUpdateStatusView.as_view(),
        name='submission-judge-edit-status'
    ),
    path(
        'antrag-kampfrichter/<int:pk>/exportieren/serienbrief',
        submission_judge.SubmissionCsvIndividualExportView.as_view(),
        name='submission-judge-export-mailmerge'
    ),
    path(
        'antrag-kampfrichter/liste/exportieren/serienbrief',
        submission_judge.SubmissionCsvExportView.as_view(),
        name='submission-judge-export-mailmerge-new'
    ),

    # Impressum
    path('impressum', TemplateView.as_view(template_name="misc/impressum.html"), name="impressum"),
    path(
        'rules',
        TemplateView.as_view(template_name="misc/competition_rules.html"),
        name="competition_rules"
    ),
]

# Password reset is implemented by Django, no need to cook our own soup here
# (besides the templates)
urlpatterns += [
    path('anmelden/', LoginView.as_view(template_name='user/login.html'), name='login'),
    path(
        'user/password/change',
        PasswordChangeView.as_view(
            template_name='user/change_password.html', success_url=reverse_lazy('index')
        ),
        name='change-password'
    ),
    path(
        'user/password/reset/',
        PasswordResetView.as_view(template_name='user/password_reset_form.html'),
        name='password_reset'
    ),
    path(
        'user/password/reset/done/',
        PasswordResetDoneView.as_view(template_name='user/password_reset_done.html'),
        name='password_reset_done'
    ),
    re_path(
        r'^user/password/reset/check/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})$',
        PasswordResetConfirmView.as_view(template_name='user/password_reset_confirm.html'),
        name='password_reset_confirm'
    ),
    path(
        'user/password/reset/complete/',
        PasswordResetCompleteView.as_view(template_name='user/password_reset_complete.html'),
        name='password_reset_complete'
    ),
]
