from enum import Enum

import datetime

import portion as P



class WhoSPresentMode():
    LIGHT_MODE = 'light'
    NORMAL_MODE = 'normal'
    HARDCORE_MODE = 'hardcore'
    SCHEDULE_MODE = 'schedule'
    ZOOM_MODE = 'zoom'

default = WhoSPresentMode.LIGHT_MODE

class Schedule: #Do not try to deceive the poll
    first_lesson = P.openclosed(datetime.time(8, 10, 0), datetime.time(10, 0, 0))
    second_lesson = P.openclosed(datetime.time(10, 20, 0), datetime.time(11, 55, 0))
    third_lesson = P.openclosed(datetime.time(12, 15, 0), datetime.time(13, 50, 0))
    fourth_lesson = P.openclosed(datetime.time(14, 10, 0), datetime.time(15, 45, 0))
    fifth_lesson = P.openclosed(datetime.time(16, 5, 0), datetime.time(17, 30, 0))

    lessons = {1: first_lesson, 2: second_lesson, 3: third_lesson, 4: fourth_lesson, 5: fifth_lesson}

    @classmethod
    def lesson_match(cls, time):
        lessons = cls.lessons

        for l in lessons:
            if lessons[l].contains(time):

                return l
        return None