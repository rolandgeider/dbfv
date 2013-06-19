# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'BankAccount'
        db.create_table(u'submission_bankaccount', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('owner_name', self.gf('django.db.models.fields.CharField')(max_length=100)),
            ('account_nr', self.gf('django.db.models.fields.CharField')(max_length=9)),
            ('bank_nr', self.gf('django.db.models.fields.CharField')(max_length=8)),
            ('bank_name', self.gf('django.db.models.fields.CharField')(max_length=30)),
        ))
        db.send_create_signal(u'submission', ['BankAccount'])

        # Adding model 'State'
        db.create_table(u'submission_state', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=100)),
            ('short_name', self.gf('django.db.models.fields.CharField')(max_length=3)),
            ('bank_account', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['submission.BankAccount'])),
        ))
        db.send_create_signal(u'submission', ['State'])

        # Adding model 'Gym'
        db.create_table(u'submission_gym', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=100)),
            ('email', self.gf('django.db.models.fields.EmailField')(max_length=75, blank=True)),
            ('state', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['submission.State'])),
        ))
        db.send_create_signal(u'submission', ['Gym'])

        # Adding model 'StateAssociation'
        db.create_table(u'submission_stateassociation', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('state', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['submission.State'])),
            ('bank_account', self.gf('django.db.models.fields.CharField')(max_length=100)),
        ))
        db.send_create_signal(u'submission', ['StateAssociation'])

        # Adding model 'Submission'
        db.create_table(u'submission_submission', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('gym', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['submission.Gym'])),
            ('anhang', self.gf('django.db.models.fields.files.FileField')(max_length=100)),
            ('creation_date', self.gf('django.db.models.fields.DateField')(auto_now_add=True, blank=True)),
            ('user', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User'])),
            ('submission_type', self.gf('django.db.models.fields.CharField')(max_length=2)),
            ('submission_status_lv', self.gf('django.db.models.fields.CharField')(default='1', max_length=2)),
            ('submission_status_bv', self.gf('django.db.models.fields.CharField')(default='1', max_length=2)),
        ))
        db.send_create_signal(u'submission', ['Submission'])

        # Adding model 'UserProfile'
        db.create_table(u'submission_userprofile', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('user', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['auth.User'], unique=True)),
            ('type', self.gf('django.db.models.fields.IntegerField')(default=-1, max_length=1)),
            ('state', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['submission.State'], null=True, blank=True)),
        ))
        db.send_create_signal(u'submission', ['UserProfile'])


    def backwards(self, orm):
        # Deleting model 'BankAccount'
        db.delete_table(u'submission_bankaccount')

        # Deleting model 'State'
        db.delete_table(u'submission_state')

        # Deleting model 'Gym'
        db.delete_table(u'submission_gym')

        # Deleting model 'StateAssociation'
        db.delete_table(u'submission_stateassociation')

        # Deleting model 'Submission'
        db.delete_table(u'submission_submission')

        # Deleting model 'UserProfile'
        db.delete_table(u'submission_userprofile')


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
        u'submission.submission': {
            'Meta': {'object_name': 'Submission'},
            'anhang': ('django.db.models.fields.files.FileField', [], {'max_length': '100'}),
            'creation_date': ('django.db.models.fields.DateField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'gym': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['submission.Gym']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'submission_status_bv': ('django.db.models.fields.CharField', [], {'default': "'1'", 'max_length': '2'}),
            'submission_status_lv': ('django.db.models.fields.CharField', [], {'default': "'1'", 'max_length': '2'}),
            'submission_type': ('django.db.models.fields.CharField', [], {'max_length': '2'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['auth.User']"})
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