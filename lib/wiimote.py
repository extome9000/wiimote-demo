# Credit to WiiBrew for extensive documentation on the Wii remote.  https://wiibrew.org/wiki/Wiimote
# cython-hidapi:   https://trezor.github.io/cython-hidapi/

import time
import hid

LEFT_BYTE_BINDING = {
    0: "none",
    1: "dpad_left",
    2: "dpad_right",
    4: "dpad_down",
    8: "dpad_up",
    16: "plus",
}

RIGHT_BYTE_BINDINGS = {
    0: "none",
    1: "two",
    2: "one",
    4: "b",
    8: "a",
    16: "minus",
    128: "home",
}

REPORTING_MODES = {
    "Status": 0x20,
    "ReadMemoryData": 0x21,
    "AcknowledgeOutputReportReturnFunctionResult": 0x22,
    "CoreButtons": 0x30,
    "CoreButtonsAccelerometer": 0x31,
    "CoreButtons8ExtensionBytes": 0x32,
    "CoreButtonsAccelerometer12IRBytes": 0x33,
    "CoreButtons19ExtensionBytes": 0x34,
    "CoreButtonsAccelerometer16ExtensionBytes": 0x35,
    "CoreButtons10IRBytes9ExtensionBytes": 0x36,
    "CoreButtonsAccelerometer10IRBytes6ExtensionBytes": 0x37,
    "21ExtensionBytes": 0x3D,
    "InterleavedCoreButtonsAccelerometer36IRBytes": 0x3E,
}

LEDS = {
    1: 0x10,
    2: 0x20,
    3: 0x40,
    4: 0x80,
}


class Wiimote:
    def __init__(self) -> None:
        # VID and PID are assigned by the USB Implementers Forum, so they should be static.
        self.vendorID = 1406
        self.productID = 774
        self.device = hid.device()
        self.connected = False

    def start(self) -> bool:
        try:
            self.device.open(vendor_id=self.vendorID, product_id=self.productID)
            self.device.set_nonblocking(1)
            #print("Manufacturer: %s" % self.device.get_manufacturer_string())
            #print("Product: %s" % self.device.get_product_string())
            #print("Serial No: %s" % self.device.get_serial_number_string())
            print("Successfully connected.")
            self.connected = True
            self.changeLED(1)
        except IOError:
            raise ValueError
            self.connected = False

    def feedback(self):
        return self.device.read(max_length=64, timeout_ms=0)

    def changeReportingMode(self, reportingMode: str) -> None:
        if reportingMode not in REPORTING_MODES:
            print("Wiimote.changeReportingMode(): Reporting mode given is not valid.")
            return None
        if not self.connected:
            print("Wiimote.changeReportingMode(): Wiimote is not connected.")
            return None

        self.device.write([0x12,0x00,REPORTING_MODES[reportingMode]])

    def changeLED(self, pos: int) -> None:
        if self.connected:
            try:
                self.device.write([0x11,LEDS[pos]])
            except ValueError:
                print("Wiimote.changeLED(): Wiimote is not connected.")
            except IndexError:
                print("Wiimote.changeLED(): Invalid position given.")
        else:
            print("Wiimote.changeLED(): Wiimote is not connected.")

    def rumble(self, duration: int) -> None:
        if self.connected:
            try:
                self.device.write([0x10,0x01])
                time.sleep(duration)
                self.device.write([0x10,0x00])
            except ValueError:
                print("Wiimote.rumble(): Wiimote is not connected.")
        else:
            print("Wiimote.rumble(): Wiimote is not connected.")

    def getStatus(self) -> None:
        self.device.write([0x15,0x00])