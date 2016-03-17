from common import BaseTestCase
from mtpdevice.mtp_storage import MtpStorage, MtpStorageInfo
from mtpdevice.mtp_object import MtpObject, MtpObjectInfo, Formats
from mtpdevice.mtp_proto import OperationDataCodes, ResponseCodes, AccessCaps, ContainerTypes
from mtpdevice.mtp_property import MtpObjectPropertyCode
from mtpdevice.mtp_exception import MtpProtocolException
from struct import pack
from binascii import unhexlify, hexlify


class MtpObjectTests(BaseTestCase):

    def setUp(self):
        super(MtpObjectTests, self).setUp()
        self.default_filename = 'test_file'
        self.default_data = b'\x01\x02\x03\x04\x05\x06\x07\x08'
        self.default_format = Formats.MP3

    def get_default_storage(self):
        storage_info = MtpStorageInfo(
            st_type=0,
            fs_type=0,
            access=0,
            max_cap=150000000,
            free_bytes=0,
            free_objs=0,
            desc='150MB Storage',
            vol_id='Test Storage',
        )
        storage = MtpStorage(storage_info)
        return storage

    def get_default_info(self, **kwargs):
        kw = {
            'storage': 0,
            'object_format': self.default_format,
            'protection': 0,
            'compressed_size': 0,
            'thumb_format': 0,
            'thumb_compressed_size': 0,
            'thumb_pix_width': 0,
            'thumb_pix_height': 0,
            'image_pix_width': 0,
            'image_pix_height': 0,
            'image_bit_depth': 0,
            'parent_object': 0,
            'assoc_type': 0,
            'assoc_desc': 0,
            'seq_num': 0,
            'filename': self.default_filename,
            'ctime': 0,
            'mtime': 0,
            'keywords': ''
        }
        kw.update(kwargs)
        info = MtpObjectInfo(
            **kw
        )
        return info

    def testObjectData(self):
        uut = MtpObject(self.default_data, self.get_default_info())
        self.assertEqual(uut.data, self.default_data)

    def testObjectInfo(self):
        info = self.get_default_info()
        uut = MtpObject(self.default_data, info)
        self.assertEqual(uut.info, info)

    def testGetInfoReturnsPackedInfo(self):
        info = self.get_default_info()
        uut = MtpObject(self.default_data, info)
        self.assertEqual(uut.get_info(), info.pack())

    def testGetObjectsEmpty(self):
        uut = MtpObject(self.default_data, self.get_default_info())
        self.assertEqual(uut.get_objects(), [])

    def testGetObjectsWithMultipleChildes(self):
        others = [
            MtpObject(self.default_data, self.get_default_info()),
            MtpObject(self.default_data, self.get_default_info()),
            MtpObject(self.default_data, self.get_default_info())
        ]
        uut = MtpObject(self.default_data, self.get_default_info())
        for obj in others:
            uut.add_object(obj)
        objs = uut.get_objects()
        self.assertEqual(len(objs), len(set(objs)))
        self.assertEqual(len(objs), len(others))
        self.assertEqual(set(objs), set(others))

    def testGetObjectsMultipleLevels(self):
        others = [
            MtpObject(self.default_data, self.get_default_info()),
            MtpObject(self.default_data, self.get_default_info()),
            MtpObject(self.default_data, self.get_default_info())
        ]
        uut = MtpObject(self.default_data, self.get_default_info())
        cur = uut
        for obj in others:
            cur.add_object(obj)
            cur = obj
        objs = uut.get_objects()
        self.assertEqual(len(objs), len(set(objs)))
        self.assertEqual(len(objs), len(others))
        self.assertEqual(set(objs), set(others))

    def testGetObjectSelfAlone(self):
        uut = MtpObject(self.default_data, self.get_default_info())
        obj = uut.get_object(uut.get_uid())
        self.assertEqual(uut, obj)

    def testGetObjectSelfWithChilds(self):
        others = [
            MtpObject(self.default_data, self.get_default_info()),
            MtpObject(self.default_data, self.get_default_info()),
            MtpObject(self.default_data, self.get_default_info())
        ]
        uut = MtpObject(self.default_data, self.get_default_info())
        for obj in others:
            uut.add_object(obj)
        obj = uut.get_object(uut.get_uid())
        self.assertEqual(uut, obj)

    def testGetObjectDoesntExist(self):
        uut = MtpObject(self.default_data, self.get_default_info())
        obj = uut.get_object(uut.get_uid() + 1)
        self.assertIsNone(obj)

    def testGetObjectChildren(self):
        others = [
            MtpObject(self.default_data, self.get_default_info()),
            MtpObject(self.default_data, self.get_default_info()),
            MtpObject(self.default_data, self.get_default_info())
        ]
        uut = MtpObject(self.default_data, self.get_default_info())
        for obj in others:
            uut.add_object(obj)
        obj = uut.get_object(others[0].get_uid())
        self.assertEqual(obj, others[0])

    def testGetObjectMultipleLevels(self):
        others = [
            MtpObject(self.default_data, self.get_default_info()),
            MtpObject(self.default_data, self.get_default_info()),
            MtpObject(self.default_data, self.get_default_info())
        ]
        uut = MtpObject(self.default_data, self.get_default_info())
        cur = uut
        for obj in others:
            cur.add_object(obj)
            cur = obj
        obj = uut.get_object(others[-1].get_uid())
        self.assertEqual(obj, others[-1])

    def testAddObjectSetsParent(self):
        parent = MtpObject(self.default_data, self.get_default_info())
        uut = MtpObject(self.default_data, self.get_default_info())
        parent.add_object(uut)
        self.assertEqual(uut.parent, parent)

    def testAddObjectSetsStorageInChild(self):
        parent = MtpObject(self.default_data, self.get_default_info())
        uut = MtpObject(self.default_data, self.get_default_info())
        storage = self.get_default_storage()
        parent.set_storage(storage)
        parent.add_object(uut)
        self.assertEqual(uut.storage, storage)
        self.assertEqual(parent.storage, storage)

    def testSetStorage(self):
        '''
        .. todo:: should this be in storage tests? (TBD)
        '''
        uut = MtpObject(self.default_data, self.get_default_info())
        storage = self.get_default_storage()
        uut.set_storage(storage)
        self.assertEqual(uut.storage, storage)

    def testSetStorageIsRecursive(self):
        '''
        .. todo:: should this be in storage tests? (TBD)
        '''
        parent = MtpObject(self.default_data, self.get_default_info())
        storage = self.get_default_storage()
        uut = MtpObject(self.default_data, self.get_default_info())
        parent.add_object(uut)
        parent.set_storage(storage)
        self.assertEqual(uut.storage, storage)
        self.assertEqual(parent.storage, storage)

    def testFormatMatchsMatch(self):
        uut = MtpObject(self.default_data, self.get_default_info())
        self.assertTrue(uut.format_matches(self.default_format))

    def testFormatMatchsNone(self):
        uut = MtpObject(self.default_data, self.get_default_info())
        self.assertTrue(uut.format_matches(None))

    def testFormatMatchsWildcard(self):
        uut = MtpObject(self.default_data, self.get_default_info())
        self.assertTrue(uut.format_matches(0xffffffff))

    def testGetPropertyDefaults(self):
        uut = MtpObject(self.default_data, self.get_default_info())
        prop = uut.get_property(MtpObjectPropertyCode.ObjectFormat)
        self.assertIsNotNone(prop)
        self.assertEqual(prop.value.value, self.default_format)

    def testGetPropertyExceptionIfNotExist(self):
        uut = MtpObject(self.default_data, self.get_default_info())
        with self.assertRaises(MtpProtocolException) as cm:
            uut.get_property(MtpObjectPropertyCode.StorageID - 1)
        self.assertEqual(cm.exception.response, ResponseCodes.OBJECT_PROP_NOT_SUPPORTED)

    # copy
    # set_protection_status
    # delete_self
    # delete
