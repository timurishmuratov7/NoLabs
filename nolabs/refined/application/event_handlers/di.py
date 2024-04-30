from nolabs.refined.application.event_handlers import AminoAcidCreatedEventHandler, ProteinCreatedEventHandler
from nolabs.refined.domain.event_dispatcher import EventDispatcher


class EventHandlersDependencies:
    @staticmethod
    def inject():
        event_handlers = [
            AminoAcidCreatedEventHandler(),
            ProteinCreatedEventHandler()
        ]

        types = [type(eh) for eh in event_handlers]
        for event_handler in event_handlers:
            if types.count(type(event_handler)) > 1:
                raise RuntimeError(f'Event handler {type(event_handler)} was registered multiple times')

            EventDispatcher.add_event_handler(event_handler)