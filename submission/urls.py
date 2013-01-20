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
#from django.core.urlresolvers import reverse_lazy

from django.views.generic import TemplateView


urlpatterns = patterns('',

    # The index page
    url(r'^$',
        TemplateView.as_view(template_name="index.html"),
        name="index"),

)
