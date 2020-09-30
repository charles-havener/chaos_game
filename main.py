# Kivy Imports
import kivy
from kivy.app import App
from kivy.uix.label import Label
from kivy.uix.gridlayout import GridLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.popup import Popup
from kivy.uix.widget import Widget
from kivy.properties import ObjectProperty
from kivy.config import Config
from kivy.uix.slider import Slider
from kivy.uix.spinner import Spinner
from kivy.core.window import Window
from kivy.uix.image import Image
from kivy.uix.popup import Popup

# Non Kivy Imports
import numpy as np
import os

# From other files
from imageCreateMain import createImage

__location__ = os.path.realpath(os.path.join(
    os.getcwd(), os.path.dirname(__file__)))


class MyGrid(Widget):
    def __init__(self, **kwargs):
        super(MyGrid, self).__init__(**kwargs)

        # Sliders + Their Value Display Label
        nvLabel = ObjectProperty(None)
        nSlider = ObjectProperty(None)
        vSlider = ObjectProperty(None)

        # Spinners
        ruleSpinner = ObjectProperty(None)
        colorSpinner = ObjectProperty(None)
        reductionSpinner = ObjectProperty(None)

        # Image
        image = ObjectProperty(None)

        # Point Labels
        labelOne = ObjectProperty(None)
        labelTwo = ObjectProperty(None)
        labelThree = ObjectProperty(None)
        labelFour = ObjectProperty(None)
        labelFive = ObjectProperty(None)
        labelSix = ObjectProperty(None)
        labelSeven = ObjectProperty(None)
        labelEight = ObjectProperty(None)

        # Compressions
        cOne = ObjectProperty(None)
        cTwo = ObjectProperty(None)
        cThree = ObjectProperty(None)
        cFour = ObjectProperty(None)
        cFive = ObjectProperty(None)
        cSix = ObjectProperty(None)
        cSeven = ObjectProperty(None)
        cEight = ObjectProperty(None)

        # Rotations
        rOne = ObjectProperty(None)
        rTwo = ObjectProperty(None)
        rThree = ObjectProperty(None)
        rFour = ObjectProperty(None)
        rFive = ObjectProperty(None)
        rSix = ObjectProperty(None)
        rSeven = ObjectProperty(None)
        rEight = ObjectProperty(None)

        # Probabilities
        pOne = ObjectProperty(None)
        pTwo = ObjectProperty(None)
        pThree = ObjectProperty(None)
        pFour = ObjectProperty(None)
        pFive = ObjectProperty(None)
        pSix = ObjectProperty(None)
        pSeven = ObjectProperty(None)
        pEight = ObjectProperty(None)

        self.image.source = os.path.join(
            __location__, 'Images', 'defaultImage.png')

    # Returns the input labels and compression/rotation/probability input varibles values in a list.

    def getPointsArray(self):
        points = [[self.labelOne, self.cOne, self.rOne, self.pOne],
                  [self.labelTwo, self.cTwo, self.rTwo, self.pTwo],
                  [self.labelThree, self.cThree, self.rThree, self.pThree],
                  [self.labelFour, self.cFour, self.rFour, self.pFour],
                  [self.labelFive, self.cFive, self.rFive, self.pFive],
                  [self.labelSix, self.cSix, self.rSix, self.pSix],
                  [self.labelSeven, self.cSeven, self.rSeven, self.pSeven],
                  [self.labelEight, self.cEight, self.rEight, self.pEight]]
        return points

    # Updates the main window text with num points and verts when sliders change.

    def sliderUpdate(self, identity):
        self.nvLabel.text = f"{self.nSlider.value:,d} and {self.vSlider.value:,d} verts"
        if identity == self.vSlider:
            self.vSliderUpdate()

    # Hides/shows and enables/disables rows of inputs when number of verts changes.

    def vSliderUpdate(self):
        points = self.getPointsArray()

        for x in range(0, min(self.vSlider.value+1, 8)):
            for y in range(4):
                points[x][y].opacity = 1
                points[x][y].disabled = False

        for x in range(self.vSlider.value, 8):
            for y in range(4):
                points[x][y].opacity = 0
                points[x][y].disabled = True

    # Clears the input column(s) on button press

    def clearInputCol(self, *o):
        points = self.getPointsArray()
        for x in o:
            for i in range(8):
                points[i][x].text = ""

    # Will create an image based on current input values and selections.

    def updateImage(self, dims):

        # Number of points to draw is based on slider value, or if high quality output then on reduction method.
        if dims > 1000:
            if self.reductionSpinner.text == "Points":
                n = 250000000
            else:
                n = 15000000
        else:
            n = self.nSlider.value

        # Vertices and dropdown selections.
        numV = self.vSlider.value
        rule = "_".join(self.ruleSpinner.text.split(" ")).lower()
        redMethod = self.reductionSpinner.text
        cmap = self.colorSpinner.text.lower()

        # Compressions, rotations, and probabilities
        comp, rot, prob = [], [], []
        defaults = [2, 0, 1/numV]
        points = self.getPointsArray()
        for x in range(self.vSlider.value):
            for y in range(1, 4):
                if points[x][y].text == '':
                    points[x][y].text = str(round(defaults[y-1], 2))

            comp.append(points[x][1].text)
            rot.append(points[x][2].text)
            prob.append(points[x][3].text)

        # Creates the image
        createImage(n, numV, comp, rot, prob, rule,
                    cmap, __location__, dims, redMethod)

        # Will show the image in display unless option to create high qual output was chosen
        # in which case it output to the current directory.
        if dims <= 1000:
            self.image.source = os.path.join(__location__, f'image{dims}.png')
            self.image.reload()


class ChaosApp(App):
    def build(self):
        self.title = "Chaos Game"
        self.icon = os.path.join(__location__, 'Icon', 'icon.ico')
        return MyGrid()


if __name__ == "__main__":
    Config.set('graphics', 'resizable', 0)
    Config.write()
    Window.size = (1600, 980)
    ChaosApp().run()
