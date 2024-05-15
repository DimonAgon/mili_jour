
from .logger import frame_track_logger as logger

import asyncio

from static_text.logging_messages import *

from contextlib import contextmanager

from functools import wraps

from typing import Any, Callable


def log_track_frame(
        specified_frame_name: str=None    ,
        total: bool=True                  ,
        untracked_data: set={}            ,
        tracked_data_: set={}             ,
        track_non_keyword_args: bool=True
) -> Callable:
    ...
    def log_track_frame_decorator(function: Callable) -> Callable:
        ...
        @contextmanager
        def log_track_frame_context(*args, **kwargs) -> None:
            tracked_keyword_data = dict(
                [item for item in kwargs.items() if item[0] not in untracked_data]
            ) \
                if not tracked_data_ \
                else tracked_data_

            tracked_data = (args, tracked_keyword_data) if track_non_keyword_args else tracked_keyword_data

            frame_name = specified_frame_name if specified_frame_name else function.__name__
            frame_description = f"{frame_name} {tracked_data}"

            if total:
                logger.info(frame_on_initiation_logging_info_message.format(frame_attributes=frame_description))

            try:
                yield

            except Exception:
                logger.exception(
                    frame_fail_logging_error_message.format(frame_attributes=frame_description),
                    exc_info=True
                )
            logger.info(frame_success_logging_info_message.format(frame_attributes=frame_description))

        @wraps(function)
        def log_track_frame_wrap(*args, **kwargs) -> Any:
            with log_track_frame_context(*args, **kwargs):
                return function(*args, **kwargs)


        @wraps(function)
        async def log_track_frame_wrap_async(*args, **kwargs) -> Any:
            with log_track_frame_context(*args, **kwargs):
                return await function(*args, **kwargs)

        context_wrap = log_track_frame_wrap_async if asyncio.iscoroutinefunction(function) else log_track_frame_wrap
        return context_wrap
    return log_track_frame_decorator





