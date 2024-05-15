import logging

from ..logger import handlers_logger as logger

from aiogram_forms import FormsManager
from aiogram_forms.errors import ValidationError

from .fields import NamedField
from static_text.utilities import *

from typing import Type, cast, Optional, Dict


class LoggedFormsManager(FormsManager):
    async def show(self, name: str) -> None:
        entity_container: Type['Form'] = self._get_form_by_name(name)

        first_entity: NamedField = cast(NamedField, entity_container.state.get_states()[0].entity)
        await self.state.set_state(first_entity.state)
        await self.event.answer(first_entity.label, reply_markup=first_entity.reply_keyboard)  # type: ignore[arg-type]
        logging.info(chat_field_message_to_logging_field_message(first_entity.label))

    async def handle(self, form: Type['Form']) -> None:
        """Handle form field."""
        state_label = await self.state.get_state()
        current_state: 'EntityState' = next(iter([
            st for st in form.state.get_states() if st.state == state_label
        ]))

        field: NamedField = cast(NamedField, current_state.entity)
        try:
            value = await field.process(
                await field.extract(self.event)
            )
            await field.validate(value)
        except ValidationError as error:
            error_message = field.error_messages.get(error.code) or error.message
            await self.event.answer(error_message, reply_markup=field.reply_keyboard)  # type: ignore[arg-type]
            return
        logger.info(
            field_validation_success_info_message.format(
                field_attributes = f"{field:name}"
            )
        )

        data = await self.state.get_data()
        form_data = data.get(form.__name__, {})
        form_data.update({field.state.state.split(':')[-1]: value})  # type: ignore[union-attr]
        await self.state.update_data({form.__name__: form_data})

        next_state_index = cast(
            Dict['EntityState', Optional['EntityState']],
            dict(zip(current_state.group, list(current_state.group)[1:]))
        )
        next_entity_state: Optional['EntityState'] = next_state_index.get(current_state)
        if next_entity_state:
            next_field: NamedField = cast(NamedField, next_entity_state.entity)
            await self.state.set_state(next_field.state)
            await self.event.answer(
                '\n'.join([
                              str(next_field.label),
                              str(next_field.help_text) or ""
                          ] if next_field.help_text else [str(next_field.label)]),
                reply_markup=next_field.reply_keyboard
            )
            logger.info(chat_field_message_to_logging_field_message(next_field.label))

        else:
            await self.state.set_state(None)
            await form.callback(self.event, **self.data)
