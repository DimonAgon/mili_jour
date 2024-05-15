import portion as P

import datetime


class Schedule: #Do not try to deceive the poll #TODO: move to Schedule.py
    first_lesson_interval = P.openclosed(datetime.time(8, 10, 0), datetime.time(10, 0, 0))
    second_lesson_interval = P.openclosed(datetime.time(10, 20, 0), datetime.time(11, 55, 0))
    third_lesson_interval = P.openclosed(datetime.time(12, 15, 0), datetime.time(13, 50, 0))
    fourth_lesson_interval = P.openclosed(datetime.time(14, 10, 0), datetime.time(15, 45, 0))
    fifth_lesson_interval = P.openclosed(datetime.time(16, 5, 0), datetime.time(17, 30, 0))
    sixth_lesson_interval = P.openclosed(datetime.time(17, 50, 0), datetime.time(19, 15, 0))
    ninth_lesson_interval = P.openclosed(datetime.time(19, 15, 0), datetime.time(23, 59, 0))

    recess = datetime.timedelta(minutes=20)

    lessons_intervals = {1: first_lesson_interval,
                         2: second_lesson_interval,
                         3: third_lesson_interval,
                         4: fourth_lesson_interval,
                         5: fifth_lesson_interval,
                         6: sixth_lesson_interval,
                         9: ninth_lesson_interval}

    @classmethod
    def lesson_match(cls, time):
        lessons = cls.lessons_intervals

        for l in lessons:
            if lessons[l].contains(time):

                return l
        return None