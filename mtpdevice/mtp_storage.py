from __future__ import absolute_import
from .mtp_base import MtpBaseObject
from .mtp_proto import AccessCaps
from .mtp_data_types import UInt16, UInt32, UInt64, MStr


class MtpStorage(MtpBaseObject):

    def __init__(self, info):
        super(MtpStorage, self).__init__()
        self.uid |= 0x00020000
        self.info = info
        self.dev = None
        self.objects = []

    def get_info(self):
        return self.info.pack()

    def get_object(self, handle):
        for obj in self.objects:
            res = obj.get_object(handle)
            if res:
                return res
        return None

    def add_object(self, obj):
        self.objects.append(obj)
        obj.set_storage(self)

    def get_objects(self):
        objs = []
        for obj in self.objects:
            objs.append(obj)
            objs.extend(obj.get_objects())
        return objs

    def set_device(self, dev):
        self.dev = dev

    def can_delete(self):
        return self.info.access.value in [AccessCaps.READ_WRITE, AccessCaps.READ_ONLY_WITH_DELETE]

    def can_write(self):
        return self.info.access.value == AccessCaps.READ_WRITE


class MtpStorageInfo(object):

    def __init__(
        self,
        st_type, fs_type, access,
        max_cap, free_bytes, free_objs,
        desc, vol_id
    ):
        '''
        :type st_type: uint from proto.StorageType
        :param st_type: storage type
        :type fs_type: uint from proto.FSType
        :param fs_type: filesystem type
        :type access: uint from proto.AccessCaps
        :param access: access capabilities
        :param max_cap: maximum capacity of the storage
        :param free_bytes: free space in bytes
        :param free_objs: free space in objects
        :type desc: str
        :param desc: storage description
        :type vol_id: str
        :param vol_id: volume identifier
        '''
        self.st_type = UInt16(st_type)
        self.fs_type = UInt16(fs_type)
        self.access = UInt16(access)
        self.max_cap = UInt64(max_cap)
        self.free_bytes = UInt64(free_bytes)
        self.free_objs = UInt32(free_objs)
        self.desc = MStr(desc)
        self.vol_id = MStr(vol_id)

    def pack(self):
        return (
            self.st_type.pack() +
            self.fs_type.pack() +
            self.access.pack() +
            self.max_cap.pack() +
            self.free_bytes.pack() +
            self.free_objs.pack() +
            self.desc.pack() +
            self.vol_id.pack()
        )
