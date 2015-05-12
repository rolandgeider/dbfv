# -*- coding: utf-8 *-*

# This file is part of Kumasta
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

from django import template
from django.forms.widgets import CheckboxInput, ClearableFileInput
from django.template.loader import render_to_string
from django.forms.formsets import BaseFormSet

from submission.models import SubmissionStarter
from submission.models import user_type
from submission.models import USER_TYPE_BUNDESVERBAND
from submission.models import USER_TYPE_USER

register = template.Library()


@register.simple_tag
def render_submission_list(submissions, user, filter_mode, submission_type='starter'):
    '''
    Render a table with submissions

    :param submissions: list with submissions
    :param user: current user
    :param filter_mode what submissions to list (open, closed, etc.)
    :param submission_type The type of the submission. Allowed values: starter, gym, judge
    '''

    if submission_type == 'starter':
        url_fragment = ''
    elif submission_type == 'gym':
        url_fragment = '-studio'
    elif submission_type == 'judge':
        url_fragment = '-judge'

    context = dict()
    context['SUBMISSION_STATUS_EINGEGANGEN'] = SubmissionStarter.SUBMISSION_STATUS_EINGEGANGEN
    context['SUBMISSION_STATUS_BEWILLIGT'] = SubmissionStarter.SUBMISSION_STATUS_BEWILLIGT
    context['SUBMISSION_STATUS_ABGELEHNT'] = SubmissionStarter.SUBMISSION_STATUS_ABGELEHNT

    submission_list = []
    if submissions:
        if filter_mode == 'open':
            submission_list = [i for i in submissions if i.submission_status ==
                               SubmissionStarter.SUBMISSION_STATUS_EINGEGANGEN]
        elif filter_mode == 'closed':
            submission_list = [i for i in submissions if i.submission_status !=
                               SubmissionStarter.SUBMISSION_STATUS_EINGEGANGEN]
        else:
            submission_list = [i for i in submissions]

    context['submission_list'] = submission_list
    context['submission_type'] = submission_type
    context['user_type'] = user_type(user)
    context['USER_TYPE_BUNDESVERBAND'] = USER_TYPE_BUNDESVERBAND
    context['USER_TYPE_USER'] = USER_TYPE_USER
    context['url_submission_view'] = 'submission{0}-view'.format(url_fragment)
    context['url_submission_edit'] = 'submission{0}-edit-status'.format(url_fragment)
    context['url_submission_delete'] = 'submission{0}-delete'.format(url_fragment)

    return render_to_string("tags/render_submission_list.html", context)


#
# Form utils
#
@register.filter(name='form_field_add_css')
def form_field_add_css(field, css):
    '''
    Adds a CSS class to a form field. This is needed among other places for
    bootstrap 3, which needs a 'form-control' class in the field itself
    '''
    return field.as_widget(attrs={"class": css})


@register.filter(name='is_checkbox')
def is_checkbox(field):
    '''
    Tests if a field element is a checkbox, as it needs to be handled slightly different

    :param field: a form field
    :return: boolen
    '''
    return field.field.widget.__class__.__name__ == CheckboxInput().__class__.__name__


@register.filter(name='is_fileupload')
def is_fileupload(field):
    '''
    Tests if a field element is a file upload, as it needs to be handled slightly different

    :param field: a form field
    :return: boolen
    '''
    return field.field.widget.__class__.__name__ == ClearableFileInput().__class__.__name__


@register.inclusion_tag('tags/render_form_element.html')
def render_form_field(field):
    '''
    Renders a form field with all necessary labels, help texts and labels
    within 'form-group'.

    See bootstrap documentation for details: http://getbootstrap.com/css/#forms
    '''

    return {'field': field}


@register.inclusion_tag('tags/render_form_submit.html')
def render_form_submit(save_text='Save', button_class='default'):
    """
    Comfort function that renders a submit button with all necessary HTML
    and CSS

    :param save_text: the text to use on the submit button
    :param button_class: CSS class to apply to the button, default 'default'
    """
    if button_class in ('default',
                        'primary',
                        'success',
                        'info',
                        'warning',
                        'danger',
                        'link'):
        button_class = button_class
    else:
        button_class = 'default'

    return {'save_text': save_text,
            'button_class': button_class}


@register.inclusion_tag('tags/render_form_errors.html')
def render_form_errors(form):
    """
    Renders the non-field errors of a form with all necessary HTML and CSS
    (non-field errors refer to errors that can't be associated to any single
    field)

    :param form: the form object
    """
    return {'form': form}


@register.inclusion_tag('tags/render_form_fields.html')
def render_form_fields(form, submit_text='Save', show_save=True):
    '''
    Comfort function that renders all fields in a form, as well as the submit
    button

    Internally it simply calls the other table_form_* functions and will render
    the fields in the order they were defined. If you want to change this, you
    need to call table_form_field for each field yourself. This function will
    also render a hidden field with a CSRF token, so be sure to pass it to the
    template.

    It is still necessary to enclose its output in <form> tags!

    :param form: the form to be rendered
    :param save_text: the text to use on the submit button
    '''

    return {'form': form,
            'show_save': show_save,
            'submit_text': submit_text}
