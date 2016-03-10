from __future__ import absolute_import
from .mtp_msg import msg_from_buff, response_from_command
from .mtp_proto import ContainerTypes, ResponseCodes
from .mtp_exception import MtpProtocolException


class MtpTransaction(object):

    def __init__(self):
        self.tid = None
        self.operation = None
        self.command = None
        self.ir_data = None
        self.ri_data = None
        self.response = None


class MtpApi(object):

    STATE_WAIT_CMD = 0
    STATE_WAIT_DATA_START = 1
    STATE_WAIT_MORE_DATA = 2
    STATE_HANDLE = 3
    STATE_RESPOND = 4

    def __init__(self, device):
        self.device = device
        self.state = None
        self.transaction = None
        self.reset()

    def reset(self):
        self.state = MtpApi.STATE_WAIT_CMD
        self.transaction = MtpTransaction()

    def handle_payload(self, payload):
        messages = []
        self.process_input(payload)
        if self.state == MtpApi.STATE_HANDLE:
            self.state_handle()
        if self.state == MtpApi.STATE_RESPOND:
            if self.transaction.ri_data:
                messages.append(self.transaction.ri_data)
            messages.append(self.transaction.response.pack())
            self.reset()
        return messages

    def process_input(self, payload):
        if self.state == MtpApi.STATE_WAIT_CMD:
            self.state_wait_command(payload)
        elif self.state == MtpApi.STATE_WAIT_DATA_START:
            self.state_wait_data_start(payload)
        elif self.state == MtpApi.STATE_WAIT_MORE_DATA:
            self.state_wait_more_data(payload)
        else:
            raise Exception('in invalid state')

    def state_handle(self):
        command = self.transaction.command
        response = self.transaction.response
        ir_data = self.transaction.ir_data
        self.transaction.ri_data = self.transaction.operation.handler(self.device, command, response, ir_data)
        self.state = MtpApi.STATE_RESPOND

    def state_wait_more_data(self, payload):
        self.transaction.ir_data.data += payload
        if self.has_got_all_data():
            self.state = MtpApi.STATE_HANDLE
        else:
            self.state = MtpApi.STATE_WAIT_MORE_DATA

    def state_wait_data_start(self, payload):
        msg = msg_from_buff(payload, permissive=True)
        if msg.ctype == ContainerTypes.Data:
            self.transaction.ir_data = msg
            if msg.has_got_all_data():
                self.state = MtpApi.STATE_RESPOND
            else:
                self.state = MtpApi.STATE_WAIT_MORE_DATA
        else:
            raise MtpProtocolException('only expecting Data packet at this stage')

    def state_wait_command(self, payload):
        msg = msg_from_buff(payload)
        if msg.ctype == ContainerTypes.Command:
            self.transaction.command = msg
            self.transaction.tid = msg.tid
            self.transaction.response = response_from_command(msg, ResponseCodes.OK)
            if msg.code not in self.device.operations:
                self.transaction.response.code = ResponseCodes.OPERATION_NOT_SUPPORTED
                self.state = MtpApi.STATE_RESPOND
            else:
                self.transaction.operation = self.device.operations[msg.code]
                if self.transaction.operation.ir_data:
                    self.state = MtpApi.STATE_WAIT_DATA_START
                else:
                    self.state = MtpApi.STATE_HANDLE
        else:
            raise MtpProtocolException('only expecting Command at this stage')

