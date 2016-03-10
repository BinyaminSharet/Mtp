from __future__ import absolute_import
from .mtp_base import MtpObjectContainer, MtpEntityInfoInterface
from .mtp_proto import MU16, MU32, MU64, MStr, AccessCaps


class MtpStorage(MtpObjectContainer):

    def __init__(self, info):
        super(MtpStorage, self).__init__(info)
        self.dev = None

    def add_object(self, obj):
        super(MtpStorage, self).add_object(obj)
        obj.set_storage(self)

    def set_device(self, dev):
        self.dev = dev

    def get_handles(self):
        handles = []
        for obj in self.objects:
            handles.extend(obj.get_handles())
        return handles

    def can_delete(self):
        return self.info.access in [AccessCaps.READ_WRITE, AccessCaps.READ_ONLY_WITH_DELETE]

    def can_write(self):
        return self.info.access == AccessCaps.READ_WRITE


class MtpStorageInfo(MtpEntityInfoInterface):

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
        self.st_type = st_type
        self.fs_type = fs_type
        self.access = access
        self.max_cap = max_cap
        self.free_bytes = free_bytes
        self.free_objs = free_objs
        self.desc = desc
        self.vol_id = vol_id

    def pack(self):
        return (
            MU16(self.st_type) +
            MU16(self.fs_type) +
            MU16(self.access) +
            MU64(self.max_cap) +
            MU64(self.free_bytes) +
            MU32(self.free_objs) +
            MStr(self.desc) +
            MStr(self.vol_id)
        )
