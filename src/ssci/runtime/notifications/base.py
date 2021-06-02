import traceback
from abc import abstractmethod, ABC
from dataclasses import dataclass
from typing import List

from pyjackson.decorators import type_field


@type_field('type')
class Notifier(ABC):
    type = ...

    KNOWN = {
        'telegram': 'ssci.runtime.notifications.telegram.TelegramNotifier'
    }

    @abstractmethod
    def notify(self, msg):
        """"""


@dataclass
class MultiNotifier(Notifier):
    notifiers: List[Notifier]

    def notify(self, msg):
        exc = None
        for n in self.notifiers:
            try:
                n.notify(msg)
            except Exception as e:
                traceback.print_exc()  # TODO
                exc = e
        if exc is not None:
            raise exc
