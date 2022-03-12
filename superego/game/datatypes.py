from typing import Any, List, Callable


class Carousel:
    def __init__(self, initial_items: List[Any] = None):
        self._items: List[Any] = list()
        if initial_items:
            self._items = initial_items

    def add(self, item: Any) -> None:
        self._items.append(item)

    def pop_push(self) -> Any:
        item = self._items.pop(0)
        self._items.append(item)
        return item

    def __len__(self):
        return len(self._items)

    def pop(self) -> Any:
        return self._items.pop(0)

    def find_remove(self, criteria: Callable) -> None:
        self._items = list(filter(criteria, self._items))

    @property
    def front(self) -> Any:
        return self._items[0]

    @property
    def items(self) -> List[Any]:
        return self._items

