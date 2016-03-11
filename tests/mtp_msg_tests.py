from common import BaseTestCase
from struct import pack
from binascii import unhexlify
from mtpdevice.mtp_proto import ContainerTypes, ResponseCodes
from mtpdevice.mtp_exception import MtpProtocolException
from mtpdevice.mtp_msg import msg_from_buff


class CommandMessageTest(BaseTestCase):

    def buildVanillabuffer(self, code, tid, params):
        length = len(params) * 4 + 0xc
        ctype = ContainerTypes.Command
        buff = pack('<IHHI', length, ctype, code, tid)
        for param in params:
            buff += pack('<I', param)
        return buff

    def vanillaTest(self, code, tid, params):
        buff = self.buildVanillabuffer(code, tid, params)
        command_message = msg_from_buff(buff)
        self.assertEqual(command_message.code, code)
        self.assertEqual(command_message.tid, tid)
        self.assertEqual(command_message.params, params)
        self.assertEqual(command_message.num_params(), len(params))
        for i in range(len(params)):
            self.assertEqual(command_message.get_param(i), params[i])
        for i in range(len(params), len(params) + 5):
            self.assertIsNone(command_message.get_param(i))

    def testCorrectValuesFromBufferNoParams(self):
        self.vanillaTest(1, 2, [])

    def testCorrectValuesFromBufferSingleParam(self):
        self.vanillaTest(1, 2, [0x12345678])

    def testCorrectValuesFromBufferMultipleParams(self):
        self.vanillaTest(1, 2, [0x01020304, 0x11121314, 0x21222324, 0x31323334, 0x41424344])

    def invalidBufferTest(self, buff, expected_response=ResponseCodes.INVALID_CODE_FORMAT):
        with self.assertRaises(MtpProtocolException) as cm:
            msg_from_buff(buff)
        if expected_response is not None:
            self.assertEqual(cm.exception.response, expected_response)

    def testInvalidLengthTooLongNoParams(self):
        buff = unhexlify('100000000100010002000000')
        self.invalidBufferTest(buff)

    def testInvalidLengthTooShortNoParams(self):
        buff = unhexlify('080000000100010002000000')
        self.invalidBufferTest(buff)

    def testInvalidLengthTooLongWithParams(self):
        buff = unhexlify('14000000010001000200000011111111')
        self.invalidBufferTest(buff)

    def testInvalidLengthTooShortWithParams(self):
        buff = unhexlify('0c000000010001000200000011111111')
        self.invalidBufferTest(buff)

    def testInvalidLengthNotMultipleOfFour(self):
        buff = unhexlify('0d0000000100010002000000ff')
        self.invalidBufferTest(buff)

    def testInvalidRequestTooshort(self):
        buff = unhexlify('0800000001000100')
        self.invalidBufferTest(buff)
