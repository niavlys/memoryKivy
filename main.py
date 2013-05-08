"""
Copyright (c) 2012, Sylvain Alborini
All rights reserved.

Redistribution and use in source and binary forms, with or without modification, are permitted provided that the following conditions are met:

    Redistributions of source code must retain the above copyright notice, this list of conditions and the following disclaimer.
    Redistributions in binary form must reproduce the above copyright notice, this list of conditions and the following disclaimer in the documentation and/or other materials provided with the distribution.

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
"""

import kivy
kivy.require('1.0.9')
from kivy.app import App
from kivy.clock import Clock
from kivy.uix.widget import Widget
from kivy.uix.image import Image
from kivy.uix.button import Button
from kivy.uix.popup import Popup
from kivy.uix.label import Label
from kivy.uix.slider import Slider
from kivy.uix.scatter import Scatter
from kivy.uix.togglebutton import ToggleButton
from kivy.core.audio import SoundLoader
from kivy.uix.gridlayout import GridLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.animation import Animation
from kivy.properties import StringProperty, ObjectProperty,NumericProperty
from kivy.uix.progressbar import ProgressBar
from random import choice,shuffle
from glob import glob
from os.path import dirname, join, basename,sep

DEFAULT_SHOWTIME = 10
DEFAULT_NBITEMS = 12
MAX_NBITEMS = None


def bestRatio(nb,width,height):
    row=1
    correctRatio=1.
    minErr=None
    nbparrow = nb/row
    if nb%row !=0:
        nbparrow+=1
    x = float(width)/nbparrow
    y = float(height)/row
    ratio=x/y
    minErr=abs(ratio-correctRatio)
    while ratio<correctRatio:
        row+=1
        nbparrow = nb/row
        if nb%row !=0:
            nbparrow+=1
        x = float(width)/nbparrow
        y = float(height)/row
        ratio=x/y
        if abs(ratio-correctRatio)>minErr:
            row-=1
        minErr = abs(ratio-correctRatio)
    return row

class MemoryButton(Button):
    done=False
    playsound=True
    filenameSound = StringProperty(None)
    filenameIcon = StringProperty(None)
    sound = ObjectProperty(None)
    background = ObjectProperty(None)
    background_hide = ObjectProperty(None)
    #background_down = ObjectProperty(None)
    background_normal = ObjectProperty(None)

    def on_filenameSound(self, instance, value):
        # the first time that the filename is set, we are loading the sample
        if self.sound is None:
            self.sound = SoundLoader.load(value)
    
    def on_filenameIcon(self, instance, value):
        # the first time that the filename is set, we are loading the sample
        if self.background_normal is None:
            self.background_normal=value
            self.background = value
            self.background_hide = self.background_down
            
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
                    #check termination
                    if self.parent.left == self.parent.items:
                        self.parent.gameOver()
                        Clock.unschedule(self.parent.elapsedTime)

                else:
                    self.parent.missed += 1
                    self.parent.first.background_down,self.parent.first.background_normal = self.parent.first.background_normal,self.parent.first.background_down
                    self.parent.first =None

class MemoryLayout(GridLayout):
    left = NumericProperty(0)   #left items to find
    items = NumericProperty(0)  #total number of items
    level = NumericProperty(0)  #seconds to count down
    countdown = NumericProperty(0)
    missed = NumericProperty(0) # number of missed items
    elapsed = NumericProperty(0)

    def __init__(self, **kwargs):
        super(MemoryLayout, self).__init__(**kwargs)
        self.state = ""
        self.first=None
        self.level=kwargs["level"]
        self.items=kwargs["items"]
        self.countdown= self.level

    def toggleButtons(self,state):
        for i in self.children:
            i.background_down,i.background_normal = i.background_normal,i.background_down
        self.state=state 

    def hideButtons(self):
        for i in self.children:
            i.done=False
            i.background_down,i.background_normal = i.background_hide,i.background_hide
            
    def showButtons(self):
        for i in self.children:
            i.background_normal = i.background
            
    def elapsedTime(self,dt):
        self.elapsed += dt
        
    def initialCountdown(self,dt):
        if self.countdown == -1:
            Clock.unschedule(self.initialCountdown)
            self.toggleButtons("OK")
            Clock.schedule_interval(self.elapsedTime,0.1)
        else:
            if not hasattr(self.parent.parent,'countdown'):
                self.parent.parent.countdown=Label(text="")
                self.parent.parent.add_widget(self.parent.parent.countdown)
            popup=self.parent.parent.countdown
            popup.text=''
            popup.font_size=12
            popup.color=(0,0,0,1)
            popup.text=str(self.countdown)
            Animation(color=(1,1,1,0),font_size=150).start(popup)
            self.countdown -= 1

    def resetTime(self,instance,newLevel):
        self.level=int(newLevel)

    def resetNbItem(self,instance,newNb):
        self.items = int(newNb)

    def reset(self):
        self.countdown = self.level
        self.first = None
        self.left = 0
        self.elapsed = 0
        self.missed = 0
        self.hideButtons()
        self.state = ''
        self.updateNbItems()
 
    def restartGame(self,inst):
        self.reset()
        self.showButtons()
        Clock.schedule_interval(self.initialCountdown,1)

    def updateNbItems(self):
        if self.items != len(self.children):
            #update self.rows to keep acceptable ratio
            newRow = bestRatio(self.items*2,self.width,self.height)

            self.clear_widgets()
            self.rows=newRow
            shuffle(icons)
            iicons=icons[:self.items]
            iicons=iicons+iicons
            shuffle(iicons)
            for i in iicons:
                s = i.split(".png")[0].split(sep)[1]
                if sounds.has_key(s):
                    aSound = choice(sounds[s])
                else:
                    aSound = sounds['default'][0]

                btn = MemoryButton(
                    text="",
                    filenameIcon=i,
                    filenameSound=aSound,
                    )  
                self.add_widget(btn)
        else:
            shuffle(self.children)

        
    def gameOver(self):
        # calculate score
        score = 100./self.level + 100.*self.items - 10.*self.missed + 100./self.elapsed
        print "done!",score

        content2 = BoxLayout(orientation='vertical',spacing=10)
        #content.add_widget(Label(text='score: %d'%int(score)))
        content = BoxLayout(orientation='vertical',size_hint_y=.7)
        #change show time
        labelSlider = LabelTimeSlider(text='Initial Show time: %s s'%self.level)
        content.add_widget(labelSlider)
        newLevel = Slider(min=1, max=30, value=self.level)
        content.add_widget(newLevel)
        newLevel.bind(value = labelSlider.update)
        newLevel.bind(value = self.resetTime) 


        #change number of items
        labelNb = LabelNb(text='Number of items: %s'%self.items)
        content.add_widget(labelNb)
        nb_items = Slider(min=5, max = MAX_NBITEMS, value = self.items )
        content.add_widget(nb_items)
        nb_items.bind(value = labelNb.update)
        nb_items.bind(value = self.resetNbItem)
       
        content2.add_widget(content)

        replay = Button(text='Replay!')
        credits = Button(text='Credits')
        action = BoxLayout(orientation='horizontal',size_hint_y=.3)
        action.add_widget(replay)
        action.add_widget(credits)
        content2.add_widget(action)


        popup = PopupGameOver(title='Congratulations! your score: %d'%int(score),
                              content=content2,
                              size_hint=(0.5, 0.5),pos_hint={'x':0.25, 'y':0.25},
                              auto_dismiss=False)
        replay.bind(on_press=popup.replay)
        replay.bind(on_press=self.restartGame)
        credits.bind(on_press=popup.credits)
        popup.open()

class PopupGameOver(Popup):
     def replay(self,inst):
         self.dismiss()
     
     def credits(self,inst):
         f=open("credits",'r')
         c=Label(text=f.read(), text_size=(self.parent.width-20, None),size_hint=(1,.9),shorten=True) 
         f.close()
         content = BoxLayout(orientation='vertical')
         close = Button(text='Close',size_hint=(1,.1))
         content.add_widget(c)
         content.add_widget(close)
         #root = ScrollView(size_hint=(None, None), size=(400, 400))
         #root.add_widget(content)
         
         popup = Popup(title='Credits:',
                       #content=root, auto_dismiss=False
                       content=content, auto_dismiss=False
                       ) 
         close.bind(on_press=popup.dismiss)
         popup.open()

class LabelTimeSlider(Label):
    def update(self,instance,value):
        self.text="Initial Show time: %d s"%int(value)

class LabelNb(Label):
    def update(self,instance,value):
        self.text="Number of items: %d"%int(value)

class MyPb(ProgressBar):
    def foundAnItem(self,instance,value):
        self.value = value

    def newNbItems(self,instance,value):
        self.value = value
        self.max = value
    

class LabelScore(Label):
    def updateTime(self,instance,value):
        self.text="Time: %0.2f s"%value

class LabelMissed(Label):
    def update(self,instance,value):
        self.text="Missed: %d"%value

def loadData():
    sounds={}
    icons=[]
    for s in glob(join(dirname(__file__),"sounds", '*.wav')):
        name=basename(s[:-4]).split("_")[0]
        if sounds.has_key(name):
            sounds[name].append(s)
        else:
            sounds[name]=[s]
    for i in glob(join(dirname(__file__),"icons", '*.png')):
        icons.append(i)
    return sounds,icons

def showmissingSounds():
    missing=[]
    for i in icons:
        s = i.split(".png")[0].split(sep)[1]
        if not sounds.has_key(s):
            missing.append(s)
    print "missing sounds for %d animals: %s"%(len(missing),missing)
 

class MyAnimalsApp(App):

    def build(self):
        global sounds,icons
        sounds,icons=loadData()
        #showmissingSounds()
        show = DEFAULT_SHOWTIME
        global MAX_NBITEMS
        MAX_NBITEMS = len(icons)
        g = MemoryLayout(rows=4,items = DEFAULT_NBITEMS, level=show,size_hint=(1,.9))
        config = BoxLayout(orientation='horizontal',spacing=10, size_hint=(1,.1))
        
        sound = ToggleButton(text='Sound On', size_hint=(0.1,1))
        sound.bind(on_press=MemoryButton.toggleSound)

        pb = MyPb(max=DEFAULT_NBITEMS, size_hint=(0.7,1),ml=g)
        
        score = LabelScore(text="Time:  0 s",size_hint=(0.1,1))
        missed =  LabelMissed(text="Missed:  0",size_hint=(0.1,1))
        
        config.add_widget(pb)
        config.add_widget(score)
        config.add_widget(missed)
        config.add_widget(sound)
        
        g.bind(missed=missed.update)     
        g.bind(elapsed=score.updateTime)        
        g.bind(left=pb.foundAnItem)
        g.bind(items=pb.newNbItems)

        playZone = BoxLayout(orientation='vertical')
        playZone.add_widget(g)
        playZone.add_widget(config)
        #select DEFAULT_NBITEMS
        shuffle(icons)
        iicons=icons[:DEFAULT_NBITEMS]

        iicons=iicons+iicons
        shuffle(iicons)
        for i in iicons:
            s = i.split(".png")[0].split(sep)[1]
            if sounds.has_key(s):
                aSound = choice(sounds[s])
            else:
                aSound = sounds['default'][0]

            btn = MemoryButton(
                text="",
                filenameIcon=i,
                filenameSound=aSound,
                )  
            g.add_widget(btn)

        root=FloatLayout()
        root.add_widget(Image(source='Jungle_Background_-_by-vectorjungle.jpg',allow_stretch=True,keep_ratio=False))
        root.add_widget(playZone)
        Clock.schedule_interval(g.initialCountdown,1)
        return root

if __name__ in ('__main__', '__android__'):
    MyAnimalsApp().run()
