#!/usr/bin/env python
import unittest
from mtp_device import MtpDevice, MtpDeviceInfo, MtpRequest, MtpResponse
from mtp_storage import MtpStorage, MtpStorageInfo
from mtp_object import MtpObject
from mtp_proto import OperationDataCodes, ResponseCodes


class MtpDeviceApiTests(unittest.TestCase):

    def setUp(self):
        super(MtpDeviceApiTests, self).setUp()
        self.objects = MtpObject.from_fs_recursive('.')
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
        self.storage.add_object(self.objects)
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

    def test_OpenSessionWithSessionId(self):
        session_id = 1
        request = MtpRequest(1, OperationDataCodes.OpenSession, [session_id])
        response = MtpResponse(request)
        self.dev.OpenSession(request, response)
        self.assertEqual(response.status, ResponseCodes.OK)
        self.assertEqual(self.dev.session_id, session_id)

    def test_OpenSessionWithoutParams(self):
        request = MtpRequest(1, OperationDataCodes.OpenSession, [])
        response = MtpResponse(request)
        self.dev.OpenSession(request, response)
        self.assertEqual(response.status, ResponseCodes.PARAMETER_NOT_SUPPORTED)
        self.assertIsNone(self.dev.session_id)

    def test_OpenSessionTwice(self):
        session_id = 1
        request = MtpRequest(1, OperationDataCodes.OpenSession, [session_id])
        response = MtpResponse(request)
        self.dev.OpenSession(request, response)
        self.assertEqual(response.status, ResponseCodes.OK)
        self.assertEqual(self.dev.session_id, session_id)

        request = MtpRequest(1, OperationDataCodes.OpenSession, [session_id + 1])
        response = MtpResponse(request)
        self.dev.OpenSession(request, response)
        self.assertEqual(response.status, ResponseCodes.SESSION_ALREADY_OPEN)
        self.assertEqual(self.dev.session_id, session_id)

    def test_CloseSessionAfterOpenSession(self):
        session_id = 1
        request = MtpRequest(1, OperationDataCodes.OpenSession, [session_id])
        response = MtpResponse(request)
        self.dev.OpenSession(request, response)

        request = MtpRequest(1, OperationDataCodes.CloseSession, [])
        response = MtpResponse(request)
        self.dev.CloseSession(request, response)
        self.assertEqual(response.status, ResponseCodes.OK)
        self.assertIsNone(self.dev.session_id)

    def test_CloseSessionBeforeOpenSession(self):
        request = MtpRequest(1, OperationDataCodes.CloseSession, [])
        response = MtpResponse(request)
        self.dev.CloseSession(request, response)
        self.assertEqual(response.status, ResponseCodes.SESSION_NOT_OPEN)

    def test_CloseSessionAfterCloseSession(self):
        session_id = 1
        request = MtpRequest(1, OperationDataCodes.OpenSession, [session_id])
        response = MtpResponse(request)
        self.dev.OpenSession(request, response)

        request = MtpRequest(1, OperationDataCodes.CloseSession, [])
        response = MtpResponse(request)
        self.dev.CloseSession(request, response)
        self.assertEqual(response.status, ResponseCodes.OK)
        self.assertIsNone(self.dev.session_id)

        request = MtpRequest(1, OperationDataCodes.CloseSession, [])
        response = MtpResponse(request)
        self.dev.CloseSession(request, response)
        self.assertEqual(response.status, ResponseCodes.SESSION_NOT_OPEN)

    def test_GetDeviceInfoBeforeOpenSession(self):
        request = MtpRequest(1, OperationDataCodes.GetDeviceInfo, [])
        response = MtpResponse(request)
        self.dev.GetDeviceInfo(request, response)
        self.assertEqual(response.status, ResponseCodes.OK)

    def test_GetDeviceInfoAfterOpenSession(self):
        session_id = 1
        request = MtpRequest(1, OperationDataCodes.OpenSession, [session_id])
        response = MtpResponse(request)
        self.dev.OpenSession(request, response)

        request = MtpRequest(2, OperationDataCodes.GetDeviceInfo, [])
        response = MtpResponse(request)
        self.dev.GetDeviceInfo(request, response)
        self.assertEqual(response.status, ResponseCodes.OK)

    def test_GetStorageIDsAfterOpenSession(self):
        session_id = 1
        request = MtpRequest(1, OperationDataCodes.OpenSession, [session_id])
        response = MtpResponse(request)
        self.dev.OpenSession(request, response)

        request = MtpRequest(2, OperationDataCodes.GetStorageIDs, [])
        response = MtpResponse(request)
        self.dev.GetStorageIDs(request, response)
        self.assertEqual(response.status, ResponseCodes.OK)

    def test_GetStorageIDsBeforeOpenSession(self):
        request = MtpRequest(2, OperationDataCodes.GetStorageIDs, [])
        response = MtpResponse(request)
        self.dev.GetStorageIDs(request, response)
        self.assertEqual(response.status, ResponseCodes.SESSION_NOT_OPEN)

    def test_GetStorageInfoAfterOpenSession(self):
        session_id = 1
        request = MtpRequest(1, OperationDataCodes.OpenSession, [session_id])
        response = MtpResponse(request)
        self.dev.OpenSession(request, response)

        request = MtpRequest(2, OperationDataCodes.GetStorageInfo, [self.storage.get_uid()])
        response = MtpResponse(request)
        self.dev.GetStorageInfo(request, response)
        self.assertEqual(response.status, ResponseCodes.OK)

    def test_GetStorageInfoBeforeOpenSession(self):
        request = MtpRequest(2, OperationDataCodes.GetStorageInfo, [self.storage.get_uid()])
        response = MtpResponse(request)
        self.dev.GetStorageInfo(request, response)
        self.assertEqual(response.status, ResponseCodes.SESSION_NOT_OPEN)

    def test_GetStorageInfoWithoutStorageId(self):
        session_id = 1
        request = MtpRequest(1, OperationDataCodes.OpenSession, [session_id])
        response = MtpResponse(request)
        self.dev.OpenSession(request, response)

        request = MtpRequest(2, OperationDataCodes.GetStorageInfo, [])
        response = MtpResponse(request)
        self.dev.GetStorageInfo(request, response)
        self.assertEqual(response.status, ResponseCodes.PARAMETER_NOT_SUPPORTED)

    def test_GetStorageInfoWithInvalidStorageId(self):
        session_id = 1
        request = MtpRequest(1, OperationDataCodes.OpenSession, [session_id])
        response = MtpResponse(request)
        self.dev.OpenSession(request, response)

        request = MtpRequest(2, OperationDataCodes.GetStorageInfo, [self.storage.get_uid() + 1])
        response = MtpResponse(request)
        self.dev.GetStorageInfo(request, response)
        self.assertEqual(response.status, ResponseCodes.INVALID_STORAGE_ID)

    def test_GetNumObjectsBeforeOpenSession(self):
        request = MtpRequest(2, OperationDataCodes.GetNumObjects, [self.storage.get_uid()])
        response = MtpResponse(request)
        self.dev.GetNumObjects(request, response)
        self.assertEqual(response.status, ResponseCodes.SESSION_NOT_OPEN)

    def test_GetNumObjectsAfterOpenSession(self):
        session_id = 1
        request = MtpRequest(1, OperationDataCodes.OpenSession, [session_id])
        response = MtpResponse(request)
        self.dev.OpenSession(request, response)

        request = MtpRequest(2, OperationDataCodes.GetNumObjects, [self.storage.get_uid()])
        response = MtpResponse(request)
        self.dev.GetNumObjects(request, response)
        self.assertEqual(response.status, ResponseCodes.OK)

    def test_GetNumObjectsWithoutStorageId(self):
        session_id = 1
        request = MtpRequest(1, OperationDataCodes.OpenSession, [session_id])
        response = MtpResponse(request)
        self.dev.OpenSession(request, response)

        request = MtpRequest(2, OperationDataCodes.GetNumObjects, [])
        response = MtpResponse(request)
        self.dev.GetNumObjects(request, response)
        self.assertEqual(response.status, ResponseCodes.PARAMETER_NOT_SUPPORTED)

    def test_GetNumObjectsWithInvalidStorageId(self):
        session_id = 1
        request = MtpRequest(1, OperationDataCodes.OpenSession, [session_id])
        response = MtpResponse(request)
        self.dev.OpenSession(request, response)

        request = MtpRequest(2, OperationDataCodes.GetNumObjects, [self.storage.get_uid() + 1])
        response = MtpResponse(request)
        self.dev.GetNumObjects(request, response)
        self.assertEqual(response.status, ResponseCodes.INVALID_STORAGE_ID)

    def test_GetObjectHandlesBeforeOpenSession(self):
        request = MtpRequest(2, OperationDataCodes.GetObjectHandles, [self.storage.get_uid()])
        response = MtpResponse(request)
        self.dev.GetObjectHandles(request, response)
        self.assertEqual(response.status, ResponseCodes.SESSION_NOT_OPEN)

    def test_GetObjectHandlesAfterOpenSession(self):
        session_id = 1
        request = MtpRequest(1, OperationDataCodes.OpenSession, [session_id])
        response = MtpResponse(request)
        self.dev.OpenSession(request, response)

        request = MtpRequest(2, OperationDataCodes.GetObjectHandles, [self.storage.get_uid()])
        response = MtpResponse(request)
        self.dev.GetObjectHandles(request, response)
        self.assertEqual(response.status, ResponseCodes.OK)

    def test_GetObjectHandlesWithoutStorageId(self):
        session_id = 1
        request = MtpRequest(1, OperationDataCodes.OpenSession, [session_id])
        response = MtpResponse(request)
        self.dev.OpenSession(request, response)

        request = MtpRequest(2, OperationDataCodes.GetObjectHandles, [])
        response = MtpResponse(request)
        self.dev.GetObjectHandles(request, response)
        self.assertEqual(response.status, ResponseCodes.PARAMETER_NOT_SUPPORTED)

    def test_GetObjectHandlesWithInvalidStorageId(self):
        session_id = 1
        request = MtpRequest(1, OperationDataCodes.OpenSession, [session_id])
        response = MtpResponse(request)
        self.dev.OpenSession(request, response)

        request = MtpRequest(2, OperationDataCodes.GetObjectHandles, [self.storage.get_uid() + 1])
        response = MtpResponse(request)
        self.dev.GetObjectHandles(request, response)
        self.assertEqual(response.status, ResponseCodes.INVALID_STORAGE_ID)

    def test_GetObjectInfoBeforeOpenSession(self):
        request = MtpRequest(2, OperationDataCodes.GetObjectInfo, [self.storage.get_uid()])
        response = MtpResponse(request)
        self.dev.GetObjectInfo(request, response)
        self.assertEqual(response.status, ResponseCodes.SESSION_NOT_OPEN)

    def test_GetObjectInfoAfterOpenSession(self):
        session_id = 1
        request = MtpRequest(1, OperationDataCodes.OpenSession, [session_id])
        response = MtpResponse(request)
        self.dev.OpenSession(request, response)

        request = MtpRequest(2, OperationDataCodes.GetObjectInfo, [self.objects.get_uid()])
        response = MtpResponse(request)
        self.dev.GetObjectInfo(request, response)
        self.assertEqual(response.status, ResponseCodes.OK)

    def test_GetObjectInfoWithoutObjectHandle(self):
        session_id = 1
        request = MtpRequest(1, OperationDataCodes.OpenSession, [session_id])
        response = MtpResponse(request)
        self.dev.OpenSession(request, response)

        request = MtpRequest(2, OperationDataCodes.GetObjectInfo, [])
        response = MtpResponse(request)
        self.dev.GetObjectInfo(request, response)
        self.assertEqual(response.status, ResponseCodes.PARAMETER_NOT_SUPPORTED)

    def test_GetObjectInfoWithInvalidObjectHandle(self):
        session_id = 1
        request = MtpRequest(1, OperationDataCodes.OpenSession, [session_id])
        response = MtpResponse(request)
        self.dev.OpenSession(request, response)

        request = MtpRequest(2, OperationDataCodes.GetObjectInfo, [0xfffffffe])
        response = MtpResponse(request)
        self.dev.GetObjectInfo(request, response)
        self.assertEqual(response.status, ResponseCodes.INVALID_OBJECT_HANDLE)

    def test_GetObjectBeforeOpenSession(self):
        request = MtpRequest(2, OperationDataCodes.GetObject, [self.storage.get_uid()])
        response = MtpResponse(request)
        self.dev.GetObject(request, response)
        self.assertEqual(response.status, ResponseCodes.SESSION_NOT_OPEN)

    def test_GetObjectAfterOpenSession(self):
        session_id = 1
        request = MtpRequest(1, OperationDataCodes.OpenSession, [session_id])
        response = MtpResponse(request)
        self.dev.OpenSession(request, response)

        request = MtpRequest(2, OperationDataCodes.GetObject, [self.objects.get_uid()])
        response = MtpResponse(request)
        self.dev.GetObject(request, response)
        self.assertEqual(response.status, ResponseCodes.OK)

    def test_GetObjectWithoutObjectHandle(self):
        session_id = 1
        request = MtpRequest(1, OperationDataCodes.OpenSession, [session_id])
        response = MtpResponse(request)
        self.dev.OpenSession(request, response)

        request = MtpRequest(2, OperationDataCodes.GetObject, [])
        response = MtpResponse(request)
        self.dev.GetObject(request, response)
        self.assertEqual(response.status, ResponseCodes.PARAMETER_NOT_SUPPORTED)

    def test_GetObjectWithInvalidObjectHandle(self):
        session_id = 1
        request = MtpRequest(1, OperationDataCodes.OpenSession, [session_id])
        response = MtpResponse(request)
        self.dev.OpenSession(request, response)

        request = MtpRequest(2, OperationDataCodes.GetObject, [0xfffffffe])
        response = MtpResponse(request)
        self.dev.GetObject(request, response)
        self.assertEqual(response.status, ResponseCodes.INVALID_OBJECT_HANDLE)

if __name__ == '__main__':
    unittest.main()
