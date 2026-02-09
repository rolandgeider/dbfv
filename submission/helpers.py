# -*- coding: utf-8 -*-

# This file is part of the DBFV submission site
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with the DBFV site.  If not, see <http://www.gnu.org/licenses/>.
# Django
from django.contrib.sites.shortcuts import get_current_site
from django.http import HttpRequest, HttpResponse
from django.urls import reverse

# Third Party
from reportlab.graphics.barcode import qr
from reportlab.graphics.shapes import Drawing
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import cm
from reportlab.pdfgen import canvas
from reportlab.platypus import (
    Paragraph,
    SimpleDocTemplate,
    Spacer,
)


def build_starter_pdf(request: HttpRequest, submission, response: HttpResponse) -> None:

    # Document
    current_site = get_current_site(request)
    url = current_site.domain + reverse('submission-view', kwargs={'pk': submission.id})

    doc = SimpleDocTemplate(
        response,
        pagesize=A4,
        rightMargin=70,
        leftMargin=70,
        topMargin=70,
        bottomMargin=50,
    )
    styles = getSampleStyleSheet()

    # QR Code
    elements = []

    qr_code = qr.QrCodeWidget(url, barLevel='H', x=185, y=240)
    bounds = qr_code.getBounds()
    width = bounds[2] - bounds[0]
    height = bounds[3] - bounds[1]
    qr_image = Drawing(150, 150, transform=[150. / width, 0, 0, 150. / height, 0, 0])
    qr_image.add(qr_code)

    elements.append(Spacer(1 * cm, 1 * cm))
    elements.append(Paragraph(f"{submission.first_name} {submission.last_name}"))
    elements.append(Paragraph(f"{submission.street}  {submission.house_nr}"))
    elements.append(Paragraph(f"{submission.zip_code } {submission.city}"))
    elements.append(Spacer(1 * cm, 4 * cm))

    elements.append(Paragraph(f"Starterlizenz {submission.creation_date.year} ({submission.gym.state.name}) - {submission.pk}", styles["Heading2"]))
    elements.append(Paragraph(f"Sehr geehrte/r Frau/Herr {submission.first_name} {submission.last_name},"))
    elements.append(Spacer(1 * cm, 0.4 * cm))

    elements.append(Paragraph(f"""<para align="justify">Die Starterlizenz {submission.creation_date.year} ist
        für das ganze Kalenderjahr gültig und berechtigt zur Teilnahme an allen vom DBFV
        e.V. und seinen Landesverbänden ausgetragenenn Wettkämpfen.</para>"""))
    elements.append(Spacer(1 * cm, 0.4 * cm))

    elements.append(Paragraph("""
        <para align="justify">Die Landesmeisterschaften dienen in allen Klassen und Kategorien wie bisher als
        Qualifikation zur Deutschen- und im Herbst zur Internationalen Deutschen Meisterschaft. 
        Sie sind als Athletin/Athlet regional und national an die Wettkampfregeln des Deutschen
        Bodybuilding- und Fitnessverbandes DBFV e.V. (siehe dbfv.de/wettkampfregeln) und
        international an die Regeln des Europäischen Verbandes EBFF und des
        Weltverbandes IFBB gebunden.</para>"""))
    elements.append(Spacer(1 * cm, 0.4 * cm))

    elements.append(Paragraph("""Wir wünschen eine erfolgreiche Wettkampfsaison"""))
    elements.append(Spacer(1 * cm, 1 * cm))
    elements.append(Paragraph("""DBFV e.V."""))
    elements.append(Paragraph("""Geschäftstselle"""))
    elements.append(qr_image)
    doc.build(elements)

    return doc


def build_judge_pdf(request: HttpRequest, submission, response: HttpResponse) -> None:

    # Document
    current_site = get_current_site(request)
    url = current_site.domain + reverse('submission-judge-view', kwargs={'pk': submission.id})
    doc = SimpleDocTemplate(
        response,
        pagesize=A4,
        rightMargin=70,
        leftMargin=70,
        topMargin=70,
        bottomMargin=50,
    )
    styles = getSampleStyleSheet()

    # QR Code
    elements = []

    qr_code = qr.QrCodeWidget(url, barLevel='H', x=185, y=240)
    bounds = qr_code.getBounds()
    width = bounds[2] - bounds[0]
    height = bounds[3] - bounds[1]
    qr_image = Drawing(150, 150, transform=[150. / width, 0, 0, 150. / height, 0, 0])
    qr_image.add(qr_code)

    elements.append(Spacer(1 * cm, 1 * cm))
    elements.append(Paragraph(f"{submission.first_name} {submission.last_name}"))
    elements.append(Paragraph(submission.street))
    elements.append(Paragraph(f"{submission.zip_code } {submission.city}"))
    elements.append(Spacer(1 * cm, 4 * cm))

    elements.append(Paragraph(f"Kampfrichterlizenz {submission.creation_date.year} - {submission.pk}", styles["Heading2"]))
    elements.append(Paragraph(f"Sehr geehrte/r Frau/Herr {submission.first_name} {submission.last_name},"))
    elements.append(Spacer(1 * cm, 0.4 * cm))

    elements.append(Paragraph("""<para align="justify">in der Theorie ist eine Bewertung oft 
    leicht nachzuvollziehen,  im Einsatz  als Kampfrichter/-in treten dann je nach Erfahrung, 
    Praxis und Teilnehmeranzahl teilweise erhebliche Schwierigkeiten auf, das Gesehene richtig 
    und im Sinne der Aktiven gerecht auf die Wertungszettel zu bringen.  </para>"""))
    elements.append(Spacer(1 * cm, 0.4 * cm))

    elements.append(Paragraph("""<para align="justify">Bodybuilding ist und bleibt eine 
    Präsentationsportart, daher muss dieser Aspekt bei der Wertung für die jeweiligen 
    Pflichtposen bzw. -drehungen und der evtl. beinhalteten Posingkür berücksichtigt werden. 
    Neben den Kenntnissen der gültigen Wettkampfregeln gilt es für die Kampfrichter/-innen 
    insbesondere auch, den DBFV e. V. bei den jeweiligen Wettkämpfen angemessen in der zu 
    repräsentieren.</para>"""))
    elements.append(Spacer(1 * cm, 0.4 * cm))

    elements.append(Paragraph("""Wir wünschen eine erfolgreiche Wettkampfsaison"""))
    elements.append(Spacer(1 * cm, 1 * cm))
    elements.append(Paragraph("""DBFV e.V."""))
    elements.append(Paragraph("""Geschäftstselle"""))
    elements.append(qr_image)
    doc.build(elements)

    return doc
