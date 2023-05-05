from enum import Enum

import datetime

import portion as P



class WhoSPresentMode(Enum):
    LIGHT_MODE = 'light'
    NORMAL_MODE = 'normal'
    HARDCORE_MODE = 'hardcore'
    SCHEDULE_MODE = 'schedule'
    ZOOM_MODE = 'zoom'
    # TODO: add an event mode

default = WhoSPresentMode.LIGHT_MODE

class Schedule: #Do not try to deceive the poll
    first_lesson_interval = P.openclosed(datetime.time(8, 10, 0), datetime.time(10, 0, 0))
    second_lesson_interval = P.openclosed(datetime.time(10, 20, 0), datetime.time(11, 55, 0))
    third_lesson_interval = P.openclosed(datetime.time(12, 15, 0), datetime.time(13, 50, 0))
    fourth_lesson_interval = P.openclosed(datetime.time(14, 10, 0), datetime.time(15, 45, 0))
    fifth_lesson_interval = P.openclosed(datetime.time(16, 5, 0), datetime.time(17, 30, 0))
    ninth_lesson_interval = P.openclosed(datetime.time(0, 0, 0), datetime.time(3, 30, 0))

    lessons_intervals = {1: first_lesson_interval,
                         2: second_lesson_interval,
                         3: third_lesson_interval,
                         4: fourth_lesson_interval,
                         5: fifth_lesson_interval,
                         9: ninth_lesson_interval}

    @classmethod
    def lesson_match(cls, time):
        lessons = cls.lessons_intervals

        for l in lessons:
            if lessons[l].contains(time):

                return l
        return None