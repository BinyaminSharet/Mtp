from common import BaseTestCase
from mtpdevice.mtp_device import MtpDevice, MtpDeviceInfo
from mtpdevice.mtp_storage import MtpStorage, MtpStorageInfo
from mtpdevice.mtp_object import MtpObject
from mtpdevice.mtp_proto import OperationDataCodes, ResponseCodes, AccessCaps, ContainerTypes
from mtpdevice.mtp_msg import MtpParametersMessage, response_from_command, MtpMessage
from mtpdevice.mtp_device_property import MtpDeviceProperty
from mtpdevice.mtp_data_types import UInt8
from struct import pack
from binascii import unhexlify


def command_message(tid, code, params=None):
    params = params if params else []
    length = 0xc + len(params) * 4
    data = b''
    for p in params:
        data += pack('<I', p)
    return MtpParametersMessage(length, ContainerTypes.Command, code, tid, data)


def data_message(tid, code, data):
    length = 0xc + len(data)
    return MtpMessage(length, ContainerTypes.Data, code, tid, data)


def response_message(cmd):
    return response_from_command(cmd, ResponseCodes.OK)


class MtpDeviceTests(BaseTestCase):

    def setUp(self):
        super(MtpDeviceTests, self).setUp()
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
        self.dev = MtpDevice(self.dev_info)
        self.dev.add_storage(self.storage)
        self.tid = 1

    def new_transaction(self):
        self.tid += 1
        return self.tid

    def successful_open_session(self):
        session_id = 1
        request = command_message(self.new_transaction(), OperationDataCodes.OpenSession, [session_id])
        response = response_message(request)
        self.dev.OpenSession(request, response, None)
        self.assertEqual(response.code, ResponseCodes.OK)
        self.assertEqual(self.dev.session_id, session_id)

    def test_OpenSessionWithSessionId(self):
        self.successful_open_session()

    def test_OpenSessionWithoutParams(self):
        request = command_message(self.new_transaction(), OperationDataCodes.OpenSession, [])
        response = response_message(request)
        self.dev.OpenSession(request, response, None)
        self.assertEqual(response.code, ResponseCodes.PARAMETER_NOT_SUPPORTED)
        self.assertIsNone(self.dev.session_id)

    def test_OpenSessionTwice(self):
        self.successful_open_session()

        request = command_message(self.new_transaction(), OperationDataCodes.OpenSession, [2])
        response = response_message(request)
        self.dev.OpenSession(request, response, None)
        self.assertEqual(response.code, ResponseCodes.SESSION_ALREADY_OPEN)
        self.assertEqual(self.dev.session_id, 1)

    def test_CloseSessionAfterOpenSession(self):
        self.successful_open_session()

        request = command_message(self.new_transaction(), OperationDataCodes.CloseSession, [])
        response = response_message(request)
        self.dev.CloseSession(request, response, None)
        self.assertEqual(response.code, ResponseCodes.OK)
        self.assertIsNone(self.dev.session_id)

    def test_CloseSessionBeforeOpenSession(self):
        request = command_message(self.new_transaction(), OperationDataCodes.CloseSession, [])
        response = response_message(request)
        self.dev.CloseSession(request, response, None)
        self.assertEqual(response.code, ResponseCodes.SESSION_NOT_OPEN)

    def test_CloseSessionAfterCloseSession(self):
        self.successful_open_session()

        request = command_message(self.new_transaction(), OperationDataCodes.CloseSession, [])
        response = response_message(request)
        self.dev.CloseSession(request, response, None)
        self.assertEqual(response.code, ResponseCodes.OK)
        self.assertIsNone(self.dev.session_id)

        request = command_message(self.new_transaction(), OperationDataCodes.CloseSession, [])
        response = response_message(request)
        self.dev.CloseSession(request, response, None)
        self.assertEqual(response.code, ResponseCodes.SESSION_NOT_OPEN)

    def test_GetDeviceInfoBeforeOpenSession(self):
        request = command_message(self.new_transaction(), OperationDataCodes.GetDeviceInfo, [])
        response = response_message(request)
        self.dev.GetDeviceInfo(request, response, None)
        self.assertEqual(response.code, ResponseCodes.OK)

    def test_GetDeviceInfoAfterOpenSession(self):
        self.successful_open_session()

        request = command_message(self.new_transaction(), OperationDataCodes.GetDeviceInfo, [])
        response = response_message(request)
        self.dev.GetDeviceInfo(request, response, None)
        self.assertEqual(response.code, ResponseCodes.OK)

    def test_GetStorageIDsAfterOpenSession(self):
        self.successful_open_session()

        request = command_message(self.new_transaction(), OperationDataCodes.GetStorageIDs, [])
        response = response_message(request)
        self.dev.GetStorageIDs(request, response, None)
        self.assertEqual(response.code, ResponseCodes.OK)

    def test_GetStorageIDsBeforeOpenSession(self):
        request = command_message(self.new_transaction(), OperationDataCodes.GetStorageIDs, [])
        response = response_message(request)
        self.dev.GetStorageIDs(request, response, None)
        self.assertEqual(response.code, ResponseCodes.SESSION_NOT_OPEN)

    def test_GetStorageInfoAfterOpenSession(self):
        self.successful_open_session()

        request = command_message(self.new_transaction(), OperationDataCodes.GetStorageInfo, [self.storage.get_uid()])
        response = response_message(request)
        self.dev.GetStorageInfo(request, response, None)
        self.assertEqual(response.code, ResponseCodes.OK)

    def test_GetStorageInfoBeforeOpenSession(self):
        request = command_message(self.new_transaction(), OperationDataCodes.GetStorageInfo, [self.storage.get_uid()])
        response = response_message(request)
        self.dev.GetStorageInfo(request, response, None)
        self.assertEqual(response.code, ResponseCodes.SESSION_NOT_OPEN)

    def test_GetStorageInfoWithoutStorageId(self):
        self.successful_open_session()

        request = command_message(self.new_transaction(), OperationDataCodes.GetStorageInfo, [])
        response = response_message(request)
        self.dev.GetStorageInfo(request, response, None)
        self.assertEqual(response.code, ResponseCodes.PARAMETER_NOT_SUPPORTED)

    def test_GetStorageInfoWithInvalidStorageId(self):
        self.successful_open_session()

        request = command_message(self.new_transaction(), OperationDataCodes.GetStorageInfo, [self.storage.get_uid() + 1])
        response = response_message(request)
        self.dev.GetStorageInfo(request, response, None)
        self.assertEqual(response.code, ResponseCodes.INVALID_STORAGE_ID)

    def test_GetNumObjectsBeforeOpenSession(self):
        request = command_message(self.new_transaction(), OperationDataCodes.GetNumObjects, [self.storage.get_uid()])
        response = response_message(request)
        self.dev.GetNumObjects(request, response, None)
        self.assertEqual(response.code, ResponseCodes.SESSION_NOT_OPEN)

    def test_GetNumObjectsAfterOpenSession(self):
        self.successful_open_session()

        request = command_message(self.new_transaction(), OperationDataCodes.GetNumObjects, [self.storage.get_uid()])
        response = response_message(request)
        self.dev.GetNumObjects(request, response, None)
        self.assertEqual(response.code, ResponseCodes.OK)

    def test_GetNumObjectsSameTwoCalls(self):
        self.successful_open_session()

        request = command_message(self.new_transaction(), OperationDataCodes.GetNumObjects, [self.storage.get_uid()])
        response = response_message(request)
        data1 = self.dev.GetNumObjects(request, response, None)
        self.assertEqual(response.code, ResponseCodes.OK)

        request = command_message(self.new_transaction(), OperationDataCodes.GetNumObjects, [self.storage.get_uid()])
        response = response_message(request)
        data2 = self.dev.GetNumObjects(request, response, None)
        self.assertEqual(response.code, ResponseCodes.OK)

        self.assertEqual(data1[-4:], data2[-4:])

    def test_GetNumObjectsWithoutStorageId(self):
        self.successful_open_session()

        request = command_message(self.new_transaction(), OperationDataCodes.GetNumObjects, [])
        response = response_message(request)
        self.dev.GetNumObjects(request, response, None)
        self.assertEqual(response.code, ResponseCodes.PARAMETER_NOT_SUPPORTED)

    def test_GetNumObjectsWithInvalidStorageId(self):
        self.successful_open_session()

        request = command_message(self.new_transaction(), OperationDataCodes.GetNumObjects, [self.storage.get_uid() + 1])
        response = response_message(request)
        self.dev.GetNumObjects(request, response, None)
        self.assertEqual(response.code, ResponseCodes.INVALID_STORAGE_ID)

    def test_GetObjectHandlesBeforeOpenSession(self):
        request = command_message(self.new_transaction(), OperationDataCodes.GetObjectHandles, [self.storage.get_uid()])
        response = response_message(request)
        self.dev.GetObjectHandles(request, response, None)
        self.assertEqual(response.code, ResponseCodes.SESSION_NOT_OPEN)

    def test_GetObjectHandlesAfterOpenSession(self):
        self.successful_open_session()

        request = command_message(self.new_transaction(), OperationDataCodes.GetObjectHandles, [self.storage.get_uid()])
        response = response_message(request)
        self.dev.GetObjectHandles(request, response, None)
        self.assertEqual(response.code, ResponseCodes.OK)

    def test_GetObjectHandlesWildcardStorageIdAfterOpenSession(self):
        self.successful_open_session()

        request = command_message(self.new_transaction(), OperationDataCodes.GetObjectHandles, [0xffffffff])
        response = response_message(request)
        self.dev.GetObjectHandles(request, response, None)
        self.assertEqual(response.code, ResponseCodes.OK)

    def test_GetObjectHandlesWithoutStorageId(self):
        self.successful_open_session()

        request = command_message(self.new_transaction(), OperationDataCodes.GetObjectHandles, [])
        response = response_message(request)
        self.dev.GetObjectHandles(request, response, None)
        self.assertEqual(response.code, ResponseCodes.PARAMETER_NOT_SUPPORTED)

    def test_GetObjectHandlesWithInvalidStorageId(self):
        self.successful_open_session()

        request = command_message(self.new_transaction(), OperationDataCodes.GetObjectHandles, [self.storage.get_uid() + 1])
        response = response_message(request)
        self.dev.GetObjectHandles(request, response, None)
        self.assertEqual(response.code, ResponseCodes.INVALID_STORAGE_ID)

    def test_GetObjectInfoBeforeOpenSession(self):
        request = command_message(self.new_transaction(), OperationDataCodes.GetObjectInfo, [self.storage.get_uid()])
        response = response_message(request)
        self.dev.GetObjectInfo(request, response, None)
        self.assertEqual(response.code, ResponseCodes.SESSION_NOT_OPEN)

    def test_GetObjectInfoAfterOpenSession(self):
        self.successful_open_session()

        request = command_message(self.new_transaction(), OperationDataCodes.GetObjectInfo, [self.object.get_uid()])
        response = response_message(request)
        self.dev.GetObjectInfo(request, response, None)
        self.assertEqual(response.code, ResponseCodes.OK)

    def test_GetObjectInfoWithoutObjectHandle(self):
        self.successful_open_session()

        request = command_message(self.new_transaction(), OperationDataCodes.GetObjectInfo, [])
        response = response_message(request)
        self.dev.GetObjectInfo(request, response, None)
        self.assertEqual(response.code, ResponseCodes.PARAMETER_NOT_SUPPORTED)

    def test_GetObjectInfoWithInvalidObjectHandle(self):
        self.successful_open_session()

        request = command_message(self.new_transaction(), OperationDataCodes.GetObjectInfo, [0xfffffffe])
        response = response_message(request)
        self.dev.GetObjectInfo(request, response, None)
        self.assertEqual(response.code, ResponseCodes.INVALID_OBJECT_HANDLE)

    def test_GetObjectBeforeOpenSession(self):
        request = command_message(self.new_transaction(), OperationDataCodes.GetObject, [self.storage.get_uid()])
        response = response_message(request)
        self.dev.GetObject(request, response, None)
        self.assertEqual(response.code, ResponseCodes.SESSION_NOT_OPEN)

    def test_GetObjectAfterOpenSession(self):
        self.successful_open_session()

        request = command_message(self.new_transaction(), OperationDataCodes.GetObject, [self.object.get_uid()])
        response = response_message(request)
        self.dev.GetObject(request, response, None)
        self.assertEqual(response.code, ResponseCodes.OK)

    def test_GetObjectWithoutObjectHandle(self):
        self.successful_open_session()

        request = command_message(self.new_transaction(), OperationDataCodes.GetObject, [])
        response = response_message(request)
        self.dev.GetObject(request, response, None)
        self.assertEqual(response.code, ResponseCodes.PARAMETER_NOT_SUPPORTED)

    def test_GetObjectWithInvalidObjectHandle(self):
        self.successful_open_session()

        request = command_message(self.new_transaction(), OperationDataCodes.GetObject, [0xfffffffe])
        response = response_message(request)
        self.dev.GetObject(request, response, None)
        self.assertEqual(response.code, ResponseCodes.INVALID_OBJECT_HANDLE)

    def test_DeleteObjectBeforeOpenSession(self):
        request = command_message(self.new_transaction(), OperationDataCodes.DeleteObject, [self.storage.get_uid()])
        response = response_message(request)
        self.dev.DeleteObject(request, response, None)
        self.assertEqual(response.code, ResponseCodes.SESSION_NOT_OPEN)

    def test_DeleteObjectAfterOpenSession(self):
        self.successful_open_session()

        request = command_message(self.new_transaction(), OperationDataCodes.DeleteObject, [self.object.get_uid()])
        response = response_message(request)
        self.dev.DeleteObject(request, response, None)
        self.assertEqual(response.code, ResponseCodes.OK)

    def test_DeleteObjectWildcardStorageIdAfterOpenSession(self):
        self.successful_open_session()

        request = command_message(self.new_transaction(), OperationDataCodes.DeleteObject, [0xffffffff])
        response = response_message(request)
        self.dev.DeleteObject(request, response, None)
        self.assertEqual(response.code, ResponseCodes.OK)

    def test_DeleteObjectInReadOnlyStorage(self):
        self.successful_open_session()

        self.storage.info.access.set_value(AccessCaps.READ_ONLY_WITHOUT_DELETE)
        request = command_message(self.new_transaction(), OperationDataCodes.DeleteObject, [self.object.get_uid()])
        response = response_message(request)
        self.dev.DeleteObject(request, response, None)
        self.assertEqual(response.code, ResponseCodes.OBJECT_WRITE_PROTECTED)

    def test_DeleteObjectWithoutObjectHandle(self):
        self.successful_open_session()

        request = command_message(self.new_transaction(), OperationDataCodes.DeleteObject, [])
        response = response_message(request)
        self.dev.DeleteObject(request, response, None)
        self.assertEqual(response.code, ResponseCodes.PARAMETER_NOT_SUPPORTED)

    def test_DeleteObjectWithInvalidObjectHandle(self):
        self.successful_open_session()

        request = command_message(self.new_transaction(), OperationDataCodes.DeleteObject, [0xfffffffe])
        response = response_message(request)
        self.dev.DeleteObject(request, response, None)
        self.assertEqual(response.code, ResponseCodes.INVALID_OBJECT_HANDLE)

    def test_DeleteObjectRemovesTheObject(self):
        self.successful_open_session()

        request = command_message(self.new_transaction(), OperationDataCodes.GetNumObjects, [self.storage.get_uid()])
        response = response_message(request)
        data1 = self.dev.GetNumObjects(request, response, None)
        self.assertEqual(response.code, ResponseCodes.OK)

        request = command_message(self.new_transaction(), OperationDataCodes.DeleteObject, [self.object.objects[0].get_uid()])
        response = response_message(request)
        self.dev.DeleteObject(request, response, None)
        self.assertEqual(response.code, ResponseCodes.OK)

        request = command_message(self.new_transaction(), OperationDataCodes.GetNumObjects, [self.storage.get_uid()])
        response = response_message(request)
        data2 = self.dev.GetNumObjects(request, response, None)
        self.assertEqual(response.code, ResponseCodes.OK)

        self.assertNotEqual(data1, data2)

    def test_ResetDeviceBeforeOpenSession(self):
        request = command_message(self.new_transaction(), OperationDataCodes.ResetDevice, [])
        response = response_message(request)
        self.dev.ResetDevice(request, response, None)
        self.assertEqual(response.code, ResponseCodes.SESSION_NOT_OPEN)

    def test_ResetDeviceAfterOpenSession(self):
        self.successful_open_session()

        request = command_message(self.new_transaction(), OperationDataCodes.ResetDevice, [])
        response = response_message(request)
        self.dev.ResetDevice(request, response, None)
        self.assertEqual(response.code, ResponseCodes.OK)

    def test_OpenSessionAfterResetDevice(self):
        self.successful_open_session()

        request = command_message(self.new_transaction(), OperationDataCodes.ResetDevice, [])
        response = response_message(request)
        self.dev.ResetDevice(request, response, None)
        self.assertEqual(response.code, ResponseCodes.OK)
        self.test_OpenSessionWithSessionId()

    def test_FormatStoreBeforeOpenSession(self):
        request = command_message(self.new_transaction(), OperationDataCodes.FormatStore, [self.storage.get_uid()])
        response = response_message(request)
        self.dev.FormatStore(request, response, None)
        self.assertEqual(response.code, ResponseCodes.SESSION_NOT_OPEN)

    def test_FormatStoreInvalidStorageId(self):
        self.successful_open_session()

        request = command_message(self.new_transaction(), OperationDataCodes.FormatStore, [self.storage.get_uid() + 1])
        response = response_message(request)
        self.dev.FormatStore(request, response, None)
        self.assertEqual(response.code, ResponseCodes.INVALID_STORAGE_ID)

    def test_FormatStoreNoStorageId(self):
        self.successful_open_session()

        request = command_message(self.new_transaction(), OperationDataCodes.FormatStore, [])
        response = response_message(request)
        self.dev.FormatStore(request, response, None)
        self.assertEqual(response.code, ResponseCodes.PARAMETER_NOT_SUPPORTED)

    def test_FormatStorageNotSupported(self):
        self.successful_open_session()
        request = command_message(self.new_transaction(), OperationDataCodes.FormatStore, [self.storage.get_uid()])
        response = response_message(request)
        self.dev.FormatStore(request, response, None)
        self.assertEqual(response.code, ResponseCodes.PARAMETER_NOT_SUPPORTED)

    def test_SendObjectInfoBeforeOpenSession(self):
        request = command_message(self.new_transaction(), OperationDataCodes.SendObjectInfo, [self.storage.get_uid()])
        response = response_message(request)
        obj_info_dataset = unhexlify('0100010001380000040000000000000000000000000000000000000000000000000000000000060000000000000000000000000011770061006c006c00700061007000650072005f0031002e006a007000650067000000000000')
        data = data_message(request.tid, request.code, obj_info_dataset)
        self.dev.SendObjectInfo(request, response, data)
        self.assertEqual(response.code, ResponseCodes.SESSION_NOT_OPEN)

    def set_default_device_properties(self):
        self.ro_prop = MtpDeviceProperty(1, 0, UInt8(5), UInt8(0))
        self.rw_prop = MtpDeviceProperty(2, 1, UInt8(5), UInt8(0))
        self.dev.add_property(self.ro_prop)
        self.dev.add_property(self.rw_prop)

    def test_GetDevicePropDescBeforeOpenSession(self):
        self.set_default_device_properties()
        request = command_message(self.new_transaction(), OperationDataCodes.GetDevicePropDesc, [1])
        response = response_message(request)
        self.dev.GetDevicePropDesc(request, response, None)
        self.assertEqual(response.code, ResponseCodes.SESSION_NOT_OPEN)

    def test_GetDevicePropDescAfterOpenSession(self):
        self.set_default_device_properties()
        self.successful_open_session()
        request = command_message(self.new_transaction(), OperationDataCodes.GetDevicePropDesc, [self.ro_prop.code.value])
        response = response_message(request)
        data = self.dev.GetDevicePropDesc(request, response, None)
        self.assertEqual(response.code, ResponseCodes.OK)
        self.assertEqual(data[12:], self.ro_prop.get_desc())

    def test_GetDevicePropDescInvalidPropCode(self):
        self.set_default_device_properties()
        self.successful_open_session()
        request = command_message(self.new_transaction(), OperationDataCodes.GetDevicePropDesc, [5])
        response = response_message(request)
        self.dev.GetDevicePropDesc(request, response, None)
        self.assertEqual(response.code, ResponseCodes.DEVICE_PROP_NOT_SUPPORTED)

    def test_GetDevicePropDescNoPropCode(self):
        self.set_default_device_properties()
        self.successful_open_session()
        request = command_message(self.new_transaction(), OperationDataCodes.GetDevicePropDesc, [])
        response = response_message(request)
        self.dev.GetDevicePropDesc(request, response, None)
        self.assertEqual(response.code, ResponseCodes.PARAMETER_NOT_SUPPORTED)

    def test_GetDevicePropValueBeforeOpenSession(self):
        self.set_default_device_properties()
        request = command_message(self.new_transaction(), OperationDataCodes.GetDevicePropValue, [1])
        response = response_message(request)
        self.dev.GetDevicePropValue(request, response, None)
        self.assertEqual(response.code, ResponseCodes.SESSION_NOT_OPEN)

    def test_GetDevicePropValueAfterOpenSession(self):
        self.set_default_device_properties()
        self.successful_open_session()
        request = command_message(self.new_transaction(), OperationDataCodes.GetDevicePropValue, [self.ro_prop.code.value])
        response = response_message(request)
        data = self.dev.GetDevicePropValue(request, response, None)
        self.assertEqual(response.code, ResponseCodes.OK)
        self.assertEqual(data[12:], self.ro_prop.get_value())

    def test_GetDevicePropValueInvalidPropCode(self):
        self.set_default_device_properties()
        self.successful_open_session()
        request = command_message(self.new_transaction(), OperationDataCodes.GetDevicePropValue, [5])
        response = response_message(request)
        self.dev.GetDevicePropValue(request, response, None)
        self.assertEqual(response.code, ResponseCodes.DEVICE_PROP_NOT_SUPPORTED)

    def test_GetDevicePropValueNoPropCode(self):
        self.set_default_device_properties()
        self.successful_open_session()
        request = command_message(self.new_transaction(), OperationDataCodes.GetDevicePropValue, [])
        response = response_message(request)
        self.dev.GetDevicePropValue(request, response, None)
        self.assertEqual(response.code, ResponseCodes.PARAMETER_NOT_SUPPORTED)

    def test_SetDevicePropValueBeforeOpenSession(self):
        self.set_default_device_properties()
        request = command_message(self.new_transaction(), OperationDataCodes.SetDevicePropValue, [self.rw_prop.code.value])
        response = response_message(request)
        ir_data = data_message(request.tid, request.code, unhexlify('28'))
        self.dev.SetDevicePropValue(request, response, ir_data)
        self.assertEqual(response.code, ResponseCodes.SESSION_NOT_OPEN)

    def test_SetDevicePropValueAfterOpenSession(self):
        self.set_default_device_properties()
        self.successful_open_session()
        request = command_message(self.new_transaction(), OperationDataCodes.SetDevicePropValue, [self.rw_prop.code.value])
        response = response_message(request)
        ir_data = data_message(request.tid, request.code, unhexlify('28'))
        self.dev.SetDevicePropValue(request, response, ir_data)
        self.assertEqual(response.code, ResponseCodes.OK)
        self.assertEqual(ir_data.data, self.rw_prop.get_value())

    def test_SetDevicePropValueInvalidPropCode(self):
        self.set_default_device_properties()
        self.successful_open_session()
        request = command_message(self.new_transaction(), OperationDataCodes.SetDevicePropValue, [5])
        response = response_message(request)
        ir_data = data_message(request.tid, request.code, unhexlify('28'))
        self.dev.SetDevicePropValue(request, response, ir_data)
        self.assertEqual(response.code, ResponseCodes.DEVICE_PROP_NOT_SUPPORTED)

    def test_SetDevicePropValueNoPropCode(self):
        self.set_default_device_properties()
        self.successful_open_session()
        request = command_message(self.new_transaction(), OperationDataCodes.SetDevicePropValue, [])
        response = response_message(request)
        ir_data = data_message(request.tid, request.code, unhexlify('28'))
        self.dev.SetDevicePropValue(request, response, ir_data)
        self.assertEqual(response.code, ResponseCodes.PARAMETER_NOT_SUPPORTED)

    def test_SetDevicePropValueReadOnly(self):
        self.set_default_device_properties()
        self.successful_open_session()
        request = command_message(self.new_transaction(), OperationDataCodes.SetDevicePropValue, [self.ro_prop.code.value])
        response = response_message(request)
        ir_data = data_message(request.tid, request.code, unhexlify('28'))
        self.dev.SetDevicePropValue(request, response, ir_data)
        self.assertEqual(response.code, ResponseCodes.ACCESS_DENIED)

    def test_ResetDevicePropValueBeforeOpenSession(self):
        self.set_default_device_properties()
        request = command_message(self.new_transaction(), OperationDataCodes.ResetDevicePropValue, [self.rw_prop.code.value])
        response = response_message(request)
        self.dev.ResetDevicePropValue(request, response, None)
        self.assertEqual(response.code, ResponseCodes.SESSION_NOT_OPEN)

    def test_ResetDevicePropValueAfterOpenSession(self):
        self.set_default_device_properties()
        self.successful_open_session()
        request = command_message(self.new_transaction(), OperationDataCodes.ResetDevicePropValue, [self.rw_prop.code.value])
        response = response_message(request)
        self.dev.ResetDevicePropValue(request, response, None)
        self.assertEqual(response.code, ResponseCodes.OK)
        self.assertEqual(self.rw_prop.get_value(), self.rw_prop.default_value.pack())

    def test_ResetDevicePropValueInvalidPropCode(self):
        self.set_default_device_properties()
        self.successful_open_session()
        request = command_message(self.new_transaction(), OperationDataCodes.ResetDevicePropValue, [5])
        response = response_message(request)
        self.dev.ResetDevicePropValue(request, response, None)
        self.assertEqual(response.code, ResponseCodes.DEVICE_PROP_NOT_SUPPORTED)

    def test_ResetDevicePropValueNoPropCode(self):
        self.set_default_device_properties()
        self.successful_open_session()
        request = command_message(self.new_transaction(), OperationDataCodes.ResetDevicePropValue, [])
        response = response_message(request)
        self.dev.ResetDevicePropValue(request, response, None)
        self.assertEqual(response.code, ResponseCodes.PARAMETER_NOT_SUPPORTED)

    def test_ResetDevicePropValueReadOnly(self):
        self.set_default_device_properties()
        self.successful_open_session()
        request = command_message(self.new_transaction(), OperationDataCodes.ResetDevicePropValue, [self.ro_prop.code.value])
        response = response_message(request)
        self.dev.ResetDevicePropValue(request, response, None)
        self.assertEqual(response.code, ResponseCodes.ACCESS_DENIED)
