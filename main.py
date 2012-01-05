
import kivy
kivy.require('1.0.8')


from random import random,choice,randint,shuffle
from kivy.app import App
from kivy.clock import Clock
from kivy.uix.widget import Widget
from kivy.uix.image import Image
from kivy.uix.button import Button
from kivy.core.audio import SoundLoader
from kivy.uix.gridlayout import GridLayout
from kivy.animation import Animation
from kivy.properties import StringProperty, ObjectProperty
from glob import glob
from os.path import dirname, join, basename

def flatten(l):
    return [item for sublist in l for item in sublist]

class MemoryButton(Button):
    done=False
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
        #if self.icon is None:
        #    self.icon = Image(source=value)
        if self.background_normal is None:
            self.background_normal=value
            self.background = value
            
    def on_press(self):
        if self.parent.state=='OK' and not self.done:
            # stop the sound if it's currently playing
            #if self.sound.status != 'stop':
            #    self.sound.stop()
            #self.sound.play()
            
            if self.parent.first is None:
                self.parent.first = self
                self.background_down,self.background_normal = self.background_normal,self.background_down
            else:
                if self is self.parent.first:
                    #self.background_down,self.background_normal = self.background_normal,self.background_down
                    self.parent.first==None
                elif self.parent.first.filenameIcon == self.filenameIcon:
                    print "youhou!!"
                    self.background_down,self.background_normal = self.background,self.background
                    self.parent.first.background_down,self.parent.first.background_normal = self.parent.first.background,self.parent.first.background
                    self.done=True
                    self.parent.first.done=True
                    self.parent.first = None
                    
                else:
                     self.parent.first.background_down,self.parent.first.background_normal = self.parent.first.background_normal,self.parent.first.background_down
                     self.parent.first =None

class MemoryLayout(GridLayout):
    def __init__(self, **kwargs):
        super(MemoryLayout, self).__init__(**kwargs)
        self.state = ""
        self.first=None

    def my_callback(self,dt):
        #everything loaded
        Clock.schedule_once(self.hideButtons, 2)

    def hideButtons(self,dt):
        for i in self.children:
            i.background_down,i.background_normal = i.background_normal,i.background_down
        self.state="OK"


    
def loadData():
    sounds={}
    icons=[]#{}
    for s in glob(join(dirname(__file__),"sounds", '*.wav')):
        name=basename(s[:-4]).split("_")[0]
        if sounds.has_key(name):
            sounds[name].append(s)
        else:
            sounds[name]=[s]

    for i in glob(join(dirname(__file__),"icons", '*.gif')):
        icons.append(i)
        #name=basename(i[:-4]).split("_")[0]
        #if icons.has_key(name):
        #    icons[name].append(i)
        #else:
        #    icons[name]=[i]
    #print sounds
    #print icons
    return sounds,icons

class MyAnimalsApp(App):

    def build(self):
        sounds,icons=loadData()
        
        g = MemoryLayout(cols=6,)
        """print root.size
        for i in sounds:
            for j in sounds[i]:
                anIcon = choice(icons[i])
                btn = AudioButton(
                    text="",#i,
                    filenameSound=j,
                    filenameIcon=anIcon,
                    size_hint=(None, None), halign='center',
                    pos_hint={'x':random()*0.8,'y':random()*0.8},
                    size=(128,128), text_size=(118, None)
                    )
                root.add_widget(btn)
                """
        icons=icons+icons
        shuffle(icons)
        for i in icons:
            aSound = choice(sounds[i.split("_")[0].split('/')[1]])
            
            btn = MemoryButton(
                text="",#i,
                filenameIcon=i,
                filenameSound=aSound,
                #size=(128,128), text_size=(118, None)
                )
            
            g.add_widget(btn)

        Clock.schedule_once(g.my_callback, 0)
        return g
        #return root

if __name__ in ('__main__', '__android__'):
    MyAnimalsApp().run()
