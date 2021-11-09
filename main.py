# Panda3D:	https://docs.panda3d.org/1.10/python/index

from panda3d.core import *
from direct.showbase.ShowBase import ShowBase
from direct.task import Task
from direct.gui.OnscreenImage import OnscreenImage
import lib.wiimote
import math

class MyApp(ShowBase):
	def __init__(self):
		ShowBase.__init__(self)

		#self.accept("space", self.throwWiimote)

		self.camera.setPos(0,0,-5)
		self.camera.setHpr(0,0,0)

		self.wiimote = self.loader.loadModel("resources/wiimote/wiimote.obj")
		self.wiimote.reparentTo(self.render)
		self.wiimote.setScale(20)
		self.wiimote.setPos(2,10,-0.5)
		self.wiimote.setHpr(0,0,0)
		#self.taskMgr.add(self.spinWiimote,"spinWiimote")

		self.buttonA = OnscreenImage(image="resources/glyphs/Wii_A.png")
		self.buttonA.setTransparency(TransparencyAttrib.MAlpha)
		self.buttonA.setScale(0.25)
		self.buttonA.setPos(-1.5,0,-0.7)
		self.buttonA.setColor(1,1,1,0.25)

		self.buttonB = OnscreenImage(image="resources/glyphs/Wii_B.png")
		self.buttonB.setTransparency(TransparencyAttrib.MAlpha)
		self.buttonB.setScale(0.25)
		self.buttonB.setPos(-1,0,-0.7)
		self.buttonB.setColor(1,1,1,0.25)

		self.controller = lib.wiimote.Wiimote()
		self.controller.start()
		self.controller.changeReportingMode("CoreButtonsAccelerometer")
		self.taskMgr.add(self.getData,"WiimoteFeedback")

	def spinWiimote(self, task):
		#self.wiimote.setH(task.time*100.0)
		self.wiimote.setP(task.time*100.0)
		self.wiimote.setR(task.time*100.0)
		return Task.cont

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
	app = MyApp()
	app.run()