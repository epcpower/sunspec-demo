import contextlib
import os

import attr
import sunspec.core.device


def apply_decorators(decorators):
    def decorator(f):
        for decorator in reversed(decorators):
            f = decorator(f)

        return f

    return decorator


def click_show_default_true():
    # https://github.com/pallets/click/issues/646#issuecomment-435317967

    import functools

    import click

    click.option = functools.partial(click.option, show_default=True)


@contextlib.contextmanager
def fresh_smdx_path(*paths):
    original_pathlist = sunspec.core.device.file_pathlist
    sunspec.core.device.file_pathlist = sunspec.core.util.PathList()

    for path in paths:
        sunspec.core.device.file_pathlist.add(os.fspath(path))

    try:
        yield sunspec.core.device.file_pathlist
    finally:
        sunspec.core.device.file_pathlist = original_pathlist


@attr.s
class Flags(object):
    _model = attr.ib()
    _point = attr.ib()
    _names = attr.ib(default=attr.Factory(set), converter=set)

    def __attrs_post_init__(self):
        self._symbols = self._model.model.points[self._point].point_type.symbols
        self._valid_names = set(s.id for s in self._symbols)

        self._validate_names(*self._names)

        self._bit_map = {int(s.value): s.id for s in self._symbols}

    def _validate_names(self, *names):
        if len(names) == 0:
            return

        names = set(names)

        bad_names = names - self._valid_names

        if len(bad_names) > 0:
            raise Exception(
                'Invalid flag{} specified for {}: {}'
                .format('s' if len(bad_names) > 1 else '',
                        self._point,
                        ', '.join(str(n) for n in bad_names)
                )
            )

    def set(self, *names):
        self._validate_names(*names)
        for name in names:
            self._names.add(name)
        return self.to_int()

    def clear(self, *names):
        self._validate_names(*names)
        for name in names:
            self._names.discard(name)
        return self.to_int()

    def to_int(self):
        return sum(1 << int(s.value) for s in self._symbols
                   if s.id in self._names)

    def set_all(self):
        self._names = set(self._valid_names)
        return self.to_int()

    def clear_all(self):
        self._names = set()
        return self.to_int()

    def from_int(self, source):
        s = '{:b}'.format(source)
        highest_bit = max(self._bit_map.keys())
        if len(s) > highest_bit+1:
            raise Exception(
                'Highest bit is {} but int has bit {} set'
                .format(highest_bit, len(s)-1)
            )

        names = (self._bit_map[n] for n, b in enumerate(reversed(s))
                 if b == '1')
        self.clear_all()
        self.set(*names)

    def active(self):
        return [s.id for s in self._symbols if s.id in self._names]
