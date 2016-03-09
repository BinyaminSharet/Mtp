'''
The object's binary data, the ObjectInfo dataset,
Object Properties and Object References
'''
from mtp_base import MtpEntity, MtpEntityInfoInterface
from mtp_proto import MU32, MU16, MStr, MDateTime
import os


class MtpObject(MtpEntity):

    def __init__(self, data, info, properties, references):
        super(MtpObject, self).__init__(info)
        self.data = data
        self.properties = properties
        self.references = references
        self.real_path = None

    def set_storage(self, storage):
        self.info.storage = storage
        # TODO: recursion loop??
        for obj in self.references:
            obj.set_storage(storage)

    def add_reference(self, obj):
        self.references.append(obj)
        obj.set_storage(self.info.storage)

    @classmethod
    def from_fs_recursive(cls, path):
        # create object for current path
        obj = MtpObject.from_file(path)
        if os.path.isdir(path):
            for filename in os.listdir(path):
                new_path = os.path.join(path, filename)
                new_obj = MtpObject.from_fs_recursive(new_path)
                obj.add_reference(new_obj)
        return obj

    @classmethod
    def from_file(cls, path):
        # TODO: handle cases othe than regular file here ...
        if os.path.isfile(path):
            data = open(path, 'rb').read()
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
            references=[]
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
