'''
The object's binary data, the ObjectInfo dataset,
Object Properties and Object References
'''
from __future__ import absolute_import
import os
from .mtp_data_types import UInt32, UInt16, MStr, MDateTime
from .mtp_base import MtpBaseObject
from .mtp_proto import ResponseCodes
from .mtp_exception import MtpProtocolException


class MtpObject(MtpBaseObject):

    def __init__(self, data, info, properties):
        super(MtpObject, self).__init__()
        self.info = info
        self.set_data(data)
        self.properties = properties
        self.real_path = None
        self.objects = []
        self.storage = None
        self.parent = None

    def copy(self):
        '''
        .. todo:: copy properties ...
        '''
        new_data = None if self.data is None else self.data[:]
        new_info = self.info.copy()
        new_obj = MtpObject(new_data, new_info, self.properties)
        for obj in self.objects:
            new_obj.add_object(obj.copy())

    def get_info(self):
        return self.info.pack()

    def get_objects(self):
        return self.objects[:]

    def add_object(self, obj):
        self.objects.append(obj)
        obj.set_parent(self)
        obj.set_storage(self.storage)

    def set_parent(self, parent):
        self.info.parent_object.set_value(0 if not parent else parent.get_uid())
        self.parent = parent

    def set_storage(self, storage):
        self.storage = storage
        if self.storage:
            self.info.storage.set_value(storage.get_uid())
        # TODO: recursion loop??
        for obj in self.objects:
            obj.set_storage(storage)

    def get_object(self, handle):
        if self.uid == handle:
            return self
        for obj in self.objects:
            res = obj.get_object(handle)
            if res is not None:
                return res
        return None

    def get_handles(self):
        handles = [self.uid]
        for obj in self.objects:
            handles.extend(obj.get_handles())
        return handles

    def set_data(self, data, adhere_size=False):
        if adhere_size:
            if len(data) > self.info.compressed_size.value:
                raise MtpProtocolException(ResponseCodes.STORE_FULL)
        if self.info and (data is not None):
            self.info.compressed_size.set_value(len(data))
        self.data = data

    def get_thumb(self, obj):
        raise MtpProtocolException(ResponseCodes.NO_THUMBNAIL_PRESENT)

    def format_matches(self, fmt):
        return (
            fmt == self.info.object_format.value or
            fmt == 0xffffffff or
            self.info.object_format.value == 0x00000000
        )

    def set_protection_status(self, status):
        if (status > 0xffff) or (status < 0):
            raise MtpProtocolException(ResponseCodes.INVALID_PARAMETER)
        self.info.protection.set_value(status)

    def delete_self(self, fmt):
        '''
        .. todo:: actual deletion ??
        '''
        if not self.format_matches(fmt):
            raise MtpProtocolException(ResponseCodes.SPECIFICATION_BY_FORMAT_UNSUPPORTED)
        if self.parent:
            self.parent.objects.remove(self)
        else:
            self.storage.objects.remove(self)

    def delete_internal(self, fmt):
        objects = self.objects[:]
        deleted_count = 0
        undeleted_count = 0
        for obj in objects:
            try:
                obj.delete(fmt)
                deleted_count += 1
            except MtpProtocolException:
                undeleted_count += 1
        if undeleted_count:
            if deleted_count:
                raise MtpProtocolException(ResponseCodes.OBJECT_WRITE_PROTECTED)
            else:
                raise MtpProtocolException(ResponseCodes.PARTIAL_DELETION)
        self.delete_self(fmt)

    def delete(self, fmt):
        if not self.storage.can_delete():
            raise MtpProtocolException(ResponseCodes.OBJECT_WRITE_PROTECTED)
        self.delete_internal(fmt)

    @classmethod
    def from_fs_recursive(cls, path):
        # create object for current path
        obj = MtpObject.from_file(path)
        if os.path.isdir(path):
            for filename in os.listdir(path):
                new_path = os.path.join(path, filename)
                new_obj = MtpObject.from_fs_recursive(new_path)
                obj.add_object(new_obj)
        return obj

    @classmethod
    def from_file(cls, path):
        # TODO: handle cases othe than regular file here ...
        if os.path.isfile(path):
            with open(path, 'rb') as f:
                data = f.read()
        else:
            data = b''
        filename = os.path.split(path)[-1]
        mtime = int(os.path.getmtime(path))
        ctime = int(os.path.getctime(path))
        info = MtpObjectInfo(
            storage=0,
            object_format=0,
            protection=0,
            compressed_size=0,
            thumb_format=0,
            thumb_compressed_size=0,
            thumb_pix_width=0,
            thumb_pix_height=0,
            image_pix_width=0,
            image_pix_height=0,
            image_bit_depth=0,
            parent_object=0,
            assoc_type=0,
            assoc_desc=0,
            seq_num=0,
            filename=filename,
            ctime=ctime,
            mtime=mtime,
            keywords=''
        )
        obj = MtpObject(
            data=data,
            info=info,
            properties=[],
        )
        obj.real_path = path
        return obj


class MtpObjectInfo(object):

    def __init__(
        self,
        storage, object_format, protection, compressed_size,
        thumb_format, thumb_compressed_size, thumb_pix_width, thumb_pix_height,
        image_pix_width, image_pix_height, image_bit_depth,
        parent_object, assoc_type, assoc_desc, seq_num,
        filename, ctime, mtime, keywords
    ):
        self.storage = UInt32(storage)
        self.object_format = UInt16(object_format)
        self.protection = UInt16(protection)
        self.compressed_size = UInt32(compressed_size)
        self.thumb_format = UInt16(thumb_format)
        self.thumb_compressed_size = UInt32(thumb_compressed_size)
        self.thumb_pix_width = UInt32(thumb_pix_width)
        self.thumb_pix_height = UInt32(thumb_pix_height)
        self.image_pix_width = UInt32(image_pix_width)
        self.image_pix_height = UInt32(image_pix_height)
        self.image_bit_depth = UInt32(image_bit_depth)
        self.parent_object = UInt32(parent_object)
        self.assoc_type = UInt16(assoc_type)
        self.assoc_desc = UInt32(assoc_desc)
        self.seq_num = UInt32(seq_num)
        self.filename = MStr(filename)
        self.ctime = MDateTime(ctime)
        self.mtime = MDateTime(mtime)
        self.keywords = MStr(keywords)

    def copy(self):
        return MtpObjectInfo(
            self.storage.value,
            self.object_format.value,
            self.protection.value,
            self.compressed_size.value,
            self.thumb_format.value,
            self.thumb_compressed_size.value,
            self.thumb_pix_width.value,
            self.thumb_pix_height.value,
            self.image_pix_width.value,
            self.image_pix_height.value,
            self.image_bit_depth.value,
            self.parent_object.value,
            self.assoc_type.value,
            self.assoc_desc.value,
            self.seq_num.value,
            self.filename.value,
            self.ctime.value,
            self.mtime.value,
            self.keywords.value,
        )

    def pack(self):
        res = b''
        res += self.storage.pack()
        res += self.object_format.pack()
        res += self.protection.pack()
        res += self.compressed_size.pack()
        res += self.thumb_format.pack()
        res += self.thumb_compressed_size.pack()
        res += self.thumb_pix_width.pack()
        res += self.thumb_pix_height.pack()
        res += self.image_pix_width.pack()
        res += self.image_pix_height.pack()
        res += self.image_bit_depth.pack()
        res += self.parent_object.pack()
        res += self.assoc_type.pack()
        # TODO (AssociationDesc)
        res += self.assoc_desc.pack()
        res += self.seq_num.pack()
        res += self.filename.pack()
        res += self.ctime.pack()
        res += self.mtime.pack()
        res += self.keywords.pack()
        return res

    @classmethod
    def from_buff(cls, buff):
        try:
            ui32 = UInt32()
            ui16 = UInt16()
            mstr = MStr()
            mdt = MDateTime()
            rest = buff
            (storage, rest) = ui32.unpack(rest)
            (object_format, rest) = ui16.unpack(rest)
            (protection, rest) = ui16.unpack(rest)
            (compressed_size, rest) = ui32.unpack(rest)
            (thumb_format, rest) = ui16.unpack(rest)
            (thumb_compressed_size, rest) = ui32.unpack(rest)
            (thumb_pix_width, rest) = ui32.unpack(rest)
            (thumb_pix_height, rest) = ui32.unpack(rest)
            (image_pix_width, rest) = ui32.unpack(rest)
            (image_pix_height, rest) = ui32.unpack(rest)
            (image_bit_depth, rest) = ui32.unpack(rest)
            (parent_object, rest) = ui32.unpack(rest)
            (assoc_type, rest) = ui16.unpack(rest)
            (assoc_desc, rest) = ui32.unpack(rest)
            (seq_num, rest) = ui32.unpack(rest)
            (filename, rest) = mstr.unpack(rest)
            (ctime, rest) = mdt.unpack(rest)
            (mtime, rest) = mdt.unpack(rest)
            (keywords, rest) = mstr.unpack(rest)
            return MtpObjectInfo(
                storage,
                object_format,
                protection,
                compressed_size,
                thumb_format,
                thumb_compressed_size,
                thumb_pix_width,
                thumb_pix_height,
                image_pix_width,
                image_pix_height,
                image_bit_depth,
                parent_object,
                assoc_type,
                assoc_desc,
                seq_num,
                filename,
                ctime,
                mtime,
                keywords,
            )
        except:
            import traceback
            traceback.print_exc()
            raise MtpProtocolException(ResponseCodes.INVALID_DATASET)
