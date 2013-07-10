from datetime import datetime
from collections import OrderedDict
# TODO: add to sys.modules so import is more generic
from libs.Adafruit_CharLCDPlate.Adafruit_CharLCDPlate import Adafruit_CharLCDPlate

class Adafruit_CharLCDPlate_AppEvent:
	active = False
	buttons = None
	lcd = None
	time = None

	def __init__(self, lcd, buttons):
		self.lcd = lcd
		self.buttons = buttons
		self.time = datetime.now()
		self.active = True

	def stop(self):
		self.active = False

BUTTONS = (
	Adafruit_CharLCDPlate.SELECT,
	Adafruit_CharLCDPlate.RIGHT,
	Adafruit_CharLCDPlate.DOWN,
	Adafruit_CharLCDPlate.UP,
	Adafruit_CharLCDPlate.LEFT,
	Adafruit_CharLCDPlate.LEFT
)

COLORS = (
	Adafruit_CharLCDPlate.RED,
	Adafruit_CharLCDPlate.GREEN,
	Adafruit_CharLCDPlate.YELLOW,
	Adafruit_CharLCDPlate.BLUE,
	Adafruit_CharLCDPlate.VIOLET,
	Adafruit_CharLCDPlate.TEAL,
	Adafruit_CharLCDPlate.ON
)

class Adafruit_CharLCDPlate_App:
	lastEvent = None
	lcd = None
	running = True

	def __init__(self):
		self.lcd = Adafruit_CharLCDPlate()
		self.lcd.clear()
		self.lcd.numlines = 2

	def handleEvent(self, event):
		raise NotImplementedError('handleEvent not defined')

	def stop(self):
		self.running = False
		self.lcd.stop()

	def run(self):
		self.running = True

		while self.running:
			buttonsPressed = self.lcd.buttons()

			if self.lastEvent == None:
				self.lastEvent = Adafruit_CharLCDPlate_AppEvent(self.lcd, buttonsPressed)

			if buttonsPressed != self.lastEvent.buttons:
				self.lastEvent.stop()
				self.lastEvent = Adafruit_CharLCDPlate_AppEvent(self.lcd, buttonsPressed)
				self.handleEvent(self.lastEvent)


class Adafruit_CharLCDPlate_Menu(Adafruit_CharLCDPlate_App):
	definition = None
	cursorPosition = [0]
	displayPosition = [0]

	def __init__(self, definition):
		Adafruit_CharLCDPlate_App.__init__(self)

		self.definition = definition
		self.updateDisplay()

		self.run()

	def getLine(self, position):
		def getDefinition(definition, index):
			print 'definition', definition
			print 'index', index
			return definition.items()[index]

		definition = self.definition

		print 'pos', position

		for index in position:
			if hasattr(definition, 'items'):
				definition = getDefinition(definition, index)

		return definition

	def getLines(self):
		line1 = self.getLine(self.cursorPosition)[0]
		line2 = ''

		position2 = self.cursorPosition
		if len(position2) > 0:
			position2[-1] += 1
			line2 = self.getLine(position2)[0]

		return (line1, line2)

	def handleEvent(self, event):
		if event.buttons & Adafruit_CharLCDPlate.DOWN:
			self.cursorPosition[-1] += 1

		elif event.buttons & Adafruit_CharLCDPlate.UP:
			self.cursorPosition[-1] -= 1

		self.updateDisplay()

	def updateDisplay(self):
		self.lcd.clear()

		lines = self.getLines()
		print 'lines', lines

		self.lcd.setCursor(1, 0)
		self.lcd.message(lines[0])
		self.lcd.setCursor(1, 1)
		self.lcd.message(lines[1])


class Adafruit_CharLCDPlate_MenuAction():
	lcd = None  # share with menu?

	def __init__(self):
		self.lcd = Adafruit_CharLCDPlate()


if __name__ == '__main__':
	class MenuAction_ShutDown(Adafruit_CharLCDPlate_MenuAction):
		def run(self):
			system('halt')

	class MenuAction_Restart(Adafruit_CharLCDPlate_MenuAction):
		def run(self):
			system('shutdown -r now')

	class MenuAction_Backlight(Adafruit_CharLCDPlate_MenuAction):
		color = None

		def __init__(self, color):
			Adafruit_CharLCDPlate_MenuAction.__init__(self)

			self.color = color

		def run(self):
			self.lcd.backlight(self.color)

	definition = OrderedDict({
		'Artist/Album': OrderedDict({
		}),
		'Settings': OrderedDict({
			'System': OrderedDict({	
				'Shut down': MenuAction_ShutDown(),
				'Restart': MenuAction_Restart()
			}),
			'Backlight': OrderedDict({
				'Red': MenuAction_Backlight(COLORS[0]),
				'Green': MenuAction_Backlight(COLORS[1]),
				'Yellow': MenuAction_Backlight(COLORS[2]),
				'Blue': MenuAction_Backlight(COLORS[3]),
				'Violet': MenuAction_Backlight(COLORS[4]),
				'Teal': MenuAction_Backlight(COLORS[5])
			})
		})
	})

	menu = Adafruit_CharLCDPlate_Menu(definition)
