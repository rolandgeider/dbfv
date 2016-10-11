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

import datetime

from django.core.urlresolvers import reverse
from django.db import models
from django.utils import formats
from submission.models import State, SubmissionStarter

championship_fields = ('name', 'date', 'state', 'categories')
judge_fields = ('name', )
placement_fields = ('category', )
category_fields = ('name', 'category_type')
participation_fields = ('championship',)
assessment_fields = ('points',)
assessmentcollection_fields = ('round',)


class Championship(models.Model):
    '''
    A Championship
    '''
    class Meta:
        '''
        Configure other properties
        '''
        ordering = ["-date", "name"]

    name = models.CharField(verbose_name='Name',
                            max_length=50)
    '''
    The championship's name
    '''

    date = models.DateField(verbose_name='Datum')
    '''
    The championship's date
    '''

    state = models.ForeignKey(State,
                              verbose_name='Bundesland')
    '''
    The federal state the championship happens in
    '''

    categories = models.ManyToManyField('Category',
                                        verbose_name='Kategorien')
    '''
    All available categories for this championship
    '''

    def __unicode__(self):
        '''
        Return a more human-readable representation
        '''
        return u'{0} ({1})'.format(self.name, formats.date_format(self.date, "SHORT_DATE_FORMAT"))


    def get_absolute_url(self):
        '''
        Return the detail view URL
        '''
        return reverse('championship:championship:view', kwargs={'pk': self.pk})

    @property
    def total_participants(self):
        '''
        Returns the total number of participants
        '''
        return self.participation_set.count()


class Category(models.Model):
    '''
    Category in a Championship
    '''
    class Meta:
        '''
        Configure other properties
        '''
        ordering = ["name"]

    CATEGORY_TYPE_BB = '3'
    CATEGORY_TYPE_OTHERS = '2'
    CATEGORY_TYPE = (
        (CATEGORY_TYPE_BB, 'Bodybuilding allgemein (3 Runden)'),
        (CATEGORY_TYPE_OTHERS, 'Andere Klassen (2 Runden)'),
    )

    name = models.CharField(verbose_name='Name',
                            max_length=50)
    '''
    The category's name
    '''

    category_type = models.CharField(
        verbose_name='Anzahl der Runden',
        max_length=6,
        choices=CATEGORY_TYPE,
        default=CATEGORY_TYPE_BB,
    )
    '''
    The type of category. This basically just controlls wether there will be
    two or three rounds.
    '''

    def __unicode__(self):
        '''
        Return a more human-readable representation
        '''
        return u'{0}'.format(self.name)


class Judge(models.Model):
    '''
    A Judge in a Championship
    '''
    class Meta:
        '''
        Configure other properties
        '''
        ordering = ["name"]

    name = models.CharField(verbose_name='Name',
                            max_length=50)
    '''
    The judge's name
    '''

    championship = models.ForeignKey(Championship,
                                     editable=False)
    '''
    The championship
    '''

    def __unicode__(self):
        '''
        Return a more human-readable representation
        '''
        return u'{0}'.format(self.name)


def limit_championship_choices():
    return {'date__gte': datetime.date.today()}


class Participation(models.Model):
    '''
    Intermediate table for championship participation
    '''

    class Meta:
        '''
        Configure other properties
        '''
        unique_together = (("championship", "participation_nr"),
                           ("championship", "submission"))

    submission = models.ForeignKey(SubmissionStarter,
                                   editable=False,
                                   verbose_name='Antrag')
    '''
    The user participating in a championship
    '''

    participation_nr = models.IntegerField(editable=False,
                                           verbose_name='Teilnehmernummer')
    '''
    A unique identification number per user and championship
    '''

    championship = models.ForeignKey(Championship,
                                     limit_choices_to=limit_championship_choices,
                                     verbose_name='Meisterschaft')
    '''
    The championship
    '''

    def __unicode__(self):
        '''
        Return a more human-readable representation
        '''
        return u'#{0} ({1})'.format(self.participation_nr,
                                    self.submission)

    def get_absolute_url(self):
        '''
        Return the detail view URL
        '''
        return reverse('championship:participation:view', kwargs={'pk': self.pk})


class Placement(models.Model):
    '''
    The final placement for an athlete in a championship for a specific category
    '''

    class Meta:
        '''
        Configure other properties
        '''
        unique_together = (("participation", "category"))
        ordering = ("category", "placement")

    participation = models.ForeignKey(Participation,
                                      editable=False,
                                      verbose_name='Teilnahme')
    '''
    The participation (basically, a championship) for this placement
    '''

    category = models.ForeignKey(Category,
                                 verbose_name='Kategorie')
    '''
    The categories in the championship
    '''

    placement = models.IntegerField(default=0,
                                    verbose_name='Platzierung')
    '''
    The user's placement in this championship and category
    '''

    points = models.PositiveSmallIntegerField(default=0,
                                              editable=False)
    '''
    The user's total points (for information purposes only)
    '''


class AssessmentCollection(models.Model):
    '''
    A collection of assessments, e.g. for different rounds
    '''

    championship = models.ForeignKey(Championship,
                                     editable=False)
    '''
    The championship this collection belongs to
    '''

    category = models.ForeignKey(Category,
                                 verbose_name='Kategorie')
    '''
    The categories in the championship
    '''

    round = models.PositiveSmallIntegerField(verbose_name='Runde')
    '''
    The round number
    '''

    def process_data(self):
        '''
        Processes and prepares data to be presented in one of the overview tables
        '''
        out = {}

        # Judges, participations
        for assessment in self.assessment_set.all():
            if not out.get(assessment.participation):
                out[assessment.participation] = {'participation': assessment.participation,
                                                 'points': None,
                                                 'placement': None,
                                                 'judges': []}
            out[assessment.participation]['judges'].append(assessment)

        # Points
        points = self.calculate_points()
        for participation in points:
            out[participation]['points'] = points[participation]['points']
            out[participation]['placement'] = points[participation]['placement']

        return out

    def get_sorted_results(self):
        '''
        Convenience method that returns the sorted results for this collection

        :return: a list of dictionaries
        '''
        tmp = []
        for value in self.process_data().values():
            tmp.append(value)
        sorted_list = sorted(tmp, key=lambda value: value['placement'])
        return sorted_list

    def calculate_points(self):
        '''
        Helper function that calculates the points for each participant

        :return: dictionary with athletes, points and their placement
        '''
        out = {}

        # Sum up the points
        for assessment in self.assessment_set.all():
            if not out.get(assessment.participation):
                out[assessment.participation] = {'points': 0, 'placement': 0}

            # Only valid assessments are taken into account
            if assessment.is_used:
                out[assessment.participation]['points'] += assessment.points

        # Calculate the placement (less points are better)
        counter = 1
        tmp = sorted(out.items(), key=lambda item: item[1]['points'])
        for participation_item in tmp:
            out[participation_item[0]]['placement'] = counter
            counter += 1

        return out


class Assessment(models.Model):
    '''
    An assessment of a judge about an athlete
    '''
    class Meta:
        '''
        Configure other properties
        '''
        ordering = ("participation", "judge", "points")

    collection = models.ForeignKey(AssessmentCollection,
                                   editable=False)
    '''
    The collection this assessment belongs to
    '''

    participation = models.ForeignKey(Participation,
                                      editable=False,
                                      verbose_name='Teilnahme')
    '''
    The participation (basically, an athlete) for this assessment
    '''

    judge = models.ForeignKey(Judge,
                              editable=False,
                              verbose_name='Kampfrichter')
    '''
    The judge making the assessment
    '''

    points = models.IntegerField(default=0,
                                 verbose_name='Punkte')
    '''
    Points given to the athlete
    '''

    def __unicode__(self):
        '''
        Return a more human-readable representation
        '''
        return u'points {0} (judge {1})'.format(self.points,
                                                self.judge)

    @property
    def is_used(self):
        '''
        Calculates whether this assessment is used for the total

        Rules:
        - for 5 or 7 judges, the best and worst assessments are discarded
        - for 9 judges the 2 best and worst assessments are discarded
        '''

        points = [a for a in self.collection.assessment_set.filter(participation=self.participation).order_by('points')]
        points_reverse = [a for a in self.collection.assessment_set.filter(participation=self.participation).order_by('-points')]

        if self.collection.championship.judge_set.count() in (5, 7):
            if self in (points[0], points_reverse[0]):
                return False
            return True
        elif self.collection.championship.judge_set.count() == 9:
            if self in (points[0], points[1], points_reverse[0], points_reverse[1]):
                return False
            return True
        # Should never happen
        else:
            pass