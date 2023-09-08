# Django
from collections import Counter

from django.contrib.auth.models import User
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    """
    Marks the user emails as verified
    """

    def handle(self, *args, **options):
        counter = Counter()

        with open("emails.txt", "r") as file:
            for email in file.readlines():
                try:
                    user = User.objects.get(email=email)
                    user.userprofile.email_verified = True
                    user.userprofile.save()
                    counter['verified'] += 1
                except User.DoesNotExist:
                    counter['not_found'] += 1

        print(counter)