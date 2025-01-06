import threading
import core.domain.events as events
import core.domain.commands as commands
import core.service_layer.unit_of_work as unit_of_work

import logging
import json
from datetime import datetime, timezone
from dataclasses import asdict
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
        log_file: str = "message_bus_log.json"
    ):
        self.uow = uow
        self.event_handlers = event_handlers
        self.command_handlers = command_handlers
        self.log_file = log_file
        self.queue = []
        self.metrics = {
            "queue_length": 0,
            "processed_messages": 0,
            "failed_messages": 0
        }

    def log_message(self, message: Message, handler_name: str, status: str, error: str = None):
        log_entry = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "message_type": message.__class__.__name__,
            "handler_name": handler_name,
            "status": status,
            "error": error,
            "message_data": asdict(message)
        }
        
        try:
            with open(self.log_file, 'a') as f:
                f.write(json.dumps(log_entry) + "\n")
                f.write(json.dumps(self.metrics) + "\n")
            logger.info(f"Logged message: {log_entry}")
        except Exception as e:
            logger.error("Failed to write log entry: %s", e)

    def handle(self, message: Message):
        self.queue.append(message)
        self.metrics["queue_length"] = len(self.queue)
        logger.info(f"Queue length: {self.metrics['queue_length']}")

        while self.queue:
            message = self.queue.pop(0)
            self.metrics["queue_length"] = len(self.queue)
            logger.info(f"Processing message: {message.__class__.__name__}, Queue length: {self.metrics['queue_length']}")
            print(f"Message type: {type(message)}")
            if isinstance(message, events.Event):
                print("Is an event")
                self.handle_event(message)
            elif isinstance(message, commands.Command):
                print("Is a command.")
                self.handle_command(message)
            else:
                print(type(message))
                raise Exception(f"{message.__class__.__name__} was not an Event or Command")

    def handle_event(self, event: events.Event):
        threads = []
        for handler_name, handler in self.event_handlers[type(event)]:
            thread = threading.Thread(target=self._handle_event_with_retry, args=(event, handler_name, handler))
            thread.start()
            threads.append(thread)
        
        for thread in threads:
            thread.join()

    def _handle_event_with_retry(self, event: events.Event, handler_name: str, handler: Callable):
        try:
            for attempt in Retrying(
                stop=stop_after_attempt(3),
                wait=wait_exponential()
            ):
                with attempt:
                    logger.debug(f"Handling event {event.__class__.__name__} with handler {handler_name}")
                    handler(event)
                    self.queue.extend(self.uow.collect_new_events())
                    logger.info(f"Event {event.__class__.__name__} handled successfully with {handler_name}.")
                    self.log_message(event, handler_name, "success")
                    self.metrics["processed_messages"] += 1
        except RetryError as retry_failure:
            logger.error(
                "Failed to handle %s event with handler %s %s times, giving up!", event.__class__.__name__, handler_name,
                retry_failure.last_attempt.attempt_number
            )
            self.log_message(event, handler_name, "failure", str(retry_failure))
            self.metrics["failed_messages"] += 1

    def handle_command(self, command: commands.Command):
        print("Command handler called.")
        logger.debug("Handling command %s", command.__class__.__name__)
        try:
            handler_name, handler = self.command_handlers[type(command)]
            print(handler_name, handler)
            logger.debug(f"Handling command {command.__class__.__name__} with command handler: {handler_name}.")
            handler(command)
            self.queue.extend(self.uow.collect_new_events())
            self.log_message(command, handler_name, "success")
            self.metrics["processed_messages"] += 1
        except Exception as e:
            logger.exception("Exception handling command %s with command handler %s", command, handler_name)
            self.log_message(command, handler_name, "failure", str(e))
            self.metrics["failed_messages"] += 1
            raise Exception

    def get_metrics(self):
        return self.metrics

# Ensure logging is configured to capture all levels
logging.basicConfig(level=logging.DEBUG)