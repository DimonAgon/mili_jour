
from typing import Type

from bot.infrastructure.enums import PresencePollOptions

from prettytable import PrettyTable

#--------------------------------------------------------universal------------------------------------------------------

#keywords

    #particles
negation_kw = "не"
already_kw = "вже"
yet_kw = "ще" #TODO: replace with "досі"
on_kw = "на"
under = "під"
to_kw = "до"
and_kw = "та"
as_kw = "як"
from_kw = "від"
    #p̶a̶r̶t̶i̶c̶l̶e̶s̶

    #nouns
name_nom_kw = "назва"; name_obj_kw = "назвою"
id_kw = "ідентифікатор"
you_nom_kw = "ви"; you_gen_kw = "вас"
admin_kw = "адмін"
success_kw = "успіх"
fail_kw = "помилка"
initiation_kw = "ініціація"
registration_nom_kw = "реєстрація"; registration_acc_kw = "реєстрацію"
creation_kw = "створення"
entering_input_kw = "ввід"
specifying_input_kw = "вказання"
key_kw = "ключ"
time_kw = "час"
parameters_kw = "параметри"
corrections_kw = "виправлення"
entries_nom_kw = "записи "; entries_pos_kw = "записів"
mode_kw = "режим"
argument_kw = "аргумент"; arguments_kw = "аргументи"
flag_kw = "флаг"
object_kw = "об'єкт"
id_kw = "ідентифікатор"
date_kw = "дата"
reference_kw = "посилання"; references_kw = "посилання"
presence_nom_kw = "присутність"; presence_gen_kw = "присутності"; presence_acc_kw = "присутності"
table_nom_kw = "таблиця"; table_acc_kw = "таблицю"
    #n̶o̶u̶n̶s̶

    #verbs
initiating_kw = "ініціалізується"
expected_kw = "очікується"
is_kw = "є";
have_been_kw = "було"
register_kw = "зареєструвати"
enter_kw = "ввести"
specify_kw = "вказати"
exists_kw = "існує"
delete_kw = "видалити"
cancel = "cкасувати"
open_kw = "відкрити"
provide_kw = "надати"
    #v̶e̶r̶b̶s̶

    #adjectives
adj_your_masc_kw = "ваш"; adj_your_fem_kw = "ваша"; adj_your_neut = "ваше"
adj_valid_masc_kw = "дійсний"; adj_valid_fem_kw = "дійсна"; adj_valid_neut_kw = "дійсне"; adj_valid_plr_kw = "дійсні"
adj_format_like_masc_kw = "коректний"; adj_format_like_fem_kw = "коректна"; adj_format_like_neut_kw = "коректне"
adj_corresponding_mask_kw = "відповідний"; adj_corresponding_fem_kw = "відповідний"; adj_corresponding_neut_kw = "відповідне"
adj_specified_masc_kw = "вказаний"; adj_specified_fem_kw = "вказана"; adj_specified_neut_kw = "вказане"
adj_entered_mask_kw = "введений"; adj_entered_fem_kw = "введена"; adj_entered_neut_kw = "введене"
adj_existing_masc_kw = "інснуючий"; adj_existing_fem_kw = "існуюче"; adj_existing_neut_kw = "існуюча"
adj_authorised_mask_kw = "розпізнаний"; adj_authorised_fem_kw = "розпізнана"; adj_authorised_neut_kw = "розпізнане"; adj_authorised_plr_kw = "розпізнані "
adj_none_mask_kw = "жодний "; adj_none_fem_kw = "жодна "; adj_none_neut_kw = "жодне "
adj_present_mask_kw = "пристуній"; adj_present_fem_kw = "присутня"; adj_present_neut_kw = "присутнє"
adj_external_mask_kw = "зовнішній"; adj_external_fem_kw = "зовнішня"; adj_external_neut_kw = "зовнішнє"
adj_additional_mask_kw = "додатковий"; adj_additional_fem_kw = "додаткова"; adj_additional_neut_kw = "додаткове"; adj_additional_plr_kw = "додаткові"
adj_marked_mask_kw = "позначений"; adj_marked_fem_kw = "позначена"; adj_marked_neut_kw = "позначене"; adj_marked_plr_kw = "позначені"
adj_current_mask_kw = "поточний"; adj_current_fem_kw = "поточна"; adj_current_neut_kw = "поточне";
    #a̶d̶j̶e̶c̶t̶i̶v̶e̶s̶

of_group_kw = "взводу"

    #adverbs
adv_authorised_kw = "розпізнано"
adv_registered_kw = "зареєстровано"
adv_noted_kw = "записано"
adv_entered_kw = "введено"
adv_valid_kw = "дійсно"
adv_format_like_kw = "коректно"
adv_specified_kw = "вказано"
adv_deleted_kw = "видалено"
adv_canceled_kw = "скасовано"
adv_opened_kw = "відкрито"
adv_closed_kw = "закрито"
adv_skipped_kw = "пропущено"
adv_dredged_kw = "вичерпано"
adv_identified_kw = "визначено"
unconventionally_kw = "необхідно"
during_kw = "впродовж"
adv_recorded_kw = "внесено"
adv_applied_kw = "звернено"
adv_passed_kw = "передано"
of_type_kw = "виду"
adv_finished_kw = "завершено"
adv_created_kw = "створено"
adv_posted_kw = "опубліковано"
    #a̶d̶v̶e̶r̶b̶s

specified_kwabbrv_kw = 'вказ.' #TODO: remove _kw from var-name

#k̶e̶y̶w̶o̶r̶d̶s̶

#keyword combinations
external_id_kwc = f"{adj_external_mask_kw} {id_kw}"
#k̶e̶y̶w̶o̶r̶d̶ c̶o̶m̶b̶i̶n̶a̶t̶i̶o̶n̶s̶

#phrase parts

    #fields
minimum_word_quantity_pp = \
    "(мінімальна кількість слів)"
yes_or_no_pp = \
    "Т/Н"
    #f̶i̶e̶l̶d̶s̶

    #fail
    #f̶a̶i̶l̶

    #notice
    #n̶o̶t̶i̶c̶e

    #success
    #s̶u̶c̶c̶e̶s̶s̶

#p̶h̶a̶s̶e̶ p̶a̶r̶t̶s̶

#--------------------------------------------------------u̶n̶i̶v̶e̶r̶s̶a̶l̶------------------------------------------------------




#--------------------------------------------------------superuser------------------------------------------------------

#keywords

    #nouns
superuser_nom_kw = "суперкористувач"; superuser_acc_kw = "суперкористувача"
    #n̶o̶u̶n̶s̶

    #verbs
    #v̶e̶r̶b̶s̶

    #adjectives
    #a̶d̶j̶e̶c̶t̶i̶v̶e̶s̶

    #adverbs
    #a̶d̶v̶e̶r̶b̶s

#k̶e̶y̶w̶o̶r̶d̶s̶

#phrases

    #fields
    #̶f̶i̶e̶l̶d̶s̶

    #fail
is_superuser_check_fail_chat_error_message = \
    f"{fail_kw} {you_gen_kw} {negation_kw} {adv_authorised_kw}, {as_kw} {superuser_acc_kw}"
superuser_registration_fail_chat_error_message = \
    f"{superuser_acc_kw} {negation_kw} {have_been_kw} {adv_registered_kw}"
    #f̶a̶i̶l̶

    #notice
    #n̶o̶t̶i̶c̶e

    #success
superuser_registration_success_chat_message = \
    f"{superuser_acc_kw} {have_been_kw} {adv_registered_kw}"
    #s̶u̶c̶c̶e̶s̶s̶

#p̶h̶r̶a̶s̶e̶s

#--------------------------------------------------------s̶u̶p̶e̶r̶u̶s̶e̶r̶------------------------------------------------------




#---------------------------------------------------------profile-------------------------------------------------------

#keywords

profile_name_kwс = "прізвище-ім'я"
profile_ordinal_kwс = f"номер у списку {of_group_kw}"

    #nouns
profile_nom_kw = "профіль"; profile_dat_kw = "профілю"; profile_acc_kw = "профілю"
    #n̶o̶u̶n̶s̶

    #verbs
    #v̶e̶r̶b̶s̶

    #adjectives
    #a̶d̶j̶e̶c̶t̶i̶v̶e̶s̶

    #adverbs
    #a̶d̶v̶e̶r̶b̶s

#k̶e̶y̶w̶o̶r̶d̶s̶

#phrases

    #fields
profile_name_chat_field_message = \
    f"{enter_kw} {profile_name_kwс}"
profile_ordinal_chat_field_message = \
    f"{enter_kw} {profile_ordinal_kwс}"
    #f̶i̶e̶l̶d̶s̶

    #fail
profile_registration_fail_chat_error_message = \
    f"{profile_nom_kw} {negation_kw} {have_been_kw} {adv_registered_kw}" #TODO: add fail_kw + ", " at start
profile_deletion_fail_chat_error_message = \
    f"{profile_nom_kw} {negation_kw} {have_been_kw} {adv_deleted_kw}" #TODO: add fail_kw at + ", " at start
profile_is_registered_check_fail_chat_error_message = \
    f"{fail_kw}, {profile_nom_kw} {negation_kw} {have_been_kw} {adv_registered_kw}"
profile_is_not_registered_by_attributes_check_fail_chat_error_message = \
    f"{fail_kw}, {profile_nom_kw} {on_kw} {specified_kwabbrv_kw} {'{profile_attributes}'} {already_kw} {have_been_kw} {adv_registered_kw}"
profile_is_registered_by_attributes_сheck_fail_chat_error_message = \
    f"{fail_kw}, {profile_nom_kw} {on_kw} {specified_kwabbrv_kw} {'{profile_attributes}'} {yet_kw} {negation_kw} {have_been_kw} {adv_registered_kw}"
profile_name_format_validation_fail_chat_error_message = \
    f"{fail_kw}, {profile_name_kwс} {have_been_kw} {adv_entered_kw} {negation_kw} {adv_format_like_kw}"
profile_ordinal_format_validation_fail_chat_error_message = \
    f"{fail_kw}, {profile_ordinal_kwс} {have_been_kw} {adv_entered_kw} {negation_kw} {adv_format_like_kw}"
    #f̶a̶i̶l̶

    #notice
    #n̶o̶t̶i̶c̶e

    #success
profile_registration_success_chat_info_message = \
    f"{profile_nom_kw} {have_been_kw} {adv_registered_kw}"
profile_deletion_success_chat_info_message = \
    f"{profile_nom_kw} {have_been_kw} {adv_deleted_kw}"
    #s̶u̶c̶c̶e̶s̶s̶

#̶p̶h̶r̶a̶s̶e̶s̶

#---------------------------------------------------------p̶r̶o̶f̶i̶l̶e̶-------------------------------------------------------




#---------------------------------------------------------journal-------------------------------------------------------

#keywords

    #nouns
journal_nom_kw = "журнал"; journal_dat_kw = "журналу";
journal_name_kw = "номер"
journal_strength_kw = "чисельність"
    #n̶o̶u̶n̶s̶

    #verbs
    #v̶e̶r̶b̶s̶

    #adjectives
    #a̶d̶j̶e̶c̶t̶i̶v̶e̶s̶

    #adverbs
    #a̶d̶v̶e̶r̶b̶s

#k̶e̶y̶w̶o̶r̶d̶s̶

#phrases

    #fields
journal_name_chat_field_message = \
    f"{enter_kw} {journal_name_kw} {journal_dat_kw}"
journal_strength_chat_field_message = \
    f"{enter_kw} {journal_strength_kw}"
    #̶f̶i̶e̶l̶d̶s̶

    #fail
journal_registration_fail_chat_message = \
    f"{fail_kw} , {journal_nom_kw} {negation_kw} {have_been_kw} {adv_registered_kw}"
journal_existence_check_fail_chat_message = \
    f"{fail_kw} , {journal_nom_kw} {negation_kw} {exists_kw}"
journal_is_not_registered_by_attributes_check_fail_chat_error_message = \
    f"{fail_kw}, {journal_nom_kw} {on_kw} {specified_kwabbrv_kw} {'{journal_attributes}'} {already_kw} {have_been_kw} {adv_registered_kw}"
journal_is_registered_by_attributes_check_fail_chat_error_message = \
    f"{fail_kw}, {journal_nom_kw} {on_kw} {specified_kwabbrv_kw} {'{journal_attributes}'} {yet_kw} {negation_kw} {have_been_kw} {adv_registered_kw}"
journal_name_format_validation_fail_chat_error_message = \
    f"{fail_kw} {journal_name_kw} {journal_dat_kw} {have_been_kw} {adv_entered_kw} {negation_kw} {adv_format_like_kw}"
journal_strength_format_validation_fail_chat_error_message = \
    f"{fail_kw} {journal_strength_kw} {journal_dat_kw} {have_been_kw} {adv_entered_kw} {negation_kw} {adv_format_like_kw}"
journal_set_check_fail_chat_error_message = \
    f"{journal_nom_kw} {negation_kw} {have_been_kw} {adv_opened_kw}"
    #f̶a̶i̶l̶

    #notice
    #n̶o̶t̶i̶c̶e

    #success
journal_unset_success_chat_info_message = \
    f"{journal_nom_kw} {adv_closed_kw}"
journal_registration_success_chat_info_message = \
    f"{journal_nom_kw} {have_been_kw} {adv_registered_kw}"
journal_deletion_success_chat_info_message = \
    f"{journal_nom_kw} {have_been_kw} {adv_deleted_kw}"
journal_set_success_chat_info_message = \
    f"{journal_nom_kw} {adv_opened_kw}"
    #s̶u̶c̶c̶e̶s̶s̶

#̶p̶h̶r̶a̶s̶e̶s̶

#---------------------------------------------------------j̶o̶u̶r̶n̶a̶l̶-------------------------------------------------------




#--------------------------------------------------------subject--------------------------------------------------------

#keywords

    #nouns
subject_nom_kw = "предмет"; subject_gen_kw = "предмету"; subjects_kw = "предмети"
subject_name_nom_kw = "назва"; subject_name_acc_kw = "назву"
    #n̶o̶u̶n̶s̶

    #verbs
    #v̶e̶r̶b̶s̶

    #adjectives
    #a̶d̶j̶e̶c̶t̶i̶v̶e̶s̶

    #adverbs
    #a̶d̶v̶e̶r̶b̶s

#k̶e̶y̶w̶o̶r̶d̶s̶

#phrases

    #fields
subject_name_chat_field_message = \
    f"{enter_kw} {subject_name_acc_kw} {subject_gen_kw}"
    #f̶i̶e̶l̶d̶s̶

    #fail
subject_creation_fail_chat_error_message = \
    f"{fail_kw}, {subject_nom_kw} {negation_kw} {have_been_kw} {adv_created_kw}"
subject_is_created_by_attributes_check_fail_chat_error_message = \
    f"{fail_kw}, {subject_nom_kw} {on_kw} {specified_kwabbrv_kw} {'{subject_attributes}'} {yet_kw} {negation_kw} {have_been_kw} {adv_created_kw}"
subject_is_not_created_by_attributes_check_fail_chat_error_message = \
    f"{fail_kw}, {subject_nom_kw} {on_kw} {specified_kwabbrv_kw} {'{subject_attributes}'} {already_kw} {have_been_kw} {adv_created_kw}"
    #f̶a̶i̶l̶

    #notice
    #n̶o̶t̶i̶c̶e

    #success
subject_creation_success_chat_info_message = \
    f"{subject_nom_kw} {have_been_kw} {adv_created_kw}"

    #s̶u̶c̶c̶e̶s̶s̶

#p̶h̶r̶a̶s̶e̶s̶

#--------------------------------------------------------s̶u̶b̶j̶e̶c̶t̶--------------------------------------------------------




#---------------------------------------------------------lesson--------------------------------------------------------

#keywords

    #nouns
lesson_kw = "заняття"
lessons_nom_kw = "заняття"; lessons_gen_kw = "занять"
    #n̶o̶u̶n̶s̶

    #verbs
    #v̶e̶r̶b̶s̶

    #adjectives
    #a̶d̶j̶e̶c̶t̶i̶v̶e̶s̶

    #adverbs
    #a̶d̶v̶e̶r̶b̶s

#k̶e̶y̶w̶o̶r̶d̶s̶

#keyword combinations
lesson_sequence_kwc = "послідовність занять"
#k̶e̶y̶w̶o̶r̶d̶ c̶o̶m̶b̶i̶n̶a̶t̶i̶o̶n̶s̶

#phrases

    #fields
lesson_select_chat_field_message = \
    f"{specify_kw} {subject_nom_kw} {lesson_kw} {'{lesson_attributes}'}"
    #f̶i̶e̶l̶d̶s̶

    #fail
during_lesson_check_fail_chat_error_message = \
    f"{fail_kw}, {lesson_kw} {negation_kw} {adv_identified_kw}"
    #f̶a̶i̶l̶

    #notice
lesson_time_skipped_chat_info_message = \
    f"{lesson_kw} {'{lesson_attributes}'} {adv_skipped_kw}, {time_kw} {lesson_kw} {adv_dredged_kw}"
    #n̶o̶t̶i̶c̶e

    #success
    #s̶u̶c̶c̶e̶s̶s̶

#p̶h̶r̶a̶s̶e̶s̶

#---------------------------------------------------------l̶e̶s̶s̶o̶n̶--------------------------------------------------------




#--------------------------------------------------------schedule-------------------------------------------------------

#keywords

    #nouns
schedule_nom_kw = "розклад"; schedule_gen_kw = "розкладу";
schedules_kw = "розклади"
    #n̶o̶u̶n̶s̶

    #verbs
    #v̶e̶r̶b̶s̶

    #adjectives
    #a̶d̶j̶e̶c̶t̶i̶v̶e̶s̶

    #adverbs
    #a̶d̶v̶e̶r̶b̶s

#k̶e̶y̶w̶o̶r̶d̶s̶

#phrases

    #fields
schedule_id_chat_field_message = \
    f"{enter_kw} {id_kw} {schedule_gen_kw}"
    #f̶i̶e̶l̶d̶s̶

    #fail
schedule_creation_fail_chat_error_message = \
    f"{schedule_nom_kw} {negation_kw} {have_been_kw} {adv_created_kw}"
schedule_is_created_by_attributes_check_fail_chat_error_message = \
    f"{fail_kw}, {schedule_nom_kw} {on_kw} {specified_kwabbrv_kw} {'{schedule_attributes}'} {yet_kw} {negation_kw} {have_been_kw} {adv_created_kw}"
schedule_is_not_empty_check_fail_chat_error_message = \
    f"{fail_kw}, {schedule_nom_kw} {is_kw} порожній"
current_schedule_post_fail_chat_error_message = \
    f"{fail_kw}, {schedule_nom_kw} {negation_kw} {have_been_kw} {adv_posted_kw}"
current_schedule_by_attributes_existence_check_fail_chat_error_message = \
    f"{fail_kw}, {adj_current_mask_kw} {schedule_nom_kw} {yet_kw} {negation_kw} {have_been_kw} {adv_posted_kw}"
    #f̶a̶i̶l̶

    #notice
schedule_building_instruction = \
    f"{specify_kw} {subjects_kw} {to_kw} {lessons_gen_kw},\n вказати символ \"_\", за відсутності {lesson_kw}, за порядком,\n {specify_kw} \"{adv_finished_kw}\" при передчасному завершенні {schedule_gen_kw}"
schedule_creation_on_cancel_chat_info_message = \
    f"{creation_kw} {schedule_gen_kw} {negation_kw} {have_been_kw} {adv_finished_kw}"
    #n̶o̶t̶i̶c̶e

    #success
schedule_creation_success_chat_info_message = \
    f"{schedule_nom_kw} {'{schedule_attributes}'} {have_been_kw} {adv_created_kw}"
current_schedule_post_success_chat_info_message = \
    f"{schedule_nom_kw} {have_been_kw} {adv_posted_kw}"
    #s̶u̶c̶c̶e̶s̶s̶

#p̶h̶r̶a̶s̶e̶s̶

#--------------------------------------------------------s̶c̶h̶e̶d̶u̶l̶e̶-------------------------------------------------------




#-----------------------------------------------------absence_reason----------------------------------------------------

#keywords

    #nouns
    #n̶o̶u̶n̶s̶

    #verbs
    #v̶e̶r̶b̶s̶

    #adjectives
    #a̶d̶j̶e̶c̶t̶i̶v̶e̶s̶

    #adverbs
    #a̶d̶v̶e̶r̶b̶s

#k̶e̶y̶w̶o̶r̶d̶s̶

#keyword combinations
absence_reason_nom_kwc = "причина відсутності";  absence_reason_pos_kwc = "причини відсутності"; absence_reason_acc_kwc = "причину відсутності";
#k̶e̶y̶w̶o̶r̶d̶ c̶o̶m̶b̶i̶n̶a̶t̶i̶o̶n̶s̶

#phrases

    #fail
absence_reason_share_fail_chat_error_message = \
    f"{fail_kw}, {absence_reason_acc_kwc} {negation_kw} {have_been_kw} {adv_noted_kw}"
    #f̶a̶i̶l̶

    #fields
absence_reason_share_suggestion_chat_field_message = \
    f"{enter_kw} {absence_reason_acc_kwc}? {yes_or_no_pp}"
absence_reason_status_chat_field_message = \
    f"{enter_kw} {absence_reason_acc_kwc} {minimum_word_quantity_pp}"
    #f̶i̶e̶l̶d̶s̶

    #notice
absence_reason_share_on_canceling_chat_info_message = \
    f"{entering_input_kw} {absence_reason_acc_kwc} {have_been_kw} {adv_canceled_kw}"
    #n̶o̶t̶i̶c̶e

    #success
absence_reason_share_success_chat_info_message = \
    f"{absence_reason_acc_kwc} {have_been_kw} {adv_noted_kw}"
    #s̶u̶c̶c̶e̶s̶s̶

#p̶h̶r̶a̶s̶e̶s̶

#-----------------------------------------------------a̶b̶s̶e̶n̶c̶e̶ ̶r̶e̶a̶s̶o̶n̶----------------------------------------------------




#-----------------------------------------------------presence_table----------------------------------------------------

#keywords

    #nouns
    #n̶o̶u̶n̶s̶

    #verbs
    #v̶e̶r̶b̶s̶

    #adjectives
    #a̶d̶j̶e̶c̶t̶i̶v̶e̶s̶

    #adverbs
    #a̶d̶v̶e̶r̶b̶s

#k̶e̶y̶w̶o̶r̶d̶s̶

#keyword combinations
presence_table_nom_kwc = f"{table_nom_kw} {presence_gen_kw}"; presence_table_acc_kwc = f"{table_acc_kw} {presence_acc_kw}"
#k̶e̶y̶w̶o̶r̶d̶ c̶o̶m̶b̶i̶n̶a̶t̶i̶o̶n̶s̶

#phrases

    #fields
redo_report_chat_field_message = \
    f"{provide_kw} {presence_table_acc_kwc} {of_type_kw}"
    #f̶i̶e̶l̶d̶s̶

    #fail
report_table_format_validation_chat_error_message = \
    f"{presence_table_acc_kwc} {negation_kw} {have_been_kw} {adv_entered_kw} вищевказаного {of_type_kw}"
    #f̶a̶i̶l̶

    #notice
    #n̶o̶t̶i̶c̶e

    #success
    #s̶u̶c̶c̶e̶s̶s̶

#p̶h̶r̶a̶s̶e̶s̶

#-----------------------------------------------------p̶r̶e̶s̶e̶n̶c̶e̶_̶t̶a̶b̶l̶e̶----------------------------------------------------




#---------------------------------------------------------report--------------------------------------------------------

#keywords

    #nouns
report_nom_kw = "звіт за взвод"; report_dat_kw = "звіту за взвод"
    #n̶o̶u̶n̶s̶

    #verbs
    #v̶e̶r̶b̶s̶

    #adjectives
    #a̶d̶j̶e̶c̶t̶i̶v̶e̶s̶

    #adverbs
    #a̶d̶v̶e̶r̶b̶s

#k̶e̶y̶w̶o̶r̶d̶s̶

#phrases

    #fields
    #f̶i̶e̶l̶d̶s̶

    #fail
report_parameters_check_fail_chat_error_message = \
    f"{fail_kw}, {parameters_kw} {negation_kw} відповідають жодному icнyючому {report_dat_kw}"
report_redo_fail_chat_error_message = \
    f"{fail_kw}, {corrections_kw} {negation_kw} {have_been_kw} {adv_recorded_kw} {to_kw} {entries_pos_kw} {report_dat_kw}"
    #f̶a̶i̶l̶

    #notice
    #n̶o̶t̶i̶c̶e

    #success
report_redo_success_chat_info_message = \
    f"{corrections_kw} {adv_recorded_kw} {to_kw} {entries_pos_kw} {report_dat_kw}"
    #s̶u̶c̶c̶e̶s̶s̶

#p̶h̶r̶a̶s̶e̶s̶

#---------------------------------------------------------r̶e̶p̶o̶r̶t̶--------------------------------------------------------



#-----------------------------------------------------miscellaneous-----------------------------------------------------
#keywords

    #nouns
    #n̶o̶u̶n̶s̶

    #verbs
    #v̶e̶r̶b̶s̶

    #adjectives
    #a̶d̶j̶e̶c̶t̶i̶v̶e̶s̶

    #adverbs
    #a̶d̶v̶e̶r̶b̶s

#k̶e̶y̶w̶o̶r̶d̶s̶

#phrases

    #fields
key_field_chat_message = \
    f"{enter_kw} {key_kw}"
    #f̶i̶e̶l̶d̶s̶

    #fail
profile_is_applied_to_check_fail_chat_error_message = \
    f"{fail_kw}, {negation_kw} {have_been_kw} {adv_applied_kw} {to_kw} {profile_acc_kw}"
is_admin_check_fail_chat_error_message = \
    f"{fail_kw}, {you_gen_kw} {negation_kw} {adv_authorised_kw}, {as_kw} {admin_kw}"
arguments_pass_check_fail_logging_error_message = \
    f"{arguments_kw} {negation_kw} {have_been_kw} {adv_passed_kw}"
mode_pass_check_fail_chat_error_message = \
    f"{fail_kw}, {negation_kw} {have_been_kw} {adv_passed_kw} {mode_kw}"
mode_validation_fail_chat_error_message = \
    f"{fail_kw}, {adj_entered_mask_kw} {mode_kw} {negation_kw} {is_kw} {adj_valid_masc_kw}"
flag_validation_fail_chat_error_message = \
    f"{fail_kw}, {adj_entered_mask_kw} {mode_kw} {negation_kw} {is_kw} {adj_valid_masc_kw}"
additional_arguments_validation_fail_logging_error_message = \
    f"{fail_kw}, {adj_additional_plr_kw} {arguments_kw} {negation_kw} {is_kw} {adj_valid_plr_kw}"
arguments_pass_check_fail_chat_error_message = \
    f"{fail_kw}, {negation_kw} {have_been_kw} {adv_passed_kw} {arguments_kw}"
lessons_pass_check_fail_chat_error_message = \
    f"{fail_kw}, {expected_kw} {lesson_sequence_kwc}"
date_pass_check_fail_chat_error_message = \
    f"{fail_kw}, {expected_kw} {date_kw}"
no_additional_arguments_check_fail_chat_error_message = \
    f"{fail_kw}, {lesson_sequence_kwc} {negation_kw} {expected_kw}"
is_absent_check_fail_chat_error_message = \
    f"{fail_kw}, {you_nom_kw} {adj_marked_plr_kw} {as_kw} {adj_present_mask_kw}"
key_validation_fail_chat_error_message = \
    f"{key_kw} {negation_kw} {is_kw} {adj_valid_masc_kw}"
registration_fail_chat_error_message = \
    f"{fail_kw}, {registration_acc_kw}– {adv_canceled_kw}"
report_table_name_references_validation_fail_chat_error_message = \
    f"{negation_kw} {adv_entered_kw} {adv_format_like_kw} іменні дані"
model_object_external_id_unregistered_check_fail_chat_error_message = \
    f"{'{model}'} {adv_registered_kw} {on_kw} {adj_external_mask_kw} {id_kw}"
    #f̶a̶i̶l̶

    #notice
HELPFUL_REPLY = \
                f"Для роботи необхідно виконати реєстрацію журналу взводу та ЗАРЕЕСТРУВАТИСЬ." \
                "\nПодальше, право на взаємодію із ботом покладається на командирський склад." \
                "\n" \
                "\nСтандартний вигляд команди:" \
                "\n     команда мод агрументи флаг" \
                "\n" \
                "\nПриклади команд:" \
                "\n     /odr 01.01.1001 doc" \
                "\n     /p 1 2 3 4 5" \
                "\n     /register re" \
                "\n"\
                "\nСписок команд наведено нижче:" \
                "\n/start– введення у бот" \
                "\n/help– інструкція до взаємодії із ботом" \
                "\n" \
                "\n          Розділ Реєстрація" \
                "\n/register– реєструвати профіль" \
                "\n/register_journal– створити журнал відвідувань" \
                "\n            флаги розділу:" \
                "\n   {" \
                "\n    re– перереєструвати" \
                "\n    delete– видалити" \
                "\n    }" \
                "\n" \
                "\n/presence /p– створити опитування щодо присутності" \
                "\n                моди:" \
                "\n   {" \
                "\n    normal[N](за замовчуванням)–" \
                "\n         створити опитування на кожне заняття" \
                "\n    light[L]– створити опитування лише один раз," \
                "\n         (відмічатися лише, коли прибув(ла) на заняття)" \
                "\n    hardcore[H]– cтворити опитування на кожне заняття," \
                "\n         в випадковий момент заняття" \
                "\n    }" \
                "\n" \
                "\n/absence_reason /ar– вказати причину відсутності" \
                "\n" \
                "\n           Розділ Звіти" \
                "\n/today_report /tr– викликати звіт за сьогоднішній день" \
                "\n/last_report /lr– викликати останній звіт" \
                "\n/on_date_report /odr– викликати звіт за датою," \
                "\n" \
                "\n/today_schedule /ts- викликати розклад за сьогоднійній день" \
                "\n/last_schedule /ls- викликати останній розклад" \
                "\n/on_date_shcedule /ods- викликати розклад за датою" \
                "\n" \
                "\n/dossier– викликати список студентів" \
                "\n            флаги розділу:" \
                "\n   {" \
                "\n    text(за замовчуванням)–" \
                "\n         викликати в текстовому форматі" \
                "\n    doc– викликати в форматі файлу" \
                "\n    }" \
                "\n" \
                "\n/redo_report /rr– переробити звіт, надавши відповідну таблицю поправок" \
                "\n" \
                "\n/allreport /all_reports- викликати єдиний файл зі звітами" \
                "\n/create_subject- створити предмет" \
                "\n/create_schedule- створити розклад" \
                "\n/post_schedule- опублікувати розклад на вказану дату" \
                "\n/set_journal /sj– відкрити журнал певного взводу" \
                "\n" \
                "\n/call- викликати студента за ім'ям," \
                "\n     щоб надіслати йому повідомлення" \
                "\n/groupcall /gc– викликати взвод за номером," \
                "\n     щоб зробити об'яву" \
                "\n" \
                "\n/cancel– скасувати ввід даних" \
                "\n/leave_chat_delete_journal– видалити журнал," \
                "\n     покинути групу"
                # TODO: add additional arguments formats hint
start_chat_info_message = \
                "Mili_jour (Military Journal)." \
                " Бота створено для підтримки роботи командирського складу учбових взводів." \
                " Надано можливість ведення журналу відвідувань через команди."
inform_to_profile_user_chat_info_message = \
    "Студенту {profile_attributes}, надіслати наступні повідомлення"
group_inform_chat_info_message = \
    "Взвод {journal_attributes} сповістити:"
data_input_on_canceling_chat_info_message = \
    f"{entering_input_kw} даних {have_been_kw} {adv_canceled_kw}"
call_on_canceling_chat_info_message = \
    "Прийняття повідомлень припинено"
group_inform_on_canceling_chat_info_message = \
    f"Оповіщення {of_group_kw} {have_been_kw} скасовано"
state_check_fail_chat_info_message = \
    "Стан не встановлено, або було скасовано"
user_inform_to_receiver_chat_error_message = \
    f"Повідомлення {from_kw} {superuser_nom_kw}"
group_inform_to_receiver_chat_info_message = \
    "Об'ява:"
report_description_chat_info_message = \
    f"{presence_table_nom_kwc}, {report_nom_kw} {'{report_parameters}'}"
schedule_description_chat_info_message = \
    f"{schedule_nom_kw} {'{schedule_parameters}'}"
    #n̶o̶t̶i̶c̶e

    #success
    #s̶u̶c̶c̶e̶s̶s̶

#p̶h̶r̶a̶s̶e̶s̶

#tables
report_example = PrettyTable()
report_example.border = False
report_example.field_names = ["Студент", "№-заняття-n)"]
row = ["Xxxxxxx", "?"]
report_example.add_rows((row, row))
report_example_text = str(report_example)
#t̶a̶b̶l̶e̶s̶

#-----------------------------------------------------m̶i̶s̶c̶e̶l̶l̶a̶n̶e̶o̶u̶s̶-----------------------------------------------------
