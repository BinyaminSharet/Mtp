'''
The object's binary data, the ObjectInfo dataset,
Object Properties and Object References
'''
from __future__ import absolute_import
import os
from struct import unpack
from .mtp_base import MtpObjectContainer, MtpEntityInfoInterface
from .mtp_proto import MU32, MU16, MStr, MStr_unpack, MDateTime, MDateTime_unpack, ResponseCodes
from .mtp_exception import MtpProtocolException


class MtpObject(MtpObjectContainer):

    def __init__(self, data, info, properties):
        super(MtpObject, self).__init__(info)
        self.data = data
        self.properties = properties
        self.real_path = None

    def set_storage(self, storage):
        self.info.storage = storage
        # TODO: recursion loop??
        for obj in self.objects:
            obj.set_storage(storage)

    def get_thumb(self, obj):
        raise MtpProtocolException(ResponseCodes.NO_THUMBNAIL_PRESENT)

    def format_matches(self, fmt):
        return (
            fmt == self.info.object_format or
            fmt == 0xffffffff or
            self.info.object_format == 0x00000000
        )

    def delete_self(self, fmt):
        '''
        .. todo:: actual deletion ??
        '''
        if not self.format_matches(fmt):
            raise MtpProtocolException(ResponseCodes.SPECIFICATION_BY_FORMAT_UNSUPPORTED)
        if self.parent:
            self.parent.objects.remove(self)
        else:
            self.info.storage.objects.remove(self)

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
        if not self.info.storage.can_delete():
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
            storage=None,
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
            parent_object=None,
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


class MtpObjectInfo(MtpEntityInfoInterface):

    def __init__(
        self,
        storage, object_format, protection, compressed_size,
        thumb_format, thumb_compressed_size, thumb_pix_width, thumb_pix_height,
        image_pix_width, image_pix_height, image_bit_depth,
        parent_object, assoc_type, assoc_desc, seq_num,
        filename, ctime, mtime, keywords
    ):
        self.storage = storage
        self.object_format = object_format
        self.protection = protection
        self.compressed_size = compressed_size
        self.thumb_format = thumb_format
        self.thumb_compressed_size = thumb_compressed_size
        self.thumb_pix_width = thumb_pix_width
        self.thumb_pix_height = thumb_pix_height
        self.image_pix_width = image_pix_width
        self.image_pix_height = image_pix_height
        self.image_bit_depth = image_bit_depth
        self.parent_object = parent_object
        self.assoc_type = assoc_type
        self.assoc_desc = assoc_desc
        self.seq_num = seq_num
        self.filename = filename
        self.ctime = ctime
        self.mtime = mtime
        self.keywords = keywords

    def pack(self):
        return (
            MU32(self.storage.get_uid()) +
            MU16(self.object_format) +
            MU16(self.protection) +
            MU32(self.compressed_size) +
            MU16(self.thumb_format) +
            MU32(self.thumb_compressed_size) +
            MU32(self.thumb_pix_width) +
            MU32(self.thumb_pix_height) +
            MU32(self.image_pix_width) +
            MU32(self.image_pix_height) +
            MU32(self.image_bit_depth) +
            MU32(0 if not self.parent_object else self.parent_object.get_uid()) +
            MU16(self.assoc_type) +
            # TODO (AssociationDesc)
            MU32(self.assoc_desc) +
            MU32(self.seq_num) +
            MStr(self.filename) +
            MDateTime(self.ctime) +
            MDateTime(self.mtime) +
            MStr(self.keywords)
        )

    @classmethod
    def from_buff(cls, buff):
        try:
            (
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
            ) = unpack('<IHHIHIIIIIIIHII', buff[:52])
            rest = buff[52:]
            (filename, rest) = MStr_unpack(rest)
            (ctime, rest) = MDateTime_unpack(rest)
            (mtime, rest) = MDateTime_unpack(rest)
            (keywords, rest) = MStr_unpack(rest)
        except:
            raise MtpProtocolException(ResponseCodes.INVALID_DATASET)