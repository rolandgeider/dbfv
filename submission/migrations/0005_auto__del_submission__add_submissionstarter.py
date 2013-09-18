# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Deleting model 'Submission'
        db.delete_table(u'submission_submission')

        # Adding model 'SubmissionStarter'
        db.create_table(u'submission_submissionstarter', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('user', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User'])),
            ('date_of_birth', self.gf('django.db.models.fields.DateField')()),
            ('active_since', self.gf('django.db.models.fields.DateField')()),
            ('last_name', self.gf('django.db.models.fields.CharField')(max_length=30)),
            ('first_name', self.gf('django.db.models.fields.CharField')(max_length=30)),
            ('street', self.gf('django.db.models.fields.CharField')(max_length=30)),
            ('zip_code', self.gf('django.db.models.fields.IntegerField')(max_length=5)),
            ('tel_number', self.gf('django.db.models.fields.CharField')(max_length=20)),
            ('nationality', self.gf('django.db.models.fields.related.ForeignKey')(default=37, to=orm['submission.Country'])),
            ('height', self.gf('django.db.models.fields.IntegerField')(max_length=3)),
            ('weight', self.gf('django.db.models.fields.IntegerField')(max_length=3)),
            ('category', self.gf('django.db.models.fields.CharField')(max_length=1)),
            ('gym', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['submission.Gym'])),
            ('creation_date', self.gf('django.db.models.fields.DateField')(auto_now_add=True, blank=True)),
            ('submission_type', self.gf('django.db.models.fields.CharField')(max_length=2)),
            ('submission_status_bv', self.gf('django.db.models.fields.CharField')(default='1', max_length=2)),
        ))
        db.send_create_signal(u'submission', ['SubmissionStarter'])


    def backwards(self, orm):
        # Adding model 'Submission'
        db.create_table(u'submission_submission', (
            ('submission_status_bv', self.gf('django.db.models.fields.CharField')(default='1', max_length=2)),
            ('user', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User'])),
            ('nationality', self.gf('django.db.models.fields.related.ForeignKey')(default=37, to=orm['submission.Country'])),
            ('gym', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['submission.Gym'])),
            ('creation_date', self.gf('django.db.models.fields.DateField')(auto_now_add=True, blank=True)),
            ('submission_type', self.gf('django.db.models.fields.CharField')(max_length=2)),
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('anhang', self.gf('django.db.models.fields.files.FileField')(max_length=100)),
        ))
        db.send_create_signal(u'submission', ['Submission'])

        # Deleting model 'SubmissionStarter'
        db.delete_table(u'submission_submissionstarter')


    models = {
        u'auth.group': {
            'Meta': {'object_name': 'Group'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '80'}),
            'permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'})
        },
        u'auth.permission': {
            'Meta': {'ordering': "(u'content_type__app_label', u'content_type__model', u'codename')", 'unique_together': "((u'content_type', u'codename'),)", 'object_name': 'Permission'},
            'codename': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['contenttypes.ContentType']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        u'auth.user': {
            'Meta': {'object_name': 'User'},
            'date_joined': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'blank': 'True'}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'groups': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['auth.Group']", 'symmetrical': 'False', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'is_staff': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_superuser': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'last_login': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'user_permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'}),
            'username': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '30'})
        },
        u'contenttypes.contenttype': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        u'submission.bankaccount': {
            'Meta': {'object_name': 'BankAccount'},
            'account_nr': ('django.db.models.fields.CharField', [], {'max_length': '9'}),
            'bank_name': ('django.db.models.fields.CharField', [], {'max_length': '30'}),
            'bank_nr': ('django.db.models.fields.CharField', [], {'max_length': '8'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'owner_name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        u'submission.country': {
            'Meta': {'object_name': 'Country'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '20'})
        },
        u'submission.gym': {
            'Meta': {'ordering': "['state__name', 'name']", 'object_name': 'Gym'},
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'state': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['submission.State']"})
        },
        u'submission.state': {
            'Meta': {'object_name': 'State'},
            'bank_account': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['submission.BankAccount']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'short_name': ('django.db.models.fields.CharField', [], {'max_length': '3'})
        },
        u'submission.stateassociation': {
            'Meta': {'object_name': 'StateAssociation'},
            'bank_account': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'state': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['submission.State']"})
        },
        u'submission.submissionstarter': {
            'Meta': {'object_name': 'SubmissionStarter'},
            'active_since': ('django.db.models.fields.DateField', [], {}),
            'category': ('django.db.models.fields.CharField', [], {'max_length': '1'}),
            'creation_date': ('django.db.models.fields.DateField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'date_of_birth': ('django.db.models.fields.DateField', [], {}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '30'}),
            'gym': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['submission.Gym']"}),
            'height': ('django.db.models.fields.IntegerField', [], {'max_length': '3'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '30'}),
            'nationality': ('django.db.models.fields.related.ForeignKey', [], {'default': '37', 'to': u"orm['submission.Country']"}),
            'street': ('django.db.models.fields.CharField', [], {'max_length': '30'}),
            'submission_status_bv': ('django.db.models.fields.CharField', [], {'default': "'1'", 'max_length': '2'}),
            'submission_type': ('django.db.models.fields.CharField', [], {'max_length': '2'}),
            'tel_number': ('django.db.models.fields.CharField', [], {'max_length': '20'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['auth.User']"}),
            'weight': ('django.db.models.fields.IntegerField', [], {'max_length': '3'}),
            'zip_code': ('django.db.models.fields.IntegerField', [], {'max_length': '5'})
        },
        u'submission.userprofile': {
            'Meta': {'object_name': 'UserProfile'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'state': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['submission.State']", 'null': 'True', 'blank': 'True'}),
            'type': ('django.db.models.fields.IntegerField', [], {'default': '-1', 'max_length': '1'}),
            'user': ('django.db.models.fields.related.OneToOneField', [], {'to': u"orm['auth.User']", 'unique': 'True'})
        }
    }

    complete_apps = ['submission']