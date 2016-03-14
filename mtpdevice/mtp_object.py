'''
The object's binary data, the ObjectInfo dataset,
Object Properties and Object References
'''
from __future__ import absolute_import
import os
from .mtp_data_types import UInt32, UInt16, UInt64, UInt128, MStr, MDateTime
from .mtp_base import MtpBaseObject
from .mtp_proto import ResponseCodes
from .mtp_exception import MtpProtocolException
from .mtp_property import MtpObjectProperty as ObjProp
from .mtp_property import MtpObjectPropertyDescriptions as PropDescs


class MtpObject(MtpBaseObject):

    props_descs = {
        PropDescs.StorageID.get_code(): PropDescs.StorageID,
        PropDescs.ObjectFormat.get_code(): PropDescs.ObjectFormat,
        PropDescs.ProtectionStatus.get_code(): PropDescs.ProtectionStatus,
        PropDescs.ObjectSize.get_code(): PropDescs.ObjectSize,
        PropDescs.AssociationType.get_code(): PropDescs.AssociationType,
        PropDescs.AssociationDesc.get_code(): PropDescs.AssociationDesc,
        PropDescs.ObjectFileName.get_code(): PropDescs.ObjectFileName,
        PropDescs.DateCreated.get_code(): PropDescs.DateCreated,
        PropDescs.DateModified.get_code(): PropDescs.DateModified,
        PropDescs.Keywords.get_code(): PropDescs.Keywords,
        PropDescs.ParentObject.get_code(): PropDescs.ParentObject,
        PropDescs.PersistantUniqueObjectIdentifier.get_code(): PropDescs.PersistantUniqueObjectIdentifier,
        PropDescs.Name.get_code(): PropDescs.Name,
    }

    def __init__(self, data, info):
        super(MtpObject, self).__init__()
        self.info = info
        self.set_data(data)
        self.real_path = None
        self.objects = []
        self.storage = None
        self.parent = None
        self.info.unique_id.value.set_value(self.get_uid())

    def copy(self):
        '''
        .. todo:: copy properties ...
        '''
        new_data = None if self.data is None else self.data[:]
        new_info = self.info.copy()
        new_obj = MtpObject(new_data, new_info)
        for obj in self.objects:
            new_obj.add_object(obj.copy())

    def get_info(self):
        return self.info.pack()

    def get_property(self, prop_code):
        if prop_code in self.info.props:
            return self.info.props[prop_code]
        raise MtpProtocolException(ResponseCodes.OBJECT_PROP_NOT_SUPPORTED)

    def get_objects(self):
        return self.objects[:]

    def add_object(self, obj):
        self.objects.append(obj)
        obj.set_parent(self)
        obj.set_storage(self.storage)

    def set_parent(self, parent):
        self.info.parent_object.value.set_value(0 if not parent else parent.get_uid())
        self.parent = parent

    def set_storage(self, storage):
        self.storage = storage
        if self.storage:
            self.info.storage.value.set_value(storage.get_uid())
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

    def get_handles(self, fmt=None):
        handles = []
        if self.format_matches(fmt):
            handles = [self.uid]
        for obj in self.objects:
            handles.extend(obj.get_handles())
        return handles

    def set_data(self, data, adhere_size=False):
        if adhere_size:
            if len(data) > self.info.compressed_size.value.value:
                raise MtpProtocolException(ResponseCodes.STORE_FULL)
        if self.info and (data is not None):
            self.info.compressed_size.value.set_value(len(data))
        self.data = data

    def get_thumb(self, obj):
        raise MtpProtocolException(ResponseCodes.NO_THUMBNAIL_PRESENT)

    def format_matches(self, fmt):
        return (
            not fmt or
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
    def get_obj_prop_desc(cls, obj_prop_code, obj_fmt_code):
        '''
        :return: ObjectPropertyDesc
        '''
        if obj_prop_code in MtpObject.props_descs:
            return MtpObject.props_descs[obj_prop_code]
        raise MtpProtocolException(ResponseCodes.OBJECT_PROP_NOT_SUPPORTED)

    @classmethod
    def get_supported_props(cls, obj_fmt_code):
        '''
        :return: array of object property codes
        '''
        return list(MtpObject.props_descs.keys())

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
        object_format = Formats.guess(path)
        info = MtpObjectInfo(
            storage=0,
            object_format=object_format,
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
        self.props = {}
        self.storage = ObjProp(PropDescs.StorageID, UInt32(storage))
        self.props[self.storage.get_code()] = self.storage
        self.object_format = ObjProp(PropDescs.ObjectFormat, UInt16(object_format))
        self.props[self.object_format.get_code()] = self.object_format
        self.protection = ObjProp(PropDescs.ProtectionStatus, UInt16(protection))
        self.props[self.protection.get_code()] = self.protection
        # need to cut out lower 32 bits, as in info it is only 32bit.
        self.compressed_size = ObjProp(PropDescs.ObjectSize, UInt64(compressed_size))
        self.props[self.compressed_size.get_code()] = self.compressed_size
        self.thumb_format = UInt16(thumb_format)
        self.thumb_compressed_size = UInt32(thumb_compressed_size)
        self.thumb_pix_width = UInt32(thumb_pix_width)
        self.thumb_pix_height = UInt32(thumb_pix_height)
        self.image_pix_width = UInt32(image_pix_width)
        self.image_pix_height = UInt32(image_pix_height)
        self.image_bit_depth = UInt32(image_bit_depth)
        self.parent_object = ObjProp(PropDescs.ParentObject, UInt32(parent_object))
        self.props[self.parent_object.get_code()] = self.parent_object
        self.assoc_type = ObjProp(PropDescs.AssociationType, UInt16(assoc_type))
        self.props[self.assoc_type.get_code()] = self.assoc_type
        self.assoc_desc = ObjProp(PropDescs.AssociationDesc, UInt32(assoc_desc))
        self.props[self.assoc_desc.get_code()] = self.assoc_desc
        self.seq_num = UInt32(seq_num)
        self.filename = ObjProp(PropDescs.ObjectFileName, MStr(filename))
        self.props[self.filename.get_code()] = self.filename
        self.ctime = ObjProp(PropDescs.DateCreated, MDateTime(ctime))
        self.props[self.ctime.get_code()] = self.ctime
        self.mtime = ObjProp(PropDescs.DateModified, MDateTime(mtime))
        self.props[self.mtime.get_code()] = self.mtime
        self.keywords = ObjProp(PropDescs.Keywords, MStr(keywords))
        self.props[self.keywords.get_code()] = self.keywords

        # The following should not be packed ....
        self.name = ObjProp(PropDescs.Name, MStr(filename))
        self.props[self.name.get_code()] = self.name
        self.unique_id = ObjProp(PropDescs.PersistantUniqueObjectIdentifier, UInt128(0))
        self.props[self.unique_id.get_code()] = self.unique_id

    def copy(self):
        return MtpObjectInfo(
            self.storage.value.value,
            self.object_format.value.value,
            self.protection.value.value,
            self.compressed_size.value.value,
            self.thumb_format.value.value,
            self.thumb_compressed_size.value.value,
            self.thumb_pix_width.value.value,
            self.thumb_pix_height.value.value,
            self.image_pix_width.value.value,
            self.image_pix_height.value.value,
            self.image_bit_depth.value.value,
            self.parent_object.value.value,
            self.assoc_type.value.value,
            self.assoc_desc.value.value,
            self.seq_num.value.value,
            self.filename.value.value,
            self.ctime.value.value,
            self.mtime.value.value,
            self.keywords.value.value,
        )

    def pack(self):
        res = b''
        res += self.storage.pack()
        res += self.object_format.pack()
        res += self.protection.pack()
        res += self.compressed_size.pack()
        res += self.thumb_format.pack()
        res += self.thumb_compressed_size.pack()[:4]
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


class Formats(object):
    # ancillary formats
    Undefined = 0x3000
    Association = 0x3001
    Script = 0x3002
    Executable = 0x3003
    Text = 0x3004
    HTML = 0x3005
    DPOF = 0x3006
    AIFF = 0x3007
    WAV = 0x3008
    MP3 = 0x3009
    AVI = 0x300A
    MPEG = 0x300B
    ASF = 0x300C
    QT = 0x300D  # guessing
    # image formats
    EXIF_JPEG = 0x3801
    TIFF_EP = 0x3802
    FlashPix = 0x3803
    BMP = 0x3804
    CIFF = 0x3805
    GIF = 0x3807
    JFIF = 0x3808
    PCD = 0x3809
    PICT = 0x380A
    PNG = 0x380B
    TIFF = 0x380D
    TIFF_IT = 0x380E
    JP2 = 0x380F
    JPX = 0x3810
    DNG = 0x3811
    # MTP extensions
    MediaCard = 0xb211
    MediaCardGroup = 0xb212
    Encounter = 0xb213
    EncounterBox = 0xb214
    M4A = 0xb215
    ZUNEUNDEFINED = 0xb217  # Unknown file type
    Firmware = 0xb802
    WindowsImageFormat = 0xb881
    UndefinedAudio = 0xb900
    WMA = 0xb901
    OGG = 0xb902
    AAC = 0xb903
    AudibleCodec = 0xb904
    FLAC = 0xb906
    SamsungPlaylist = 0xb909
    UndefinedVideo = 0xb980
    WMV = 0xb981
    MP4 = 0xb982
    MP2 = 0xb983
    _3GP = 0xb984
    UndefinedCollection = 0xba00
    AbstractMultimediaAlbum = 0xba01
    AbstractImageAlbum = 0xba02
    AbstractAudioAlbum = 0xba03
    AbstractVideoAlbum = 0xba04
    AbstractAudioVideoPlaylist = 0xba05
    AbstractContactGroup = 0xba06
    AbstractMessageFolder = 0xba07
    AbstractChapteredProduction = 0xba08
    AbstractAudioPlaylist = 0xba09
    AbstractVideoPlaylist = 0xba0a
    AbstractMediacast = 0xba0b
    WPLPlaylist = 0xba10
    M3UPlaylist = 0xba11
    MPLPlaylist = 0xba12
    ASXPlaylist = 0xba13
    PLSPlaylist = 0xba14
    UndefinedDocument = 0xba80
    AbstractDocument = 0xba81
    XMLDocument = 0xba82
    MSWordDocument = 0xba83
    MHTCompiledHTMLDocument = 0xba84
    MSExcelSpreadsheetXLS = 0xba85
    MSPowerpointPresentationPPT = 0xba86
    UndefinedMessage = 0xbb00
    AbstractMessage = 0xbb01
    UndefinedContact = 0xbb80
    AbstractContact = 0xbb81
    vCard2 = 0xbb82
    vCard3 = 0xbb83
    UndefinedCalendarItem = 0xbe00
    AbstractCalendarItem = 0xbe01
    vCalendar1 = 0xbe02
    vCalendar2 = 0xbe03
    UndefinedWindowsExecutable = 0xbe80
    MediaCast = 0xbe81
    Section = 0xbe82

    @classmethod
    def guess(cls, path):
        ext_format = {
            'mp3': Formats.MP3,
            'avi': Formats.AVI,
            'jpg': Formats.EXIF_JPEG,
            'jpeg': Formats.EXIF_JPEG,
            'png': Formats.PNG,
            'bmp': Formats.BMP,
            'wav': Formats.WAV,
            'm3u': Formats.M3UPlaylist,
            'html': Formats.HTML,
            'mht': Formats.MHTCompiledHTMLDocument
        }
        if os.path.isdir(path):
            return Formats.Association
        ext = path.split('.')[-1].lower()
        if ext in ext_format:
            return ext_format[ext]
        return Formats.Undefined
