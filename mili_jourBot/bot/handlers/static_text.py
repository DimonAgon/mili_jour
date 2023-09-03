
from typing import Type

from ..infrastructure.enums import PresencePollOptions

#greeting
greeting_text = "Mili_jour (Military Journal)." \
               " Бота створено для підтримки роботи командирського складу учбових взводів." \
               " Надано можливість ведення журналу відвідувань через команди. Проект на стадії розробки." \
               " Дійовість деяких аспектів буде перевірена та перероблена за необхідності."

#HELP
HELPFUL_REPLY = f"Для роботи необхідно виконати реєстрацію журналу взводу та ЗАРЕЕСТРУВАТИСЬ." \
                    "\nПодальше, право на взаємодію із ботом покладається на командирський склад." \
                    "\nСписок команд наведено нижче:" \
                    "\n/start– введення у бот" \
                    "\n/help– інструкція до взаємодії із ботом" \
                    "\n/register– реєструвати профіль" \
                    "\n/register_journal– створити журнал відвідувань" \
                    "\n/cancel– відмінити реєстрацію aбо вказання причини відсутності" \
                    "\n/who_s_present– створити опитування щодо присутності" \
                    "\n/absence_reason– вказати причину відсутності" \
                    "\n/today_report– викликати звіт за сьогоднішній день" \
                    "\n/last_report– викликати останній звіт" \
                    "\n/on_date_report– викликати звіт за датою"

#registration
profile_registration_text = "ініціюю реєстрацію"

group_registration_text = "Ініціюю реєстрацію взводу"

registration_canceling_text = "Процес реєстрації було перервано"

#absence
absence_reason_share_suggestion_text = "Вказати причину відстутності? Т/Н"

#presence options
def presence_option_to_string(presence_option: Type[PresencePollOptions]):
    match presence_option:
        case PresencePollOptions.Present:
            return "Я"
        case PresencePollOptions.Absent:
            return "Відсутній"

#validation
no_mode_validation_error_message = "Помилка, вкажіть режим"

wrong_mode_validation_error_message = "Помилка, вказано невірний режим"

no_arguments_validation_error_message = "Помилка, вкажіть аргументи"

wrong_lessons_validation_error_mesage = "Помилка, очікується послідовність занять"

wrong_date_validation_error_message = "Помилка, очікується дата"

no_additional_arguments_required = "Помилка, режим не потребує послідовності занять"

out_of_lesson_absence_reason_sharing_error_message = "Помилка, причину відсутності вказати впродовж відповідного заняття"

on_present_absence_reason_sharing_error_message = "Помилка, вас відмічено як присутнього"

on_invalid_date_report_error_message = "Помилка, задана дата не відповідає жодному звіту взводу"

#forms validation
name_format_validation_error_message = "Ввести ім'я коректно"

name_availability_validation_error_message = "Профіль вже зареєстровано"

journal_format_validation_error_message = "Ввести номер взводу коректно"

journal_name_availability_validation_error_message = "Взвод вже зареєстровано"

journal_name_in_base_validation_error_message = "Взвод не зареєстровано"

ordinal_format_validation_error_message = "Ввести номер коректно"

strength_format_validation_error_message = "Ввести чисельність коректно"

#forms
#fields
journal_field_message = "Ввести номер взводу"

name_field_message = "Ввести Прізвище та Ім'я"

ordinal_field_message = "Ввести номер у списку"

strength_field_message = "Ввести чисельність взводу"

status_field_message = "Ввести причину відсутності (мінімальна кількість слів)"

#callback
profile_form_callback_message = "Профіль зареєстровано"

journal_form_callback_message = "Журнал відвідувань до взводу створено"

absence_reason_form_сallback_text = "Причину записано"

on_registration_fail_text = "Помилка, реєстрацію скасовано"

absence_reason_fail_text = "Помилка, причину не записано"

#logging


