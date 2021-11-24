# -------------------------------------------------------------------------------
#
#  Copyright (c) FotoNation.
#  All rights reserved. Confidential.
#
# -------------------------------------------------------------------------------


from boot_django import boot_django

# First we need to setup django
boot_django()

from django.contrib.auth.models import Group, User
from django.core.management import call_command


def main():
    call_command("makemigrations")
    call_command("migrate")

    group_admin = Group.objects.create(name="admin")
    Group.objects.create(name="students")
    Group.objects.create(name="teachers")


    admin = User.objects.create_superuser(username='admin', email='admin@example.com', password='admin..')

    group_admin.user_set.add(admin)


if __name__ == '__main__':
    main()
