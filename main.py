# Panda3D:	https://docs.panda3d.org/1.10/python/index

from panda3d.core import *
from direct.showbase.ShowBase import ShowBase
from direct.task import Task
from direct.gui.OnscreenImage import OnscreenImage
import lib.wiimote
import math

GLYPH_PATH = "resources/glyphs/"


class ButtonVisual(OnscreenImage):
	def __init__(self, image: str, pos: tuple, scale: int) -> None:
		super().__init__(image=GLYPH_PATH+image+".png")
		self.setTransparency(TransparencyAttrib.MAlpha)
		self.setPos(pos[0],pos[1],pos[2])
		self.setScale(scale)
		self.setColor(1,1,1,0.25)


class Stack:
	def __init__(self, stackMax: int) -> None:
		self.stack = [0] * stackMax
		self.stackMax = stackMax

	def add(self, item: float) -> None:
		self.stack.pop()
		self.stack.insert(0,item)

	def getAvg(self) -> float:
		return sum(self.stack) / self.stackMax


class App(ShowBase):
	def __init__(self) -> None:
		super().__init__(self)

		self.camera.setPos(0,0,-5)
		self.camera.setHpr(0,0,0)

		self.wiimote = self.loader.loadModel("resources/wiimote/wiimote.obj")
		self.wiimote.reparentTo(self.render)
		self.wiimote.setScale(20)
		self.wiimote.setPos(2,10,-0.5)
		self.wiimote.setHpr(0,0,0)

		self.buttonA = ButtonVisual(image="Wii_A",pos=(-1.5,0,0.1),scale=0.25)
		self.buttonB = ButtonVisual(image="Wii_B",pos=(-1,0,0.1),scale=0.25)
		self.buttonMinus = ButtonVisual(image="Wii_Minus",pos=(-1.55,0,-0.3),scale=0.175)
		self.buttonHome = ButtonVisual(image="Wii_Home",pos=(-1.25,0,-0.3),scale=0.175)
		self.buttonPlus = ButtonVisual(image="Wii_Plus",pos=(-0.95,0,-0.3),scale=0.175)
		self.buttonOne = ButtonVisual(image="Wii_1",pos=(-1.5,0,-0.7),scale=0.25)
		self.buttonTwo = ButtonVisual(image="Wii_2",pos=(-1,0,-0.7),scale=0.25)
		self.buttonDpad = ButtonVisual(image="Wii_Dpad",pos=(-1.25,0,0.65),scale=0.33)
		
		self.buttonList = {
			"r1": self.buttonTwo,
			"r2": self.buttonOne,
			"r4": self.buttonB,
			"r8": self.buttonA,
			"r16": self.buttonMinus,
			"l16": self.buttonPlus,
			"r128": self.buttonHome,
		}

		try:
			self.controller = lib.wiimote.Wiimote()
			self.controller.start()
			self.controller.changeReportingMode("CoreButtonsAccelerometer")
			self.rStack = Stack(stackMax=15)
			self.pStack = Stack(stackMax=15)
			self.taskMgr.add(self.getData,"WiimoteFeedback")
		except ValueError:
			self.buttonDisconnected = ButtonVisual(image="Controller_Disconnected",pos=(0,0,0),scale=0.5)

	def getData(self, task):
		data = self.controller.feedback()
		if data:
			l,r = data[1] & 159, data[2] & 159 # Bit mask over LSBs (0b10011111)
			print(l,r)
			if f"r{r}" in self.buttonList: self.buttonList[f"r{r}"].setColor(1,1,1,1)
			if f"l{l}" in self.buttonList: self.buttonList[f"l{l}"].setColor(1,1,1,1)

			# yore ugleh
			if l == 1:
				self.buttonDpad.setImage("resources/glyphs/Wii_Dpad_Left.png")
				self.buttonDpad.setTransparency(TransparencyAttrib.MAlpha)
				self.buttonDpad.setColor(1,1,1,1)
			if l == 2:
				self.buttonDpad.setImage("resources/glyphs/Wii_Dpad_Right.png")
				self.buttonDpad.setTransparency(TransparencyAttrib.MAlpha)
				self.buttonDpad.setColor(1,1,1,1)
			if l == 4:
				self.buttonDpad.setImage("resources/glyphs/Wii_Dpad_Down.png")
				self.buttonDpad.setTransparency(TransparencyAttrib.MAlpha)
				self.buttonDpad.setColor(1,1,1,1)
			if l == 8:
				self.buttonDpad.setImage("resources/glyphs/Wii_Dpad_Up.png")
				self.buttonDpad.setTransparency(TransparencyAttrib.MAlpha)
				self.buttonDpad.setColor(1,1,1,1)

			if r == 0:
				for b in self.buttonList.items():
					if b[0][0] == "r":
						b[1].setColor(1,1,1,0.25)
			if l == 0:
				for b in self.buttonList.items():
					if b[0][0] == "l":
						b[1].setColor(1,1,1,0.25)
				self.buttonDpad.setImage("resources/glyphs/Wii_Dpad.png")
				self.buttonDpad.setTransparency(TransparencyAttrib.MAlpha)
				self.buttonDpad.setColor(1,1,1,0.25)

			# Accelerometer data is 0 degrees at 0x80, so have to subtract 128 (which is 0x80).
			x, y, z = data[3]-128, data[4]-128, data[5]-128
			r = math.atan2(y,z) * (180/math.pi) + 90
			p = math.atan2(-x,math.sqrt(y*y + z*z)) * (180/math.pi)
			# Yaw is impossible to calculate without a gyroscope or compass.

			self.rStack.add(r)
			self.pStack.add(p)

			rAvg = self.rStack.getAvg()
			pAvg = self.pStack.getAvg()

			self.wiimote.setHpr(180,rAvg,pAvg)

		return Task.cont

if __name__ == "__main__":
	loadPrcFile("cfg.prc")
	app = App()
	app.run()
