# from struct import pack, unpack
from binascii import unhexlify
from common import BaseTestCase
from mtpdevice.mtp_device_property import MtpDeviceProperty, MtpPropertyCode
from mtpdevice.mtp_data_types import UInt8, UInt16, UInt32


class MtpDevicePropertyTest(BaseTestCase):

    def testUint8PropertyDesc(self):
        expected = unhexlify('0150020000002700')
        uut = MtpDeviceProperty(MtpPropertyCode.DPC_BatteryLevel, 0, UInt8(0x27), UInt8(0))
        self.assertEqual(uut.get_desc(), expected)

    def testUint8PropertyValue(self):
        expected = unhexlify('27')
        uut = MtpDeviceProperty(MtpPropertyCode.DPC_BatteryLevel, 0, UInt8(0x27), UInt8(0))
        self.assertEqual(uut.get_value(), expected)

    def testUint16PropertyDesc(self):
        expected = unhexlify('01500400000000341200')
        uut = MtpDeviceProperty(MtpPropertyCode.DPC_BatteryLevel, 0, UInt16(0x1234), UInt16(0))
        self.assertEqual(uut.get_desc(), expected)

    def testUint16PropertyValue(self):
        expected = unhexlify('3412')
        uut = MtpDeviceProperty(MtpPropertyCode.DPC_BatteryLevel, 0, UInt16(0x1234), UInt16(0))
        self.assertEqual(uut.get_value(), expected)

    def testUint32PropertyDesc(self):
        expected = unhexlify('0150060000887766554433221100')
        uut = MtpDeviceProperty(MtpPropertyCode.DPC_BatteryLevel, 0, UInt32(0x11223344), UInt32(0x55667788))
        self.assertEqual(uut.get_desc(), expected)

    def testUint32PropertyValue(self):
        expected = unhexlify('44332211')
        uut = MtpDeviceProperty(MtpPropertyCode.DPC_BatteryLevel, 0, UInt32(0x11223344), UInt32(0x55667788))
        self.assertEqual(uut.get_value(), expected)
