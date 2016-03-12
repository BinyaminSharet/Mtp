from struct import pack, unpack
from binascii import unhexlify
from common import BaseTestCase
from mtpdevice.mtp_device import MtpDevice, MtpDeviceInfo
from mtpdevice.mtp_device_property import MtpDeviceProperty, MtpPropertyCode
from mtpdevice.mtp_storage import MtpStorage, MtpStorageInfo
from mtpdevice.mtp_object import MtpObject
from mtpdevice.mtp_proto import ContainerTypes, OperationDataCodes, ResponseCodes
from mtpdevice.mtp_api import MtpApi
from mtpdevice.mtp_data_types import UInt8


class MtpApiTest(BaseTestCase):
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
            capture_formats=[],
            playback_formats=[],
            manufacturer='BinyaminSharet',
            model='Role',
            device_version='1.2.3',
            serial_number='0123456789abcdef',
        )
        properties = [
            MtpDeviceProperty(MtpPropertyCode.DPC_BatteryLevel, 0, UInt8(50), UInt8(0))
        ]
        self.dev = MtpDevice(self.dev_info, properties)
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

    def testApiUnsupportedOperation(self):
        command = pack('<IHHI', 0xc, ContainerTypes.Command, 0, 1)
        excepted_response = pack('<IHHI', 0xc, ContainerTypes.Response, ResponseCodes.OPERATION_NOT_SUPPORTED, 1)
        resps = self.api.handle_payload(command)
        self.assertEqual(len(resps), 1)
        self.assertEqual(resps[0], excepted_response)

    def testApiSendObjectOperation(self):
        obj_data = b'1234'
        # open session
        self.testApiOpenSession()

        # send object info
        send_obj_info_cmd = pack('<IHHII', 0x10, ContainerTypes.Command, OperationDataCodes.SendObjectInfo, 1, self.storage.get_uid())
        send_obj_info_cmd_resp = self.api.handle_payload(send_obj_info_cmd)
        self.assertEqual(send_obj_info_cmd_resp, [])
        obj_info_dataset = unhexlify('0100010001380000040000000000000000000000000000000000000000000000000000000000060000000000000000000000000011770061006c006c00700061007000650072005f0031002e006a007000650067000000000000')
        send_obj_info_data = pack('<IHHI', len(obj_info_dataset) + 0xc, ContainerTypes.Data, OperationDataCodes.SendObjectInfo, 1) + obj_info_dataset
        send_obj_info_data_resp = self.api.handle_payload(send_obj_info_data)
        self.assertEqual(len(send_obj_info_data_resp), 1)
        response_status = unpack('<H', send_obj_info_data_resp[0][6:8])[0]
        self.assertEqual(response_status, ResponseCodes.OK)

        # send object
        send_obj_cmd = pack('<IHHI', 0xc, ContainerTypes.Command, OperationDataCodes.SendObject, 2)
        send_obj_cmd_resp = self.api.handle_payload(send_obj_cmd)
        self.assertEqual(send_obj_cmd_resp, [])
        send_obj_data = pack('<IHHI', len(obj_data) + 0xc, ContainerTypes.Data, OperationDataCodes.SendObject, 2) + obj_data
        send_obj_data_resp = self.api.handle_payload(send_obj_data)
        self.assertEqual(len(send_obj_data_resp), 1)
        response_status = unpack('<H', send_obj_info_data_resp[0][6:8])[0]
        self.assertEqual(response_status, ResponseCodes.OK)
        # read object info
        # read object ?

    def testApiLongSendObjectOperation(self):
        obj_data = b'1234'
        # open session
        self.testApiOpenSession()

        # send object info
        send_obj_info_cmd = pack('<IHHII', 0x10, ContainerTypes.Command, OperationDataCodes.SendObjectInfo, 1, self.storage.get_uid())
        send_obj_info_cmd_resp = self.api.handle_payload(send_obj_info_cmd)
        self.assertEqual(send_obj_info_cmd_resp, [])
        obj_info_dataset = unhexlify('0100010001380000040000000000000000000000000000000000000000000000000000000000060000000000000000000000000011770061006c006c00700061007000650072005f0031002e006a007000650067000000000000')
        send_obj_info_data = pack('<IHHI', len(obj_info_dataset) + 0xc, ContainerTypes.Data, OperationDataCodes.SendObjectInfo, 1) + obj_info_dataset
        send_obj_info_data_resp = self.api.handle_payload(send_obj_info_data)
        self.assertEqual(len(send_obj_info_data_resp), 1)
        response_status = unpack('<H', send_obj_info_data_resp[0][6:8])[0]
        self.assertEqual(response_status, ResponseCodes.OK)

        # send object
        send_obj_cmd = pack('<IHHI', 0xc, ContainerTypes.Command, OperationDataCodes.SendObject, 2)
        send_obj_cmd_resp = self.api.handle_payload(send_obj_cmd)
        self.assertEqual(send_obj_cmd_resp, [])

        send_obj_data = pack('<IHHI', len(obj_data) + 0xc, ContainerTypes.Data, OperationDataCodes.SendObject, 2) + obj_data[:2]
        send_obj_data_resp = self.api.handle_payload(send_obj_data)
        self.assertEqual(send_obj_data_resp, [])

        send_obj_data = obj_data[2:3]
        send_obj_data_resp = self.api.handle_payload(send_obj_data)
        self.assertEqual(send_obj_data_resp, [])

        send_obj_data = obj_data[3:4]
        send_obj_data_resp = self.api.handle_payload(send_obj_data)
        self.assertEqual(len(send_obj_data_resp), 1)

        response_status = unpack('<H', send_obj_info_data_resp[0][6:8])[0]
        self.assertEqual(response_status, ResponseCodes.OK)
        # read object info
        # read object ?
