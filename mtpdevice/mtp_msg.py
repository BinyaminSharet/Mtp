from __future__ import absolute_import
from struct import pack, unpack
from .mtp_exception import MtpProtocolException
from .mtp_proto import ResponseCodes, ContainerTypes


class MtpMessage(object):

    def __init__(self, length, ctype, code, tid, data):
        self.length = length
        self.ctype = ctype
        self.code = code
        self.tid = tid
        self.data = data

    def has_got_all_data(self):
        if self.length < len(self.data) + 0xc:
            raise MtpProtocolException('length(%#x) < actual data length(%#x) + 0xc' % (self.length, len(self.data) + 0xc))
        return self.length == len(self.data) + 0xc

    def pack(self):
        self.length = len(self.data) + 0xc
        return pack('<IHHI', self.length, self.ctype, self.code, self.tid) + self.data


class MtpParametersMessage(MtpMessage):

    def __init__(self, length, ctype, code, tid, data):
        super(MtpParametersMessage, self).__init__(length, ctype, code, tid, data)
        if len(data) % 4 != 0:
            raise MtpProtocolException(ResponseCodes.INVALID_CODE_FORMAT, 'Command message length (%#x) is not a multiple of four' % (len(data)))
        self.params = []
        for i in range(0, len(data), 4):
            self.params.append(unpack('<I', data[i:i + 4])[0])

    def num_params(self):
        return len(self.params)

    def get_param(self, idx):
        if idx < len(self.params):
            return self.params[idx]
        return None

    def add_param(self, param):
        self.params.append(param)

    def pack(self):
        self.data = b''
        for param in self.params:
            self.data += pack('<I', param)
        return super(MtpParametersMessage, self).pack()


def response_from_command(cmd, code):
    return MtpParametersMessage(0xc, ContainerTypes.Response, code, cmd.tid, b'')


def msg_from_buff(buff, permissive=False):
    if len(buff) < 0xc:
        raise MtpProtocolException(ResponseCodes.INVALID_CODE_FORMAT, 'request too short')
    length, ctype, code, tid = unpack('<IHHI', buff[:0xc])
    if not permissive:
        if len(buff) != length:
            raise MtpProtocolException(ResponseCodes.INVALID_CODE_FORMAT, 'request length (%#x) != actual length (%#x)' % (length, len(buff)))
    data = buff[0xc:]
    msg_classes = {
        ContainerTypes.Command: MtpParametersMessage,
        ContainerTypes.Data: MtpMessage,
        ContainerTypes.Response: MtpParametersMessage,
        ContainerTypes.Event: MtpMessage,
    }
    cls = msg_classes.get(ctype, MtpMessage)
    return cls(length, ctype, code, tid, data)
