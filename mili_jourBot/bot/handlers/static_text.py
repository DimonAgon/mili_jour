
from typing import Type

from ..infrastructure.enums import PresencePollOptions

#message
#command
#start
greeting_text = "Mili_jour (Military Journal)." \
               " Бота створено для підтримки роботи командирського складу учбових взводів." \
               " Надано можливість ведення журналу відвідувань через команди."

#help
HELPFUL_REPLY = f"Для роботи необхідно виконати реєстрацію журналу взводу та ЗАРЕЕСТРУВАТИСЬ." \
                    "\nПодальше, право на взаємодію із ботом покладається на командирський склад." \
                    "\nСписок команд наведено нижче:" \
                    "\n/start– введення у бот" \
                    "\n/help– інструкція до взаємодії із ботом" \
                    "\n/register– реєструвати профіль" \
                    "\n/register_journal– створити журнал відвідувань" \
                    "\n/cancel– перервати ввід даних" \
                    "\n/presence– створити опитування щодо присутності" \
                    "\n/absence_reason– вказати причину відсутності" \
                    "\n/today_report– викликати звіт за сьогоднішній день" \
                    "\n/last_report– викликати останній звіт" \
                    "\n/on_date_report– викликати звіт за датою" \
                    "\n/set_journal– відкрити журнал певного взводу" \
                    "\n/call- викликати студента за ім'ям," \
                    "\nщоб переслати йому повідомлення" \
                    "\n/groupcall– викликати взвод за номером," \
                    "\nщоб зробити об'яву"

#registration
#profile
profile_registration_text = "ініціюю реєстрацію"

#group
group_registration_text = "Ініціюю реєстрацію взводу"

#superuser
key_is_unauthentic_text = "Ключ суперкористувача не є дійсним. Ввeсти ключ повторно"

#presence
lesson_skipped_text = "Заняття {} пропущено, час заняття вичерпано"

#absence_reason
absence_reason_share_suggestion_text = "Вказати причину відстутності? Т/Н"

#report
report_text = "Таблиця присутності, Звіт за {}"

#set_journal
journal_set_text = "Журнал взводу {} відкрито"

#call
enter_profile_name_message = "Ввести Прізвище та Ім'я студента"
user_inform_text = "Студенту {}, надіслати наступні повідомлення"

#groupcall
enter_journal_name_message = "Ввести номер взводу"
group_inform_text = "Взвод {} сповістити:"

#cancel
registration_canceling_message = "Реєстрацію було перервано"

absence_reason_share_canceling_message = "Вказання причини відсутності перервано"

journal_unset_message = "Журнал закрито"

call_canceling_message = "Прийняття повідомлень завершено"

group_inform_canceling_message = "Оповіщення скасовано"

no_state_message = "Стан не встановлено, або було скасовано"

#states
inform_message = "Повідомлення від викладача:"
group_inform_message = "Об'ява:"

#filters
is_not_now_speaking_error_message = "*дочекатись відповіді співрозмовника"

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

invalid_parameters_report_error_message = "Помилка, за даними параметрами не знайдено жодного звіту взводу"

#forms validation
name_format_validation_error_message = "Ввести Прізвище, ім'я коректно"

name_availability_validation_error_message = "Профіль вже зареєстровано"

profile_by_name_not_in_db_error_message = "Профіль за заданим ім'ям не зареєстровано"

journal_format_validation_error_message = "Ввести номер взводу коректно"

journal_name_availability_validation_error_message = "Взвод вже зареєстровано"

journal_name_in_base_validation_error_message = "Взвод не зареєстровано"

ordinal_format_validation_error_message = "Ввести номер коректно"

strength_format_validation_error_message = "Ввести чисельність коректно"

#forms
#fields
superuser_key_field_message = "Ввести ключ суперкористувача"

journal_field_message = "Ввести номер взводу"

name_field_message = "Ввести Прізвище та Ім'я"

ordinal_field_message = "Ввести номер у списку"

strength_field_message = "Ввести чисельність взводу"

status_field_message = "Ввести причину відсутності (мінімальна кількість слів)"

#callback
superuser_form_callback_message = "Cуперкористувача зареєстровано"

profile_form_callback_message = "Профіль зареєстровано"

journal_form_callback_message = "Журнал відвідувань до взводу створено"

absence_reason_form_сallback_text = "Причину записано"

on_registration_fail_text = "Помилка, реєстрацію скасовано"

absence_reason_fail_text = "Помилка, причину не записано"

#logging
#info
statuses_amended_for_group_info_message = "statuses amended for group {}"

lesson_poll_sent_to_group_info_message = "lesson {} poll sent to {}"

lesson_poll_stopped_info_message = "lesson {} poll has been stopped at {}"

data_entering_canceled = "data entering canceled at {}"

poll_sent_info_message = "poll sent to {} mode: {}"

poll_stopped_info_message = "poll has been stopped at {}"

poll_answer_info_message = "poll answer {}:{} from {}"

presence_set_for_user_info_message = "presence set for user {}"

absence_reason_form_initiated_info_message = "absence reason form initiated for user {}"

superuser_created_info_message = "A superuser created for user_id {}"

superuser_registration_form_initiated_info_message = "superuser registration form initiated for user {}"

superuser_key_info_message = 'user {} superuser key: {}'

profile_registration_form_initiated_info_message = "profile registration form initiated for user {}"

profile_created_info_message = "A profile created for user_id {}"

journal_registration_form_initiated_info_message = "journal registration form initiated at {}"

journal_created_info_message = "A journal created for group_id {}"

report_requested_info_message = "report requested at {}, mode: {}, flag: {}"

today_report_initiated_info_message = "today report initiated for group {}, mode: {}"

today_entries_initiated_info_message = "today entries initiated for group {}"

lesson_entries_initiated_info_message = "lesson {} entries initiated for group {}"

#error
#command
#args
no_arguments_logging_error_message = "Command initiation failed\nError: no arguments expected"

#presence
lesson_skipped_logging_error_message = "lesson {} iteration skipped, lesson time is over"

#registration
#superuser
superuser_creation_error_message = "Failed to create a superuser for user_id {}\nError:{}"

#absence_reason
absence_reason_set_impossible_error_message = "Absence reason set is impossible for user {}, is_present: True"

#profile
profile_creation_error_message = "Failed to create a profile for user_id {}\nError:{}"

#journal
journal_creation_error_message = "Failed to create a journal for group_id {}\nError:{}"

#status
status_set_error_message = "Failed to set a status for journal_entry for an entry of profile of user id of {}\nError:{}"

#report
get_report_failed_error_message = "get report failed for {}, wrong parameters"

#set journal
no_journal_set_error_message = "no journal set for superuser {}"



