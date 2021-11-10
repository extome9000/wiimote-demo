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


class App(ShowBase):
	def __init__(self):
		super().__init__(self)

		#self.accept("space", self.throwWiimote)

		self.camera.setPos(0,0,-5)
		self.camera.setHpr(0,0,0)

		self.wiimote = self.loader.loadModel("resources/wiimote/wiimote.obj")
		self.wiimote.reparentTo(self.render)
		self.wiimote.setScale(20)
		self.wiimote.setPos(2,10,-0.5)
		self.wiimote.setHpr(0,0,0)

		self.buttonA = ButtonVisual(image="Wii_A",pos=(-1.5,0,-0.7),scale=0.25)
		self.buttonB = ButtonVisual(image="Wii_B",pos=(-1,0,-0.7),scale=0.25)
		self.buttonMinus = ButtonVisual(image="Wii_Minus",pos=(-1.6,0,-0.3),scale=0.175)
		self.buttonPlus = ButtonVisual(image="Wii_Plus",pos=(-1.3,0,-0.3),scale=0.175)
		self.buttonHome = ButtonVisual(image="Wii_Home",pos=(-1,0,-0.3),scale=0.175)

		try:
			self.controller = lib.wiimote.Wiimote()
			self.controller.start()
			self.controller.changeReportingMode("CoreButtonsAccelerometer")
			self.taskMgr.add(self.getData,"WiimoteFeedback")
		except ValueError:
			self.buttonDisconnected = ButtonVisual(image="Controller_Disconnected",pos=(0,0,0),scale=0.5)

	def getData(self, task):
		data = self.controller.feedback()
		if data:
			if data[0] == 0x31:
				x, y, z = data[3]-128, data[4]-128, data[5]-128
				r = math.atan2(y,z) * (180/math.pi) + 90
				p = math.atan2(-x,math.sqrt(y*y + z*z)) * (180/math.pi)
				# Yaw is impossible to calculate without a gyroscope or compass.
				self.wiimote.setHpr(180,r,p)
		return Task.cont

if __name__ == "__main__":
	loadPrcFile("cfg.prc")
	app = App()
	app.run()
