from mtp_base import MtpObjectContainer, MtpEntityInfoInterface
from mtp_proto import MU16, MU32, MStr, MArray, OperationDataCodes

operations = {}


def operation(opcode):
    def decorator(func):
        def wrapper(*args, **kwargs):
            res = func(*args, **kwargs)
            return res
        if opcode in operations:
            raise Exception('operation %#x already defined', opcode)
        operations[opcode] = wrapper
        return wrapper
    return decorator


class MtpDevice(MtpObjectContainer):

    def __init__(self, info):
        super(MtpDevice, self).__init__(info)
        self.storages = {}
        self.operations = operations

    def add_storage(self, storage):
        '''
        :type storage: MtpStorage
        :param storage: storage to add
        '''
        self.storages[storage.get_uid()] = storage
        storage.set_device(self)

    @operation(OperationDataCodes.GetDeviceInfo)
    def GetDeviceInfo(self):
        return self.get_info()


class MtpDeviceInfo(MtpEntityInfoInterface):

    def __init__(
        self,
        std_version, mtp_vendor_ext_id, mtp_version, mtp_extensions,
        functional_mode, operations_supported, events_supported,
        device_properties_supported, capture_formats, playback_formats,
        manufacturer, model, device_version, serial_number
    ):
        '''
        :type std_version: 16bit uint
        :param std_version: Standard Version
        :type mtp_vendor_ext_id: 32bit uint
        :param mtp_vendor_ext_id: MTP Vendor Extension ID
        :type mtp_version: 16bit uint
        :param mtp_version: MTP Version
        :type mtp_extensions: str
        :param mtp_extensions: MTP Extensions
        :type functional_mode: 16bit uint
        :param functional_mode: Functional Mode
        :type operations_supported: list of 16bit uint
        :param operations_supported: Operations Supported
        :type events_supported: list of 16bit uint
        :param events_supported: Events Supported
        :type device_properties_supported: list of 16bit uint
        :param device_properties_supported: Device Properties Supported
        :type capture_formats: list of 16bit uint
        :param capture_formats: Capture Formats
        :type playback_formats: list of 16bit uint
        :param playback_formats: Playback Formats
        :type manufacturer: str
        :param manufacturer: Manufacturer
        :type model: str
        :param model: Model
        :type device_version: str
        :param device_version: Device Version
        :type serial_number: str
        :param serial_number: Serial Number
        '''
        self.std_version = std_version
        self.mtp_vendor_ext_id = mtp_vendor_ext_id
        self.mtp_version = mtp_version
        self.mtp_extensions = mtp_extensions
        self.functional_mode = functional_mode
        self.operations_supported = operations_supported
        self.events_supported = events_supported
        self.device_properties_supported = device_properties_supported
        self.capture_formats = capture_formats
        self.playback_formats = playback_formats
        self.manufacturer = manufacturer
        self.model = model
        self.device_version = device_version
        self.serial_number = serial_number

    def pack(self):
        return (
            MU16(self.std_version) +
            MU32(self.mtp_vendor_ext_id) +
            MU16(self.mtp_version) +
            MStr(self.mtp_extensions) +
            MU16(self.functional_mode) +
            MArray(MU16, self.operations_supported) +
            MArray(MU16, self.events_supported) +
            MArray(MU16, self.device_properties_supported) +
            MArray(MU16, self.capture_formats) +
            MArray(MU16, self.playback_formats) +
            MStr(self.manufacturer) +
            MStr(self.model) +
            MStr(self.device_version) +
            MStr(self.serial_number)
        )




























