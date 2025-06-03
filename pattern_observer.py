import abc
class Observer(metaclass= abc.ABCMeta):

    @abc.abstractmethod
    def notify(self):
        pass

class Subject(metaclass= abc.ABCMeta):

    @abc.abstractmethod
    def notifyAll(self):
        pass

    @abc.abstractmethod
    def register(self, ob):
        pass