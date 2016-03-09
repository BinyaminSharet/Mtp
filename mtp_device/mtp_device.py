from mtp_base import MtpObjectContainer, MtpEntityInfoInterface
from mtp_proto import MU16, MU32, MStr, MArray, OperationDataCodes, ResponseCodes, mtp_data
from struct import unpack


class MtpProtocolException(Exception):

    def __init__(self, response, msg=None):
        super(MtpProtocolException, self).__init__(msg)
        self.response = response


operations = {}


def operation(opcode, num_params=None, session_required=True):
    '''
    Decorator for an API operation function

    :param opcode: operation code
    :param num_params: number of parameter the operation expects (default: None)
    :param session_required: is the operation requires a session (default: True)
    '''

    def decorator(func):

        def wrapper(self, request, response):
            try:
                if num_params is not None:
                    if request.num_params() < num_params:
                        raise MtpProtocolException(ResponseCodes.PARAMETER_NOT_SUPPORTED)
                if session_required and (self.session_id is None):
                    raise MtpProtocolException(ResponseCodes.SESSION_NOT_OPEN)
                res = func(self, request)
            except MtpProtocolException as ex:
                response.status = ex.response
                res = None
            return res

        if opcode in operations:
            raise Exception('operation %#x already defined', opcode)
        operations[opcode] = wrapper
        return wrapper

    return decorator


class MtpRequest(object):

    def __init__(self, tid, code, params):
        self.tid = tid
        self.code = code
        self.params = params

    def num_params(self):
        return len(self.params)

    def get_param(self, idx):
        if idx < len(self.params):
            return self.params[idx]
        return None

    @classmethod
    def from_buff(cls, data):
        if len(data) % 4 != 0:
            raise Exception('request length (%#x) is not a multiple of four' % (len(data)))
        if len(data) < 0xc:
            raise Exception('request too short')
        length, ctype, opcode, tid = unpack('<IBBI', data[:0xc])
        if len(data) != length:
            raise Exception('request length (%#x) != actual length (%#x)' % (length, len(data)))
        params_buff = data[0xc:]
        params = []
        for i in range(0, len(params_buff), 4):
            params.append(unpack('<I', params_buff[i:i + 4])[0])
        return MtpRequest(tid, opcode, params)


class MtpResponse(object):

    def __init__(self, request):
        self.request = request
        self.status = ResponseCodes.OK
        self.data = None


class MtpDevice(MtpObjectContainer):

    def __init__(self, info):
        super(MtpDevice, self).__init__(info)
        self.stores = {}
        self.operations = operations
        self.info.operations_supported = operations.keys()
        self.session_id = None

    def add_storage(self, storage):
        '''
        :type storage: MtpStorage
        :param storage: storage to add
        '''
        self.stores[storage.get_uid()] = storage
        storage.set_device(self)

    @operation(OperationDataCodes.GetDeviceInfo, num_params=0, session_required=False)
    def GetDeviceInfo(self, request):
        return mtp_data(request, self.get_info())

    # @operation(OperationDataCodes., num_params=None, session_required=True)
    @operation(OperationDataCodes.OpenSession, num_params=1, session_required=False)
    def OpenSession(self, request):
        if self.session_id:
            raise MtpProtocolException(ResponseCodes.SESSION_ALREADY_OPEN)
        self.session_id = request.params[0]

    @operation(OperationDataCodes.CloseSession, num_params=0)
    def CloseSession(self, request):
        self.session_id = None

    @operation(OperationDataCodes.GetStorageIDs, num_params=0)
    def GetStorageIDs(self, request):
        ids = self.stores.keys()
        data = MArray(MU32, ids)
        return mtp_data(request, data)

    @operation(OperationDataCodes.GetStorageInfo, num_params=1)
    def GetStorageInfo(self, request):
        storage_id = request.get_param(0)
        storage = self.get_storage(storage_id)
        return mtp_data(request, storage.get_info())

    @operation(OperationDataCodes.GetNumObjects, num_params=1)
    def GetNumObjects(self, request):
        storage_id = request.get_param(0)
        if storage_id == 0xffffffff:
            relevant_store = self.stores.values()
        else:
            relevant_store = [self.get_storage(storage_id)]
        obj_fmt_code = request.get_param(1)
        handles = self.get_handles_from_stores(relevant_store, obj_fmt_code)
        # .. todo:: assoc_handle filtering
        # assoc_handle = request.get_param(2)
        return mtp_data(request, MU32(len(handles)))

    @operation(OperationDataCodes.GetObjectHandles, num_params=1)
    def GetObjectHandles(self, request):
        storage_id = request.get_param(0)
        if storage_id == 0xffffffff:
            relevant_store = self.stores.values()
        else:
            relevant_store = [self.get_storage(storage_id)]
        obj_fmt_code = request.get_param(1)
        handles = self.get_handles_from_stores(relevant_store, obj_fmt_code)
        # .. todo:: assoc_handle filtering
        # assoc_handle = request.get_param(2)
        return mtp_data(request, MArray(MU32, handles))

    @operation(OperationDataCodes.GetObjectInfo, num_params=1)
    def GetObjectInfo(self, request):
        handle = request.get_param(0)
        obj = self.get_object(handle)
        return mtp_data(request, obj.get_info())

    @operation(OperationDataCodes.GetObject, num_params=1)
    def GetObject(self, request):
        handle = request.get_param(0)
        obj = self.get_object(handle)
        return mtp_data(request, obj.data)

    # @operation(OperationDataCodes.GetThumb, num_params=1)
    # def GetThumb(self, request):

    def get_handles_from_stores(self, stores, obj_fmt_code):
        '''
        :param stores: stores to search in
        :param obj_fmt_code: format to filter objects by
        :return: list of handles
        '''
        res = []
        for store in stores:
            handles = store.get_handles()
            if obj_fmt_code:
                handles = [h for h in handles if store.get_object(h).get_fmt() == obj_fmt_code]
            res.extend(handles)
        return res

    def get_object(self, handle):
        '''
        :param handle: handle of the object
        :raises: MtpProtocolException if there is no object with given handle
        :return: MtpObject
        '''
        obj = None
        for store in self.stores.values():
            obj = store.get_object(handle)
            if obj:
                break
        if not obj:
            raise MtpProtocolException(ResponseCodes.INVALID_OBJECT_HANDLE)
        return obj

    def get_storage(self, storage_id):
        '''
        :param storage_id: the storage id to get
        :raises: MtpProtocolException if storage with this id does not exist
        :return: MtpStorage
        '''
        if storage_id not in self.stores:
            raise MtpProtocolException(ResponseCodes.INVALID_STORAGE_ID)
        return self.stores[storage_id]


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
