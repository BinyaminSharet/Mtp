class IdFactory(object):

    def __init__(self):
        self.reset()

    def reset(self):
        self.counter = 0

    def uid(self):
        self.counter += 1
        return self.counter


ID_FACTORY = IdFactory()


class MtpBaseObject(object):

    def __init__(self):
        self.uid = ID_FACTORY.uid()

    def get_uid(self):
        return self.uid
