"""
This module contains utilities which are shared between other modules.
"""

from typing import Any, Callable


class cached_property:  # pylint: disable=invalid-name
    """Descriptor that transforms a class method into a property whose value is
    computed once and then cached for subsequent accesses.

    Args:
        func (Callable[[Any], Any]): class method whose value should be cached

    .. note::

        Each class instance is associated with an independent cache.

    .. warning::

        Unlike ``functools.cached_property``, this descriptor is *not* safe for
        concurrent use.
    """

    def __init__(self, func: Callable[[Any], Any]) -> None:
        self.func = func
        self.caches = {}
        self.__doc__ = func.__doc__

    def __get__(self, instance: Any, _) -> Any:
        """Returns the (cached) value associated with the given instance."""
        # Edge case to support getattr() and generate Sphinx documentation.
        if instance is None:
            return self

        if instance not in self.caches:
            self.caches[instance] = self.func(instance)
        return self.caches[instance]

    def __set__(self, instance: Any, value: Any) -> None:
        """Sets the cache of the given instance to the provided value."""
        self.caches[instance] = value

    def __delete__(self, instance: Any) -> None:
        """Clears the cache of the given instance."""
        self.caches.pop(instance, None)
