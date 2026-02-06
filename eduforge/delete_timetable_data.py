#!/usr/bin/env python
import os
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()

from modules.timetable.models import SectionTimetable

count = SectionTimetable.objects.all().count()
SectionTimetable.objects.all().delete()
print(f"Deleted {count} timetable records")
