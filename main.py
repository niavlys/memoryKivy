
import kivy
kivy.require('1.0.9')
from kivy.app import App
from kivy.clock import Clock
from kivy.uix.widget import Widget
from kivy.uix.image import Image
from kivy.uix.button import Button
from kivy.uix.popup import Popup
from kivy.uix.label import Label
from kivy.uix.togglebutton import ToggleButton
from kivy.core.audio import SoundLoader
from kivy.uix.gridlayout import GridLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.animation import Animation
from kivy.properties import StringProperty, ObjectProperty,NumericProperty
from kivy.uix.progressbar import ProgressBar
from random import choice,shuffle
from glob import glob
from os.path import dirname, join, basename


class MemoryButton(Button):
    done=False
    playsound=True
    filenameSound = StringProperty(None)
    filenameIcon = StringProperty(None)
    sound = ObjectProperty(None)
    background_normal = ObjectProperty(None)
    background = ObjectProperty(None)
    
 
    def on_filenameSound(self, instance, value):
        # the first time that the filename is set, we are loading the sample
        if self.sound is None:
            self.sound = SoundLoader.load(value)
    
    def on_filenameIcon(self, instance, value):
        # the first time that the filename is set, we are loading the sample
        if self.background_normal is None:
            self.background_normal=value
            self.background = value
   
    @classmethod
    def toggleSound(cls,instance):
        instance.text = ["Sound On" if instance.state == 'normal' else "Sound Off"][0]
        cls.playsound = instance.state == 'normal'

    def on_press(self):
        if self.parent.state=='OK' and not self.done: 
            if self.parent.first is None:
                self.parent.first = self
                self.background_down,self.background_normal = self.background_normal,self.background_down
            else:
                if self is self.parent.first:
                    self.parent.first==None
                elif self.parent.first.filenameIcon == self.filenameIcon:
                    print "youhou!!"
                    self.parent.left+=1
                    if self.playsound:
                        if self.sound.status != 'stop':
                            self.sound.stop()
                        self.sound.play()

                    self.background_down,self.background_normal = self.background,self.background
                    self.parent.first.background_down,self.parent.first.background_normal = self.parent.first.background,self.parent.first.background
                    self.done=True
                    self.parent.first.done=True
                    self.parent.first = None
                    
                else:
                     self.parent.first.background_down,self.parent.first.background_normal = self.parent.first.background_normal,self.parent.first.background_down
                     self.parent.first =None

class MemoryLayout(GridLayout):
    left = NumericProperty(0)   #left items to find
    items = NumericProperty(0)  #total number of items
    level = NumericProperty(0)  #seconds to count down
    countdown = NumericProperty(0)

    def __init__(self, **kwargs):
        super(MemoryLayout, self).__init__(**kwargs)
        self.state = ""
        self.first=None
        self.level=kwargs["level"]
        self.items=self.cols*2
        self.countdown= self.level

    def hideButtons(self):
        for i in self.children:
            i.background_down,i.background_normal = i.background_normal,i.background_down
        self.state="OK"

    def initialCountdown(self,dt):
        if self.countdown == -1:
            Clock.unschedule(self.initialCountdown)
            self.hideButtons()
        else:
            popup=Label(text=str(self.countdown))
            self.parent.parent.add_widget(popup)
            Animation(color=(1,1,1,0),font_size=150).start(popup)
            self.countdown -= 1

class MyPb(ProgressBar):
    def __init__(self, **kwargs):
        super(ProgressBar, self).__init__(**kwargs)
        self.ml = kwargs['ml']
    
    def foundAnItem(self,instance,value):
        print self.max,self.value
        self.value += 100*self.ml.level
        if self.value==self.max:
            print "done!"
        #popup = Popup(title='Test popup',
        #              content=Label(text='Hello world'),
        #              size_hint=(None, None),pos_hint={"x":0.5,"y":0.5}, size=(400, 400),)
        #popup=Label(text='Hello world')
        #self.parent.parent.parent.add_widget(popup)
        #Animation(color=(1,1,1,0),font_size=100).start(popup)


def loadData():
    sounds={}
    icons=[]
    for s in glob(join(dirname(__file__),"sounds", '*.wav')):
        name=basename(s[:-4]).split("_")[0]
        if sounds.has_key(name):
            sounds[name].append(s)
        else:
            sounds[name]=[s]
    for i in glob(join(dirname(__file__),"icons", '*.gif')):
        icons.append(i)
    return sounds,icons

class MyAnimalsApp(App):

    def build(self):
        sounds,icons=loadData()
        show=10
        g = MemoryLayout(cols=len(icons)/2, level=show,size_hint=(1,.9))
        config = BoxLayout(orientation='horizontal', size_hint=(1,.1))
        sound = ToggleButton(text='Sound On', size_hint=(0.1,1))
        sound.bind(on_press=MemoryButton.toggleSound)
        pb = MyPb(max=len(icons)*100*show, size_hint=(0.9,1),ml=g)
        config.add_widget(pb)
        config.add_widget(sound)
        g.bind(left=pb.foundAnItem)

        root = BoxLayout(orientation='vertical')
        root.add_widget(g)
        root.add_widget(config)
        icons=icons+icons
        shuffle(icons)
        for i in icons:
            aSound = choice(sounds[i.split("_")[0].split('/')[1]])
            btn = MemoryButton(
                text="",
                filenameIcon=i,
                filenameSound=aSound,
                )  
            g.add_widget(btn)

        #Clock.schedule_interval(pb.updatePB,0.1)
        
        #return g
        f=FloatLayout()
        f.add_widget(root)
        #return root
        Clock.schedule_interval(g.initialCountdown,1)
        return f

if __name__ in ('__main__', '__android__'):
    MyAnimalsApp().run()
