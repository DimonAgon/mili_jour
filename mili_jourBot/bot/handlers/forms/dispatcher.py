

from aiogram_forms.dispatcher import EntityDispatcher
from aiogram_forms import Form

from aiogram import types

from .manager import LoggedFormsManager

from typing import Type, Dict, Any, Callable, Awaitable


class LoggedFormsDispatcher(EntityDispatcher):
    def _get_entity_container_handler(
            self, container: Type['EntityContainer']
    ) -> Callable[..., Awaitable[None]]:
        """Get entity container event handler."""

        async def message_handler(event: types.Message, **data: Dict[str, Any]) -> None:
            """Entity container event handler, redirect to manager."""
            if issubclass(container, Form):
                manager = LoggedFormsManager(self, event, data)
                await manager.handle(container)
            else:
                raise RuntimeError(f'Container of type "{container.__class__.__name__}" is not supported!')

        return message_handler


dispatcher = LoggedFormsDispatcher()