
from aenum import Enum, auto
from django.db.models import TextChoices

from django.utils.translation import gettext_lazy as _


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


class PresencePollOptions(Enum):
    Present = 0
    Absent = 1