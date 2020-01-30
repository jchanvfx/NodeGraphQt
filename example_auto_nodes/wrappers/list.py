def append(self, object):
    self.append(object)
    return self


def clear(self):
    self.clear()
    return self


def copy(self):
    return self.copy()


def count(self, value):
    return self.count(value)


def extend(self, iterable):
    self.extend(iterable)
    return self

def index(self, value):
    return self.index(value)


def insert(self, index, obj):
    self.insert(index, obj)
    return self


def pop(self, index=-1):
    return self.pop(index)


def remove(self, value):
    return self.remove(value)


def reverse(self):
    self.reverse()
    return self


def sort(self):
    self.sort()
    return self


# custom functions
def get(self, index):
    return self.__getitem__(index)
