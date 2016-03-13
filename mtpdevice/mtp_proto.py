from __future__ import absolute_import
from .mtp_data_types import UInt16, UInt32


class DataCodeTypes(object):
    PTP_OPERATION = 0x1000
    PTP_RESPONSE = 0x2000
    PTP_OBJECT_FORMAT = 0x3000
    PTP_EVENT = 0x4000
    PTP_DEVICE_PROP = 0x5000
    VENDOR_EXTENSION_OPERATION = 0x9000
    MTP_OPERATION = 0x9800
    VENDOR_EXTENSION_RESPONSE = 0xA000
    MTP_RESPONSE = 0xA800
    VENDOR_EXTENSION_OBJECT_FORMAT = 0xB000
    MTP_OBJECT_FORMAT = 0xB800
    VENDOR_EXTENSION_EVENT = 0xC000
    MTP_EVENT = 0xC800
    VENDOR_EXTENSION_DEVICE_PROP = 0xD000
    MTP_DEVICE_PROP = 0xD400
    VENDOR_EXTENSION_OBJECT_PROP = 0xD800
    MTP_OBJECT_PROP = 0xDC00


class ResponseCodes(object):
    UNDEFINED = 0x2000
    OK = 0x2001
    GENERAL_ERROR = 0x2002
    SESSION_NOT_OPEN = 0x2003
    INVALID_TRANSACTION_ID = 0x2004
    OPERATION_NOT_SUPPORTED = 0x2005
    PARAMETER_NOT_SUPPORTED = 0x2006
    INCOMPLETE_TRANSFER = 0x2007
    INVALID_STORAGE_ID = 0x2008
    INVALID_OBJECT_HANDLE = 0x2009
    DEVICE_PROP_NOT_SUPPORTED = 0x200A
    INVALID_OBJECT_FORMAT_CODE = 0x200B
    STORE_FULL = 0x200C
    OBJECT_WRITE_PROTECTED = 0x200D
    STORE_READ_ONLY = 0x200E
    ACCESS_DENIED = 0x200F
    NO_THUMBNAIL_PRESENT = 0x2010
    SELF_TEST_FAILED = 0x2011
    PARTIAL_DELETION = 0x2012
    STORE_NOT_AVAILABLE = 0x2013
    SPECIFICATION_BY_FORMAT_UNSUPPORTED = 0x2014
    NO_VALID_OBJECT_INFO = 0x2015
    INVALID_CODE_FORMAT = 0x2016
    UNKNOWN_VENDOR_CODE = 0x2017
    CAPTURE_ALREADY_TERMINATED = 0x2018
    DEVICE_BUSY = 0x2019
    INVALID_PARENT_OBJECT = 0x201A
    INVALID_DEVICE_PROP_FORMAT = 0x201B
    INVALID_DEVICE_PROP_VALUE = 0x201C
    INVALID_PARAMETER = 0x201D
    SESSION_ALREADY_OPEN = 0x201E
    TRANSACTION_CANCELLED = 0x201F
    SPECIFICATION_OF_DESTINATION_UNSUPPORTED = 0x2020
    INVALID_OBJECT_PROP_CODE = 0xA801
    INVALID_OBJECT_PROP_FORMAT = 0xA802
    INVALID_OBJECT_PROP_VALUE = 0xA803
    INVALID_OBJECT_REFERENCE = 0xA804
    GROUP_NOT_SUPPORTED = 0xA805
    INVALID_DATASET = 0xA806
    SPECIFICATION_BY_GROUP_UNSUPPORTED = 0xA807
    SPECIFICATION_BY_DEPTH_UNSUPPORTED = 0xA808
    OBJECT_TOO_LARGE = 0xA809
    OBJECT_PROP_NOT_SUPPORTED = 0xA80A


class OperationDataCodes(object):
    GetDeviceInfo = 0x1001
    OpenSession = 0x1002
    CloseSession = 0x1003
    GetStorageIDs = 0x1004
    GetStorageInfo = 0x1005
    GetNumObjects = 0x1006
    GetObjectHandles = 0x1007
    GetObjectInfo = 0x1008
    GetObject = 0x1009
    GetThumb = 0x100A
    DeleteObject = 0x100B
    SendObjectInfo = 0x100C
    SendObject = 0x100D
    InitiateCapture = 0x100E
    FormatStore = 0x100F
    ResetDevice = 0x1010
    SelfTest = 0x1011
    SetObjectProtection = 0x1012
    PowerDown = 0x1013
    GetDevicePropDesc = 0x1014
    GetDevicePropValue = 0x1015
    SetDevicePropValue = 0x1016
    ResetDevicePropValue = 0x1017
    TerminateOpenCapture = 0x1018
    MoveObject = 0x1019
    CopyObject = 0x101A
    GetPartialObject = 0x101B
    InitiateOpenCapture = 0x101C
    GetObjectPropsSupported = 0x9801
    GetObjectPropDesc = 0x9802
    GetObjectPropValue = 0x9803
    SetObjectPropValue = 0x9804
    GetObjectPropList = 0x9805
    SetObjectPropList = 0x9806
    GetInterdependentPropDesc = 0x9807
    SendObjectPropList = 0x9808
    GetObjectReferences = 0x9810
    SetObjectReferences = 0x9811
    Skip = 0x9820


class ContainerTypes(object):
    Undefined = 0
    Command = 1
    Data = 2
    Response = 3
    Event = 4


class StorageType(object):
    FIXED_ROM = 0x0001
    REMOVABLE_ROM = 0x0002
    FIXED_RAM = 0x0003
    REMOVABLE_RAM = 0x0004


class FSType(object):
    FLAT = 0x0001
    HIERARCHICAL = 0x0002
    DCF = 0x0003


class AccessCaps(object):
    READ_WRITE = 0x0000
    READ_ONLY_WITHOUT_DELETE = 0x0001
    READ_ONLY_WITH_DELETE = 0x0002


def mtp_data(container, data):
    return UInt32(len(data) + 0xC).pack() + UInt16(ContainerTypes.Data).pack() + UInt16(container.code).pack() + UInt32(container.tid).pack() + data
