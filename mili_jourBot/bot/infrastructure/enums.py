
from aenum import Enum, auto
from django.db.models import TextChoices

from django.utils.translation import gettext_lazy as _

import datetime

import portion as P



class PresenceMode(TextChoices):
    LIGHT_MODE = 'L', _('light')
    NORMAL_MODE = 'N', _('normal')
    HARDCORE_MODE = 'H', _('hardcore')
    SCHEDULE_MODE = 'schedule'
    ZOOM_MODE = 'zoom'
    #TODO: add an event mode

default = PresenceMode.NORMAL_MODE #TODO: use def default instead


class ReportMode(Enum):
    TODAY = auto()
    LAST = auto()
    ON_DATE = auto()
    DOSSIER = auto()
    class Flag(Enum):
        DOCUMENT = 'doc'
        TEXT = 'text'


class RegistrationMode(Enum):

    REREGISTER = 're'
    DELETE = 'delete'

all_modes = {PresenceMode, ReportMode, RegistrationMode}


class Schedule: #Do not try to deceive the poll
    first_lesson_interval = P.openclosed(datetime.time(8, 10, 0), datetime.time(10, 0, 0))
    second_lesson_interval = P.openclosed(datetime.time(10, 20, 0), datetime.time(11, 55, 0))
    third_lesson_interval = P.openclosed(datetime.time(12, 15, 0), datetime.time(13, 50, 0))
    fourth_lesson_interval = P.openclosed(datetime.time(14, 10, 0), datetime.time(15, 45, 0))
    fifth_lesson_interval = P.openclosed(datetime.time(16, 5, 0), datetime.time(17, 30, 0))
    sixth_lesson_interval = P.openclosed(datetime.time(17, 50, 0), datetime.time(19, 15, 0))

    recess = datetime.timedelta(minutes=20)

    lessons_intervals = {1: first_lesson_interval,
                         2: second_lesson_interval,
                         3: third_lesson_interval,
                         4: fourth_lesson_interval,
                         5: fifth_lesson_interval,
                         6: sixth_lesson_interval}

    @classmethod
    def lesson_match(cls, time):
        lessons = cls.lessons_intervals

        for l in lessons:
            if lessons[l].contains(time):

                return l
        return None


class PresencePollOptions(Enum):
    Present = 0
    Absent = 1