import unittest
from mtpdevice.mtp_device import MtpDevice, MtpDeviceInfo
from mtpdevice.mtp_storage import MtpStorage, MtpStorageInfo
from mtpdevice.mtp_object import MtpObject
from mtpdevice.mtp_proto import ContainerTypes, OperationDataCodes, ResponseCodes
from mtpdevice.mtp_api import MtpApi
from struct import pack


class MtpApiTest(unittest.TestCase):
    '''
    Currently, all tests here are with buffers, as the API of MtpApi
    '''

    def setUp(self):
        super(MtpApiTest, self).setUp()
        self.object = MtpObject.from_fs_recursive('.')
        self.storage_info = MtpStorageInfo(
            st_type=0,
            fs_type=0,
            access=0,
            max_cap=150000,
            free_bytes=0,
            free_objs=0,
            desc='MyStorage',
            vol_id='Python MTP Device Stack',
        )
        self.storage = MtpStorage(self.storage_info)
        self.storage.add_object(self.object)
        self.dev_info = MtpDeviceInfo(
            std_version=0x0102,
            mtp_vendor_ext_id=0x03040506,
            mtp_version=0x0708,
            mtp_extensions='Some Extension',
            functional_mode=0x0000,
            operations_supported=[],
            events_supported=[],
            device_properties_supported=[],
            capture_formats=[],
            playback_formats=[],
            manufacturer='BinyaminSharet',
            model='Role',
            device_version='1.2.3',
            serial_number='0123456789abcdef',
        )
        self.dev = MtpDevice(self.dev_info)
        self.dev.add_storage(self.storage)
        self.api = MtpApi(self.dev)

    def testApiOpenSession(self):
        command = pack('<IHHII', 0x10, ContainerTypes.Command, OperationDataCodes.OpenSession, 1, 1)
        excepted_response = pack('<IHHI', 0xc, ContainerTypes.Response, ResponseCodes.OK, 1)
        resps = self.api.handle_payload(command)
        self.assertEqual(len(resps), 1)
        self.assertEqual(resps[0], excepted_response)

    def testApiGetDeviceInfo(self):
        command = pack('<IHHI', 0x0c, ContainerTypes.Command, OperationDataCodes.GetDeviceInfo, 1)
        excepted_response = pack('<IHHI', 0xc, ContainerTypes.Response, ResponseCodes.OK, 1)
        resps = self.api.handle_payload(command)
        self.assertEqual(len(resps), 2)
        self.assertEqual(resps[1], excepted_response)
