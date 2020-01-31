def clear(self):
    self.clear()
    return self


def copy(self):
    return self.copy()


def fromkeys(self, iterable, value=None):
    return self.fromkeys(iterable, value)


def get(self, key, default=None):
    return self.get(key, default)


def items(self):
    return list(self.items())


def keys(self):
    return list(self.keys())


def pop(self, index):
    return self.pop(index)


def popitem(self):
    return self.popitem()


def setdefault(self, key, default=None):
    self.setdefault(key, default)
    return self


def update(self, e):
    self.update(e)
    return self


def values(self):
    return list(self.values())
