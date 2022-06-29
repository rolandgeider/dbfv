# -*- coding: utf-8 -*-

# This file is part of the DBFV site.
#
# the DBFV site is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# the DBFV site is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with the DBFV site.  If not, see <http://www.gnu.org/licenses/>.
# Django
from django.contrib.sites.shortcuts import get_current_site
from django.http import HttpRequest
from django.urls import reverse

# Third Party
from reportlab.graphics.barcode import qr
from reportlab.graphics.shapes import Drawing
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import cm
from reportlab.platypus import (
    Paragraph,
    SimpleDocTemplate,
    Spacer,
)


def build_submission_pdf(request: HttpRequest, pk: int, response):
    current_site = get_current_site(request)
    url = current_site.domain + reverse('submission-view', kwargs={'pk': pk})
    doc = SimpleDocTemplate(
        response, pagesize=A4, rightMargin=50, leftMargin=50, topMargin=50, bottomMargin=50
    )
    styles = getSampleStyleSheet()
    elements = [Paragraph("Titel kommt hier", styles["Heading2"]), Spacer(10 * cm, 0.5 * cm)]
    # story.append(Spacer(1, 2))  # some space between lines
    qr_code = qr.QrCodeWidget(url, barLevel='H')
    bounds = qr_code.getBounds()
    width = bounds[2] - bounds[0]
    height = bounds[3] - bounds[1]
    qr_image = Drawing(100, 100, transform=[100. / width, 0, 0, 100. / height, 0, 0])
    qr_image.add(qr_code)
    elements.append(qr_image)
    doc.build(elements)

    return doc
