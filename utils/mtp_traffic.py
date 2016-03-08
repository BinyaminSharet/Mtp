#!/usr/bin/env python
import pcapy
import sys
from struct import unpack


ctypes = ['Undefined', 'Command', 'Data', 'Response', 'Event']
ops = {
    0x1001: 'GetDeviceInfo',
    0x1002: 'OpenSession',
    0x1003: 'CloseSession',
    0x1004: 'GetStorageIDs',
    0x1005: 'GetStorageInfo',
    0x1006: 'GetNumObjects',
    0x1007: 'GetObjectHandles',
    0x1008: 'GetObjectInfo',
    0x1009: 'GetObject',
    0x100A: 'GetThumb',
    0x100B: 'DeleteObject',
    0x100C: 'SendObjectInfo',
    0x100D: 'SendObject',
    0x100E: 'InitiateCapture',
    0x100F: 'FormatStore',
    0x1010: 'ResetDevice',
    0x1011: 'SelfTest',
    0x1012: 'SetObjectProtection',
    0x1013: 'PowerDown',
    0x1014: 'GetDevicePropDesc',
    0x1015: 'GetDevicePropValue',
    0x1016: 'SetDevicePropValue',
    0x1017: 'ResetDevicePropValue',
    0x1018: 'TerminateOpenCapture',
    0x1019: 'MoveObject',
    0x101A: 'CopyObject',
    0x101B: 'GetPartialObject',
    0x101C: 'InitiateOpenCapture',
    0x9801: 'GetObjectPropsSupported',
    0x9802: 'GetObjectPropDesc',
    0x9803: 'GetObjectPropValue',
    0x9804: 'SetObjectPropValue',
    0x9810: 'GetObjectReferences',
    0x9811: 'SetObjectReferences',
    0x9820: 'Skip',

    # response codes
    0x2000: 'RespUndefined',
    0x2001: 'RespOk',
    0x2002: 'RespGeneralError',
    0x2003: 'RespSessionNotOpen',
    0x2004: 'RespInvalidTransactionId',
    0x2005: 'RespOperationNotSupported',
    0x2006: 'RespParameterNotSupported',
    0x2007: 'RespIncompleteTransfer',
    0x2008: 'RespInvalidStorageId',
    0x2009: 'RespInvalidObjectHandle',
    0x200A: 'RespDevicePropNotSupported',
    0x200B: 'RespInvalidObjectFormatCode',
    0x200C: 'RespStorageFull',
    0x200D: 'RespObjectWriteProtected',
    0x200E: 'RespStoreReadOnly',
    0x200F: 'RespAccessDenied',
    0x2010: 'RespNoThumbnailPresent',
    0x2011: 'RespSelfTestFailed',
    0x2012: 'RespPartialDeletion',
    0x2013: 'RespStoreNotAvailable',
    0x2014: 'RespSpecificationByFormatUnsupported',
    0x2015: 'RespNoValidObjectInfo',
    0x2016: 'RespInvalidCodeFormat',
    0x2017: 'RespUnknownVendorCode',
    0x2018: 'RespCaptureAlreadyTerminated',
    0x2019: 'RespDeviceBusy',
    0x201A: 'RespInvalidParentObject',
    0x201B: 'RespInvalidDevicePropFormat',
    0x201C: 'RespInvalidDevicePropValue',
    0x201D: 'RespInvalidParameter',
    0x201E: 'RespSessionAlreadyOpen',
    0x201F: 'RespTransactionCancelled',
    0x2020: 'RespSpecificationOfDestinationUnsupported',
    0xA801: 'RespInvalidObjectPropCode',
    0xA802: 'RespInvalidObjectPropFormat',
    0xA803: 'RespInvalidObjectPropValue',
    0xA804: 'RespInvalidObjectReference',
    0xA805: 'RespGroupNotSupported',
    0xA806: 'RespInvalidDataset',
    0xA807: 'RespSpecificationByGroupUnsupported',
    0xA808: 'RespSpecificationByDepthUnsupported',
    0xA809: 'RespObjectTooLarge',
    0xA80A: 'RespObjectPropNotSupported',
}


def parse_mtp(data):
    rest = data
    clen, ctype, ccode, tid = unpack('<IHHI', str(rest[:12]))
    rest = rest[12:]
    # trans_id = unpack('<I', str(rest[:4]))[0]
    # rest = rest[4:]
    return '%04x:%-10s:%s(%04x):%08x >> %s' % (clen, ctypes[ctype], ops.get(ccode, 'Unknown'), ccode, tid, rest.encode('hex'))


def get_total_len(data):
    return unpack('<I', str(data[:4]))[0]


def parse_file(filename):
    f = pcapy.open_offline(filename)
    count = 0
    stage = 0
    len_to_read = 0
    while 1:
        (hdr, data) = f.next()
        if not hdr:
            break
        urb_type = ord(data[8])
        ep = ord(data[10])
        if ep == 0x81 and urb_type == 0x43:
            d = 'RX'
        elif ep == 0x02 and urb_type == 0x53:
            d = 'TX'
            print('')
        else:
            continue
        payload = data[0x40:]
        if len_to_read > 0:  # data...
            print('>>> %s' % payload.encode('hex'))
            len_to_read -= len(payload)
        else:
            if len(payload) < 12:
                continue
            print('current data: %s' % payload.encode('hex'))
            print('[%s] %s' % (d, parse_mtp(payload)))
            len_to_read = get_total_len(payload) - len(payload) 
        count += 1
    print 'count: %s' % (count)


def main():
    filename = sys.argv[1]
    parse_file(filename)


if __name__ == '__main__':
    main()
