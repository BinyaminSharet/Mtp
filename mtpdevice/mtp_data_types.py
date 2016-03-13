from struct import calcsize, pack, unpack
import datetime


class SimpleDataTypes(object):
    INT8 = 0x0001
    UINT8 = 0x0002
    INT16 = 0x0003
    UINT16 = 0x0004
    INT32 = 0x0005
    UINT32 = 0x0006
    INT64 = 0x0007
    UINT64 = 0x0008
    INT128 = 0x0009
    UINT128 = 0x000a
    AINT8 = 0x4001
    AUINT8 = 0x4002
    AINT16 = 0x4003
    AUINT16 = 0x4004
    AINT32 = 0x4005
    AUINT32 = 0x4006
    AINT64 = 0x4007
    AUINT64 = 0x4008
    AINT128 = 0x4009
    AUINT128 = 0x400a
    STR = 0xffff


class MtpDataType(object):

    def __init__(self, dtype, value):
        self.dtype = dtype
        self.size = None
        self.set_value(value)

    def set_value(self, value):
        self.value = value
        self.packed = None

    def pack(self):
        if self.packed is None:
            self.packed = self._pack()
        return self.packed

    def unpack(self, buff):
        res = self._unpack(buff)
        self.set_value(res)
        return (res, buff[self.size:])


class MtpIntType(MtpDataType):

    def __init__(self, fmt, dtype, value):
        self.fmt = fmt
        super(MtpIntType, self).__init__(dtype, value)
        self.size = calcsize(fmt)

    def _pack(self):
        return pack(self.fmt, self.value)

    def _unpack(self, buff):
        return unpack(self.fmt, buff[:self.size])[0]


def Int8(value=0):
    return MtpIntType('<b', SimpleDataTypes.INT8, value)


def UInt8(value=0):
    return MtpIntType('<B', SimpleDataTypes.UINT8, value)


def Int16(value=0):
    return MtpIntType('<h', SimpleDataTypes.INT16, value)


def UInt16(value=0):
    return MtpIntType('<H', SimpleDataTypes.UINT16, value)


def Int32(value=0):
    return MtpIntType('<i', SimpleDataTypes.INT32, value)


def UInt32(value=0):
    return MtpIntType('<I', SimpleDataTypes.UINT32, value)


def Int64(value=0):
    return MtpIntType('<q', SimpleDataTypes.INT64, value)


def UInt64(value=0):
    return MtpIntType('<Q', SimpleDataTypes.UINT64, value)


class I128(MtpIntType):

    def _pack(self):
        return pack(self.fmt, (self.value & 0xffffffffffffffff), ((self.value >> 64) & 0xffffffffffffffff))

    def _unpack(self, buff):
        part1, part2 = unpack(self.fmt, buff[:self.size])
        res = part1 | (part2 << 64)
        return res


def Int128(value=0):
    return I128('<qq', SimpleDataTypes.INT128, value)


def UInt128(value=0):
    return I128('<QQ', SimpleDataTypes.UINT128, value)


class MArray(MtpDataType):

    def __init__(self, ftype, values, ltype=None):
        if ltype is None:
            ltype = UInt32
        self.pseudo = ftype(0)
        self.ftype = ftype
        self.value = []
        self.length = ltype(0)
        super(MArray, self).__init__(self.pseudo.dtype | 0x4000, values)

    def set_value(self, value):
        for v in value:
            self.add_value(self.ftype(v))
        self.packed = None

    def add_value(self, value):
        self.value.append(value)
        self.packed = None
        self.length.set_value(self.length.value + 1)

    def _pack(self):
        packed = self.length.pack()
        for v in self.value:
            packed += v.pack()
        return packed

    def _unpack(self, buff):
        (length, rest) = self.length.unpack(buff)
        values = []
        for i in range(length):
            (v, rest) = self.pseudo.unpack(rest)
            values.append(v)
        self.set_value(values)
        self.size = self.length.size + (length * self.pseudo.size)
        return values


def MEnum(ftype, values):
    return MArray(ftype, values, UInt16)


class MStr(MtpDataType):

    def __init__(self, value=''):
        super(MStr, self).__init__(0xffff, value)

    def _pack(self):
        s = self.value
        if len(self.value):
            s += '\x00'
            encoded = s.encode('utf-16le')
        else:
            encoded = b''
        return pack('B', len(s)) + encoded

    def _unpack(self, buff):
        strlen = unpack('B', buff[0:1])[0]
        encodedlen = (strlen * 2)
        encoded = buff[1:encodedlen + 1]
        decoded = encoded.decode('utf-16le')
        resstr = decoded[:-1]
        self.size = encodedlen + 1
        self.value = resstr
        return resstr


class MDateTime(MStr):

    def _pack(self):
        intval = self.value
        dt = datetime.datetime.fromtimestamp(intval)
        self.value = dt.strftime('%Y%m%dT%H%M%S')
        packed = super(MDateTime, self)._pack()
        self.value = intval
        return packed

    def _unpack(self, buff):
        super(MDateTime, self)._unpack(buff)
        if len(self.value):
            self.value = int(datetime.datetime.strptime(self.value, '%Y%m%dT%H%M%S'))
        else:
            self.value = 0
        return self.value
