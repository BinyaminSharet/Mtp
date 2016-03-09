class MtpProtocolException(Exception):

    def __init__(self, response, msg=None):
        super(MtpProtocolException, self).__init__(msg)
        self.response = response
