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

from django.views.generic import TemplateView
from django.conf.urls import patterns, url, include
from django.contrib.auth.decorators import permission_required

from core.forms import EmailListForm
from core.views import email_lists


# sub patterns for email lists
patterns_email = patterns('',
    url(r'^auswaehlen/$',
        permission_required('core.change_emailcron')(TemplateView.as_view(template_name="email/overview.html")),
        name='overview'),
    url(r'^erstellen/(?P<type>(starter|studio))$',
        permission_required('core.change_emailcron')(email_lists.EmailListFormPreview(EmailListForm)),
        name='add'),
)


urlpatterns = patterns('',
    url(r'^email-listen/', include(patterns_email, namespace="email")),
)
