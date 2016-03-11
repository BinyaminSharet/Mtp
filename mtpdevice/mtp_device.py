from __future__ import absolute_import
from .mtp_proto import MU16, MU32, MStr, MArray, OperationDataCodes, ResponseCodes, mtp_data, ContainerTypes
from .mtp_object import MtpObjectInfo, MtpObject
from .mtp_exception import MtpProtocolException


operations = {}


class Operation(object):
    def __init__(self, handler, ir_data=False):
        self.handler = handler
        self.ir_data = ir_data


def operation(opcode, num_params=None, session_required=True, ir_data_required=False):
    '''
    Decorator for an API operation function

    :param opcode: operation code
    :param num_params: number of parameter the operation expects (default: None)
    :param session_required: is the operation requires a session (default: True)
    :param ir_data_required: is data expected from the initiator (default: False)
    '''

    def decorator(func):
        def wrapper(self, command, response, ir_data):
            try:
                if num_params is not None:
                    if command.ctype != ContainerTypes.Command:
                        raise MtpProtocolException(ResponseCodes.INVALID_CODE_FORMAT)
                    if command.num_params() < num_params:
                        raise MtpProtocolException(ResponseCodes.PARAMETER_NOT_SUPPORTED)
                if session_required and (self.session_id is None):
                    raise MtpProtocolException(ResponseCodes.SESSION_NOT_OPEN)
                if ir_data_required and (ir_data is None):
                    raise MtpProtocolException(ResponseCodes.INVALID_DATASET)
                res = func(self, command, response, ir_data)
            except MtpProtocolException as ex:
                response.code = ex.response
                res = None
            return res

        if opcode in operations:
            raise Exception('operation %#x already defined', opcode)
        operations[opcode] = Operation(wrapper, ir_data_required)
        return wrapper

    return decorator


class MtpDevice(object):

    def __init__(self, info):
        super(MtpDevice, self).__init__()
        self.info = info
        self.stores = {}
        self.operations = operations
        self.info.operations_supported = list(operations.keys())
        self.session_id = None
        self.last_obj = None

    def get_info(self):
        return self.info.pack()

    def add_storage(self, storage):
        '''
        :type storage: MtpStorage
        :param storage: storage to add
        '''
        self.stores[storage.get_uid()] = storage
        storage.set_device(self)

    def handle_transaction(self, command, response, ir_data):
        ccode = command.code
        if ccode in operations:
            if self.last_obj and (ccode != OperationDataCodes.SendObject):
                self.last_obj.delete(0xffffffff)
                self.last_obj = None
            return self.operations[ccode].handler(self, command, response, ir_data)
        return None

    @operation(OperationDataCodes.GetDeviceInfo, num_params=0, session_required=False)
    def GetDeviceInfo(self, command, response, ir_data):
        return mtp_data(command, self.get_info())

    # @operation(OperationDataCodes., num_params=None, session_required=True)
    @operation(OperationDataCodes.OpenSession, num_params=1, session_required=False)
    def OpenSession(self, command, response, ir_data):
        if self.session_id:
            raise MtpProtocolException(ResponseCodes.SESSION_ALREADY_OPEN)
        self.session_id = command.params[0]

    @operation(OperationDataCodes.CloseSession, num_params=0)
    def CloseSession(self, command, response, ir_data):
        self.session_id = None

    @operation(OperationDataCodes.GetStorageIDs, num_params=0)
    def GetStorageIDs(self, command, response, ir_data):
        ids = list(self.stores.keys())
        data = MArray(MU32, ids)
        return mtp_data(command, data)

    @operation(OperationDataCodes.GetStorageInfo, num_params=1)
    def GetStorageInfo(self, command, response, ir_data):
        storage_id = command.get_param(0)
        storage = self.get_storage(storage_id)
        return mtp_data(command, storage.get_info())

    @operation(OperationDataCodes.GetNumObjects, num_params=1)
    def GetNumObjects(self, command, response, ir_data):
        storage_id = command.get_param(0)
        obj_fmt_code = command.get_param(1)
        handles = self.get_handles_for_store_id(storage_id, obj_fmt_code)
        # .. todo:: assoc_handle filtering
        # assoc_handle = command.get_param(2)
        return mtp_data(command, MU32(len(handles)))

    @operation(OperationDataCodes.GetObjectHandles, num_params=1)
    def GetObjectHandles(self, command, response, ir_data):
        storage_id = command.get_param(0)
        obj_fmt_code = command.get_param(1)
        handles = self.get_handles_for_store_id(storage_id, obj_fmt_code)
        # .. todo:: assoc_handle filtering
        # assoc_handle = command.get_param(2)
        return mtp_data(command, MArray(MU32, handles))

    @operation(OperationDataCodes.GetObjectInfo, num_params=1)
    def GetObjectInfo(self, command, response, ir_data):
        handle = command.get_param(0)
        obj = self.get_object(handle)
        return mtp_data(command, obj.get_info())

    @operation(OperationDataCodes.GetObject, num_params=1)
    def GetObject(self, command, response, ir_data):
        handle = command.get_param(0)
        obj = self.get_object(handle)
        return mtp_data(command, obj.data)

    @operation(OperationDataCodes.GetThumb, num_params=1)
    def GetThumb(self, command, response, ir_data):
        handle = command.get_param(0)
        obj = self.get_object(handle)
        return mtp_data(command, obj.get_thumb())

    @operation(OperationDataCodes.DeleteObject, num_params=1)
    def DeleteObject(self, command, response, ir_data):
        handle = command.get_param(0)
        obj_fmt_code = command.get_param(1)
        if handle == 0xffffffff:
            self.delete_all_objects(obj_fmt_code)
        else:
            obj = self.get_object(handle)
            obj.delete(0xffffffff)

    @operation(OperationDataCodes.SendObjectInfo, num_params=1, ir_data_required=True)
    def SendObjectInfo(self, command, response, ir_data):
        '''
        .. todo:: complete !!
        '''
        storage_id = command.get_param(0)
        parent_handle = command.get_param(1)
        if storage_id:
            store = self.get_storage(storage_id)
            if parent_handle:
                parent = store.get_object(parent_handle)
                parent_uid = parent.get_uid()
            else:
                parent = store
                parent_uid = 0xffffffff
            if store.can_write():
                obj_info = MtpObjectInfo.from_buff(ir_data.data)
                obj = MtpObject(None, obj_info, [])
                parent.add_object(obj)
                response.add_param(store.get_uid())
                response.add_param(parent_uid)
                response.add_param(obj.get_uid())
                # next operation MUST be SendObject, otherwise we do NOT keep the object
                # so we need a refrence to it.
                self.last_obj = obj
            else:
                raise MtpProtocolException(ResponseCodes.STORE_READ_ONLY)
        else:
            #
            # This might not be accurate, but I'm willing to play with that for now
            raise MtpProtocolException(ResponseCodes.INVALID_STORAGE_ID)

    @operation(OperationDataCodes.SendObject, num_params=0, ir_data_required=True)
    def SendObject(self, command, response, ir_data):
        if not self.last_obj:
            raise MtpProtocolException(ResponseCodes.NO_VALID_OBJECT_INFO)
        self.last_obj.set_data(ir_data.data, adhere_size=True)
        self.last_obj = None

    # @operation(OperationDataCodes.InitiateCapture, num_params=0):
    def InitiateCapture(self, command, response, ir_data):
        '''
        .. todo::

            This is part of a complex operation (first time to have events)
            so it is not implemented for now ...
            See appendix D.2.14
        '''
        raise MtpProtocolException(ResponseCodes.OPERATION_NOT_SUPPORTED)

    @operation(OperationDataCodes.FormatStore, num_params=1)
    def FormatStore(self, command, response, ir_data):
        '''
        Current implementation will NOT perform a format
        '''
        storage_id = command.get_param(0)
        self.get_storage(storage_id)
        raise MtpProtocolException(ResponseCodes.PARAMETER_NOT_SUPPORTED)

    @operation(OperationDataCodes.ResetDevice, num_params=0)
    def ResetDevice(self, command, response, ir_data):
        if not self.session_id:
            raise MtpProtocolException(ResponseCodes.SESSION_NOT_OPEN)
        self.session_id = None

    def delete_all_objects(self, obj_fmt_code):
        deleted = False
        undeleted = False
        for store in self.stores.values():
            objects = store.get_objects()
            for obj in objects:
                try:
                    obj.delete(obj_fmt_code)
                    deleted = True
                except MtpProtocolException as ex:
                    if ex.status == ResponseCodes.PARTIAL_DELETION:
                        deleted = True
                    undeleted = True
        if undeleted:
            if deleted:
                raise MtpProtocolException(ResponseCodes.OBJECT_WRITE_PROTECTED)
            else:
                raise MtpProtocolException(ResponseCodes.PARTIAL_DELETION)

    def get_handles_for_store_id(self, storage_id, obj_fmt_code):
        '''
        :param stores: stores to search in
        :param obj_fmt_code: format to filter objects by
        :return: list of handles
        '''
        res = []
        if storage_id == 0xffffffff:
            relevant_store = list(self.stores.values())
        else:
            relevant_store = [self.get_storage(storage_id)]
        for store in relevant_store:
            handles = [h for h in store.get_handles() if store.get_object(h).format_matches(obj_fmt_code)]
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


class MtpDeviceInfo(object):

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
