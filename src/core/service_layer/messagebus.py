import core.domain.events as events
import core.domain.commands as commands
import core.service_layer.unit_of_work as unit_of_work

import logging
from typing import Union, List, Dict, Type, Callable, Tuple
from tenacity import Retrying, RetryError, stop_after_attempt, wait_exponential

logger = logging.getLogger(__name__)

Message = Union[commands.Command, events.Event]


class MessageBus:
    def __init__(
        self,
        uow: unit_of_work.AbstractUnitOfWork,
        event_handlers: Dict[Type[events.Event], List[Tuple[str, Callable]]],
        command_handlers: Dict[Type[commands.Command], Tuple[str, Callable]],
    ):
        self.uow = uow
        self.event_handlers = event_handlers
        self.command_handlers = command_handlers

    def handle(self, message: Message):
        self.queue = [message]
        while self.queue:
            message = self.queue.pop(0)
            if isinstance(message, events.Event):
                self.handle_event(message)
            elif isinstance(message, commands.Command):
                self.handle_command(message)
            else:
                raise Exception(f"{message.__class__.__name__} was not an Event or Command")

    def handle_event(self, event: events.Event,):
        for handler_name, handler in self.event_handlers[type(event)]:
            try:
                for attempt in Retrying(
                    stop=stop_after_attempt(3),
                    wait=wait_exponential()
                ):

                    with attempt:
                        print(f"handling event {event.__class__.__name__ } with handler {handler_name}")
                        handler(event)
                        self.queue.extend(self.uow.collect_new_events())
                        print(f"Event {event.__class__.__name__} handled successfully with {handler_name}.")
            except RetryError as retry_failure:
                logger.error(
                    "Failed to handle %s event with % handler %s times, giving up!", event.__class__.__name__, handler_name,
                    retry_failure.last_attempt.attempt_number
                )
                continue

    def handle_command(self, command: commands.Command):
        logger.debug("handling command %s", command.__class__.__name__)
        try:
            handler_name, handler = self.command_handlers[type(command)]
            print(f"Handling command {command.__class__.__name__} with command handler: {handler_name}.")
            handler(command)
            self.queue.extend(self.uow.collect_new_events())
        except Exception:
            logger.exception("Exception handling command %s with command handler %s", command, handler_name)
            raise
        