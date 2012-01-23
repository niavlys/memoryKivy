
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

DEFAULT_SHOWTIME = 10

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
        self.items=self.cols*2
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
            popup=Label(text=str(self.countdown))
            self.parent.parent.add_widget(popup)
            Animation(color=(1,1,1,0),font_size=150).start(popup)
            self.countdown -= 1

    def reloadGame(self,instance,newLevel):
        self.reset(newLevel)
        
    def reset(self,newLevel):
        self.level=int(newLevel)
        #shuffle buttons
        if self.state =='OK':
            self.first=None
            self.countdown= self.level
            self.elapsed=0
            self.missed = 0
            self.hideButtons()
            self.state = ''
            shuffle(self.children)
 
    def restartGame(self,inst):
        self.showButtons()
        Clock.schedule_interval(self.initialCountdown,1)

        
    def gameOver(self):
        
        # calculate score
        score = 100./self.level + 100.*self.items + 100.*self.missed + 100./self.elapsed
        print "done!",score

        content = BoxLayout(orientation='vertical')
        content.add_widget(Label(text='score: %d'%int(score)))
        
        content.add_widget(Label(text='Initial Show time:'))
        newLevel=Slider(min=0, max=30, value=DEFAULT_SHOWTIME)
        
        content.add_widget(newLevel)
        
        newLevel.bind(value=self.reloadGame)
        self.reset(DEFAULT_SHOWTIME)

        #TODO: 
        #content.add_widget(Label(text='Number of items:'))
        #content.add_widget(Slider(min=0, max=30, value=DEFAULT_SHOWTIME))
       
        replay = Button(text='Replay!')
        credits = Button(text='Credits')
        action = BoxLayout(orientation='horizontal')
        action.add_widget(replay)
        action.add_widget(credits)
        content.add_widget(action)


        popup = PopupGameOver(title='Game Over!',
                              content=content,
                              size_hint=(0.5, 0.5),pos_hint={'x':0.25, 'y':0.25},
                              auto_dismiss=False)
        replay.bind(on_press=popup.replay)
        replay.bind(on_press=self.restartGame)
        popup.open()

class PopupGameOver(Popup):
     def replay(self,inst):
         self.dismiss()



class MyPb(ProgressBar):
    def __init__(self, **kwargs):
        super(ProgressBar, self).__init__(**kwargs)
        self.ml = kwargs['ml']
    
    def foundAnItem(self,instance,value):
        self.value += 100*self.ml.level

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
    for i in glob(join(dirname(__file__),"icons", '*.gif')):
        icons.append(i)
    return sounds,icons

class MyAnimalsApp(App):

    def build(self):
        sounds,icons=loadData()
        show = DEFAULT_SHOWTIME

        g = MemoryLayout(cols=len(icons)/2, level=show,size_hint=(1,.9))
        config = BoxLayout(orientation='horizontal',spacing=10, size_hint=(1,.1))
        
        sound = ToggleButton(text='Sound On', size_hint=(0.1,1))
        sound.bind(on_press=MemoryButton.toggleSound)
        pb = MyPb(max=len(icons)*100*show, size_hint=(0.7,1),ml=g)
        
        score = LabelScore(text="Time:  0 s",size_hint=(0.1,1))
        missed =  LabelMissed(text="Missed:  0",size_hint=(0.1,1))
        
        
        config.add_widget(pb)
        config.add_widget(score)
        config.add_widget(missed)
        config.add_widget(sound)
        
        g.bind(missed=missed.update)     
        g.bind(elapsed=score.updateTime)        
        g.bind(left=pb.foundAnItem)

        playZone = BoxLayout(orientation='vertical')
        playZone.add_widget(g)
        playZone.add_widget(config)
        
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

       
        root=FloatLayout()
        root.add_widget(playZone)
        Clock.schedule_interval(g.initialCountdown,1)
        return root

if __name__ in ('__main__', '__android__'):
    MyAnimalsApp().run()
