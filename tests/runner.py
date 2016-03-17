#!/usr/bin/env python
import os
import unittest
from mtp_device_tests import *
from mtp_api_tests import *
from mtp_msg_tests import *
from mtp_property_tests import *
from mtp_object_tests import *


if __name__ == '__main__':
    if not os.path.exists('logs'):
        os.mkdir('logs')
    unittest.main()
