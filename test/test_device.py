# *****************************************************************************
# Copyright (c) 2016 IBM Corporation and other Contributors.
#
# All rights reserved. This program and the accompanying materials
# are made available under the terms of the Eclipse Public License v1.0
# which accompanies this distribution, and is available at
# http://www.eclipse.org/legal/epl-v10.html
#
# Contributors:
#   Lokesh Haralakatta  - Initial Contribution
# *****************************************************************************

import copy

import wiotp.sdk.device
import wiotp.sdk.application
from wiotp.sdk.exceptions import ApiException
import uuid
import os
from nose.tools import *
from nose import SkipTest
import logging
import testUtils

class TestDevice(testUtils.AbstractTest):
    registeredDevice = None
    deviceClient = None
    managedClient = None

    DEVICE_TYPE = "test_device"
    DEVICE_ID = str(uuid.uuid4())
    
    @classmethod
    def setup_class(self):
        if self.DEVICE_TYPE not in self.appClient.registry.devicetypes:
            self.setupAppClient.api.registry.devicetypes.create({"id": self.DEVICE_TYPE})

        self.registeredDevice = self.appClient.registry.devices.create({"typeId": self.DEVICE_TYPE, "deviceId": self.DEVICE_ID})
        
        self.options = {
            "identity": {
                "orgId": self.ORG_ID,
                "typeId": self.registeredDevice.typeId,
                "deviceId": self.registeredDevice.deviceId
            },
            "auth": {
                "token": self.registeredDevice.authToken
            }
        }
        
        self.deviceClient = wiotp.sdk.device.DeviceClient(self.options)

        #Create default DeviceInfo Instance and associate with ManagedClient Instance
        deviceInfoObj = wiotp.sdk.device.DeviceInfo()
        deviceInfoObj.fwVersion = 0.0
        self.managedClient = wiotp.sdk.device.ManagedDeviceClient(self.options, deviceInfo=deviceInfoObj)    

    @classmethod
    def teardown_class(self):
        del self.deviceClient
        del self.managedClient
        self.appClient.registry.devices.delete({"typeId": self.DEVICE_TYPE, "deviceId": self.DEVICE_ID})


    def testDeviceClientInstance(self):
        deviceCli = wiotp.sdk.device.DeviceClient({
            "identity": {
                "orgId": self.ORG_ID,  "typeId": self.registeredDevice.typeId,  "deviceId": self.registeredDevice.deviceId
            },
            "auth": { "token": self.registeredDevice.authToken }
        })
        assert_is_instance(deviceCli , wiotp.sdk.device.DeviceClient)

    
    @SkipTest
    def testNotAuthorizedConnect(self):
        client = wiotp.sdk.device.DeviceClient({
            "identity": {
                "orgId": self.ORG_ID, "typeId": self.registeredDevice.typeId, "deviceId": self.registeredDevice.deviceId
            },
            "auth": { "token": "MGhUixxxxxxxxxxxx" }
        })
        with assert_raises(ConnectionException) as e:
            client.connect()
        assert_equals(e.exception, ConnectionException)
        assert_equals(e.exception.msg,'Not authorized')

    @SkipTest
    def testMissingMessageEncoder(self):
        with assert_raises(MissingMessageEncoderException)as e:
            myData={'name' : 'foo', 'cpu' : 60, 'mem' : 50}
            self.deviceClient.connect()
            self.deviceClient.publishEvent("missingMsgEncode", "jason", myData)
        assert_equals(e.exception, MissingMessageEncoderException)
    
    def testDeviceInfoInstance(self):
        deviceInfoObj = wiotp.sdk.device.DeviceInfo()
        assert_is_instance(deviceInfoObj, wiotp.sdk.device.DeviceInfo)
        print(deviceInfoObj)

    def testDeviceFirmwareInstance(self):
        deviceFWObj = wiotp.sdk.device.DeviceFirmware()
        assert_is_instance(deviceFWObj, wiotp.sdk.device.DeviceFirmware)
        print(deviceFWObj)
        
    def testPublishEvent(self):
        def devPublishCallback():
            print("Device Publish Event done!!!")

        myData={'name' : 'foo', 'cpu' : 60, 'mem' : 50}
        self.deviceClient.connect()
        assert_true(self.deviceClient.publishEvent("testPublishJsonEvent", "json", myData,on_publish=devPublishCallback,qos=2))
        self.deviceClient.disconnect()
    
    def testPublishEventPort1883(self):
        def devPublishCallback():
            print("Device Publish Event done!!!")

        myData={'name' : 'foo', 'cpu' : 60, 'mem' : 50}
        options = copy.deepcopy(self.options)
        options["options"] = {"mqtt": { "port": 1883 } }
        deviceClient = wiotp.sdk.device.DeviceClient(options)
        deviceClient.connect()
        assert_true(deviceClient.publishEvent("testPublishJsonEvent", "json", myData,on_publish=devPublishCallback,qos=2))
        deviceClient.disconnect()

    @SkipTest
    # Currently, port 80 only works with websockets, not tcp :/
    def testPublishEventPort80(self):
        def devPublishCallback():
            print("Device Publish Event done!!!")

        myData={'name' : 'foo', 'cpu' : 60, 'mem' : 50}
        options = copy.deepcopy(self.options)
        options["options"] = {"mqtt": { "port": 80 } }
        deviceClient = wiotp.sdk.device.DeviceClient(options)
        deviceClient.connect()
        assert_true(deviceClient.publishEvent("testPublishJsonEvent", "json", myData,on_publish=devPublishCallback,qos=2))
        deviceClient.disconnect()

    def testPublishEventPort80ws(self):
        def devPublishCallback():
            print("Device Publish Event done!!!")

        myData={'name' : 'foo', 'cpu' : 60, 'mem' : 50}
        options = copy.deepcopy(self.options)
        options["options"] = {"mqtt": { "port": 80 } }
        options["options"]["mqtt"]["transport"] = "websockets"
        deviceClient = wiotp.sdk.device.DeviceClient(options)
        deviceClient.connect()
        assert_true(deviceClient.publishEvent("testPublishJsonEvent", "json", myData,on_publish=devPublishCallback,qos=2))
        deviceClient.disconnect()

    def testPublishEventPort1883ws(self):
        def devPublishCallback():
            print("Device Publish Event done!!!")

        myData={'name' : 'foo', 'cpu' : 60, 'mem' : 50}
        options = copy.deepcopy(self.options)
        options["options"] = {"mqtt": { "port": 1883 } }
        options["options"]["mqtt"]["transport"] = "websockets"
        deviceClient = wiotp.sdk.device.DeviceClient(options)
        deviceClient.connect()
        assert_true(deviceClient.publishEvent("testPublishJsonEvent", "json", myData,on_publish=devPublishCallback,qos=2))
        deviceClient.disconnect()

    def testPublishEventPort8883(self):
        def devPublishCallback():
            print("Device Publish Event done!!!")

        myData={'name' : 'foo', 'cpu' : 60, 'mem' : 50}
        options = copy.deepcopy(self.options)
        options["options"] = {"mqtt": { "port": 8883 } }
        deviceClient = wiotp.sdk.device.DeviceClient(options)
        deviceClient.connect()
        assert_true(deviceClient.publishEvent("testPublishJsonEvent", "json", myData,on_publish=devPublishCallback,qos=2))
        deviceClient.disconnect()
    
    def testPublishEventPort8883ws(self):
        def devPublishCallback():
            print("Device Publish Event done!!!")

        myData={'name' : 'foo', 'cpu' : 60, 'mem' : 50}
        options = copy.deepcopy(self.options)
        options["options"] = {"mqtt": { "port": 8883 } }
        options["options"]["mqtt"]["transport"] = "websockets"
        deviceClient = wiotp.sdk.device.DeviceClient(options)
        deviceClient.connect()
        assert_true(deviceClient.publishEvent("testPublishJsonEvent", "json", myData,on_publish=devPublishCallback,qos=2))
        deviceClient.disconnect()


    def testPublishEventPort443(self):
        def devPublishCallback():
            print("Device Publish Event done!!!")

        myData={'name' : 'foo', 'cpu' : 60, 'mem' : 50}
        options = copy.deepcopy(self.options)
        options["options"] = {"mqtt": { "port": 443 } }
        deviceClient = wiotp.sdk.device.DeviceClient(options)
        deviceClient.connect()
        assert_true(deviceClient.publishEvent("testPublishJsonEvent", "json", myData,on_publish=devPublishCallback,qos=2))
        deviceClient.disconnect()

    def testPublishEventPort443ws(self):
        def devPublishCallback():
            print("Device Publish Event done!!!")

        myData={'name' : 'foo', 'cpu' : 60, 'mem' : 50}
        options = copy.deepcopy(self.options)
        options["options"] = {"mqtt": { "port": 443 } }
        options["options"]["mqtt"]["transport"] = "websockets"
        deviceClient = wiotp.sdk.device.DeviceClient(options)
        deviceClient.connect()
        assert_true(deviceClient.publishEvent("testPublishJsonEvent", "json", myData,on_publish=devPublishCallback,qos=2))
        deviceClient.disconnect()

    @raises(Exception)
    def testPublishEventPortInvalid(self):
        options = copy.deepcopy(self.options)
        options["options"] = {"mqtt": { "port": 100 } }
        deviceClient = wiotp.sdk.device.DeviceClient(options)
        deviceClient.connect()
        deviceClient.disconnect()
    
