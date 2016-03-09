class IdFactory(object):

    def __init__(self):
        self.reset()

    def reset(self):
        self.counter = 0

    def uid(self):
        self.counter += 1
        return self.counter


ID_FACTORY = IdFactory()


class MtpEntity(object):

    def __init__(self, info):
        self.uid = ID_FACTORY.uid()
        self.info = info

    def get_handles(self):
        return [self.get_uid()]

    def get_uid(self):
        return self.uid

    def set_parent(self, parent):
        '''
        :type parent: MtpObjectContainer
        :param parent: parent of this object
        '''
        self.parent = parent

    def get_info(self):
        '''
        :rtype: bytearray
        :return: the entity's info
        '''
        return self.info.pack()


class MtpEntityInfoInterface(object):

    def pack(self):
        '''
        :rtype: bytearray
        :return: the info
        '''
        raise NotImplementedError


class MtpObjectContainer(MtpEntity):

    def __init__(self, info):
        super(MtpObjectContainer, self).__init__(info)
        self.objects = []

    def get_objects(self):
        return self.objects[:]

    def add_object(self, obj):
        '''
        :type obj: MtpObject
        :param obj: MTP object to add
        '''
        self.objects.append(obj)
        obj.set_parent(self)

    def get_object(self, handle):
        if self.uid == handle:
            return self
        for obj in self.objects:
            res = obj.get_object(handle)
            if res is not None:
                return res
        return None

    def get_handles(self):
        handles = super(MtpObjectContainer, self).get_handles()
        for obj in self.objects:
            handles.extend(obj.get_handles())
        return handles
