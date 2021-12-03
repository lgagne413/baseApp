# -*- coding: utf-8 -*-
"""
This module can be used to speed up Python app development.

Frame structure is as follows:
    controller container -> PageTemplate Frame -> PageTemplate Canvas -> PageTemplate mainframe -> Page subframes
    
User should create classes that inherit from Controller, PageTemplate, and provided subframes (and their children) to create an app quickly. 

Quickstart:
    PAGES=[Home]
    app = Controller(PAGES,'0.0')
    app.title('baseApp')
    app.geometry('1400x700')

    app.mainloop()

Created on Fri Dec  3 11:23:53 2021

@author: lgagne
"""

import tkinter as tk
import pandas
import pandastable
#import datetime
#import re
import queue

######################
#templateFrames
######################

class PageTemplate(tk.Frame):
    """
    Base page for all of our frames.
    
    Inherits from Tk.Frame.
    
    Attributes:
        name: when a class inherits from PageTemplate this should be changed and used for convenience
        controller: the controller (tk.Tk) that runs the app
        cols: default width of grid
        canvas: placed over frame (self) to enable scroll bar usage
        mainframe: the frame where all subframes are to be placed
        elements: dict of dicts to hold page elements (navbar subframe, etc.)
        
    """
    def __init__(self, parent:tk.Frame, controller:tk.Tk,cols:int=50):
        """
        Inits PageTemplate class.
        
        Inherits from tk.Frame

        Parameters
        ----------
        parent : tk.Frame
            parent frame of PageTemplate instance.  Usually Controller class container attribute.
        controller : tk.Tk
            Controller class instance.
        cols : int, optional
            width of grid. The default is 50.

        Returns
        -------
        None.

        """
        tk.Frame.__init__(self, parent)
        self.name='template'

        self.controller = controller
        self.cols=cols

        vsb=tk.Scrollbar(self,orient='vertical')
        hsb=tk.Scrollbar(self,orient='horizontal')
        vsb.pack(side="right", fill="y")
        hsb.pack(side="bottom", fill="x")
        self.canvas=tk.Canvas(self, borderwidth=0)
        self.canvas.pack(side="left", fill="both", expand=True)
        self.canvas.configure(yscrollcommand=vsb.set)
        self.canvas.configure(xscrollcommand=hsb.set)
        vsb.configure(command=self.canvas.yview)
        hsb.configure(command=self.canvas.xview)
        self.mainframe=tk.Frame(self.canvas, background=self.canvas.cget('bg'))
        self.canvas.create_window((4, 4), window=self.mainframe, anchor="nw")
        self.mainframe.bind("<Configure>", self.scroll_set)

        self.elements={'subframes':{'navbar':NavBar(self.mainframe,self.controller)},'labels':{},'buttons':{},'entries':{},'vars':{},'tables':{},'queries':{}}
        self.elements['subframes']['navbar'].grid(row = 0, column = 0,rowspan=6,columnspan=cols,sticky='w')
        self.elements['subframes']['page']=tk.Frame(self.mainframe)
        self.elements['subframes']['page'].grid(row = 6, column = 0,rowspan=10,columnspan=cols,sticky='w')


    def scroll_set(self,event):
        """sets scroll functionality.  Used internally."""
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))

    def on_enter(self):
        """runs whenever the frame is shown by controller"""
        print(self.name)

    def lock(self):
        """used to lock navbar, can be modified to lock submit buttons, etc"""
        self.elements['subframes']['navbar'].lock_navbar()

    def unlock(self):
        """used to unlock navbar, can be modified to unlock submit buttons, etc"""
        self.elements['subframes']['navbar'].unlock_navbar()

class Home(PageTemplate):
    """Example inheritor of PageTemplate"""
    def __init__(self, parent, controller,**kwargs):
        super().__init__(parent,controller,**kwargs)
        self.name='Home'
        self.elements['subframes']['navbar'].update_title( self.name)
        self.elements['subframes']['navbar'].update_desc('Hello, world')

        self.elements['labels']['pageLabel']=tk.Label(self.elements['subframes']['page'], text ='This is the Page Frame',borderwidth=3,relief='ridge',font=self.controller.settings['medfont'])

        self.elements['labels']['pageLabel'].grid(row = 0, column = 1,sticky='w',columnspan=self.cols)

######################
#subframes
######################

class NavBar(tk.Frame):
    """
    A class for a basic navbar subframe.
    
    Inherits from tk.Frame
    
    Attributes:
        name: convenience attribute
        controller: Controller class instance.
        elements: dict of dicts to hold page elements (lables, vars, etc.)
    
    """
    def __init__(self, parent: tk.Frame, controller:tk.Tk):
        """
        Inits NavBar class

        Parameters
        ----------
        parent : tk.Frame
            parent frame of NavBar instance.  Usually PageTemplate class instance.

        controller : tk.Tk
            controller class instance.

        Returns
        -------
        None.

        """
        tk.Frame.__init__(self, parent)
        self.name = 'navbar_subframe'
        self.controller = controller
        self.elements={'subframes':{},'labels':{},'buttons':{},'entries':{},'vars':{},'texts':{}}

        self.elements['buttons']['Home']=tk.Button(self, text ="Home",command = lambda : controller.show_frame(Home),bg='red')

        self.elements['labels']['title']=tk.Label(self, text ="Default", font = self.controller.settings['largefont'])
        self.elements['texts']['desc']=tk.Text(self, wrap='word',width=150,height=5)
        self.elements['labels']['messages']=tk.Label(self, text ='Messages will be displayed here',font=self.controller.settings['smallfont'],fg='blue')

        self.elements['buttons']['Home'].grid(row = 0, column = 0,sticky='w')

        self.elements['labels']['title'].grid(row = 1, column = 0,sticky='w',columnspan=100)
        self.elements['texts']['desc'].grid(row = 2, column = 0,rowspan=4,columnspan=100,sticky='w')
        self.elements['labels']['messages'].grid(row=6,column=0,columnspan=100,sticky='w')

    def update_desc(self,text:str):
        """Change the description element """
        self.elements['texts']['desc'].insert(1.0,text)
        self.elements['texts']['desc']["state"]="disabled"
        self.update_idletasks()

    def lock_navbar(self):
        """Lock the navbar """
        for n in self.elements['buttons']:
            self.elements['buttons'][n]['state']='disabled'
        self.update_idletasks()

    def unlock_navbar(self):
        """Unlock the navbar """
        for n in self.elements['buttons']:
            self.elements['buttons'][n]['state']='normal'
        self.update_idletasks()

    def update_title(self,title):
        """Change the title element """
        self.elements['labels']['title']['text']=title
        self.update_idletasks()

    def update_message(self,m):
        """Change the message element """
        self.elements['labels']['messages'].config(text=m)
        self.update_idletasks()

class SubTable(tk.Frame):
    """
    A class for a basic table subframe per pandastable.
    
    Inherits from tk.Frame
    
    Attributes:
        name: convenience attribute
        controller: Controller class instance.
        elements: dict of dicts to hold page elements (buttons, tables, etc.)
    
    """
    def __init__(self, parent:tk.Frame, controller:tk.Tk):
        """
        Inits SubTable class
        
        Inherits from tk.Frame

        Parameters
        ----------
        parent : tk.Frame
            parent frame of SubTable instance.  Usually PageTemplate class instance.
        controller : tk.Tk
            controller class instance.

        Returns
        -------
        None.

        """
        tk.Frame.__init__(self, parent)
        self.name = 'table_subframe'
        self.controller = controller
        self.elements={'subframes':{},'labels':{},'buttons':{},'entries':{},'vars':{'tablemodel':pandastable.TableModel()},'texts':{},
                        'tables':{'table':pandastable.Table(self,editable=False,width=1200,height=500)}}

        self.elements['tables']['table'].grid(row = 0, column = 0,columnspan=100)

    def edit_table(self,df:pandas.DataFrame):
        """DataFrame to update table"""
        self.elements['vars']['tablemodel'].setup(df)
        self.elements['tables']['table'].updateModel(self.elements['vars']['tablemodel'])
        self.elements['tables']['table'].show()


######################
#App
######################

class Controller(tk.Tk):
    """
    Base Class for Tkinter App.
    
    Holds all app-wide data and pages.  In herits from tk.Tk.
    
    Attributes:
        settings: A dictionary of app-wide settings, used for uniformity:
            version: the version of the app.
            smallfont, medfont, largefont: sets the default fonts.
        frames: A dictionary of frame class : frame instance pairs.
        pages: a list of frame classes.
        data: a dict of dicts to store app-wide dataframes, inputs, connections, etc.
        queue: a queue for implementing threading.
        
    """
    def __init__(self, pages:list,version:str,*args, **kwargs):
        """
        Inits Controller with attributes.

        Parameters
        ----------
        pages : list
            list of page / frame classes.
        version : str
            string describing version of app.
        *args : TYPE
            additional args to pass through to tk.Tk.
        **kwargs : TYPE
            additional kwargs to pass through to tk.Tk.

        Returns
        -------
        None.

        """
        tk.Tk.__init__(self, *args, **kwargs)
        self.settings={'version':version,'smallfont':("Verdana", 12),'medfont':("Verdana", 20),'largefont':("Verdana", 30)}
        container = tk.Frame(self)
        container.pack(side = "top", fill = "both", expand = True)

        container.grid_rowconfigure(0, weight = 1)
        container.grid_columnconfigure(0, weight = 1)

        self.frames = {}
        self.pages=pages
        for F in self.pages:
            self.frames[F] = F(container, self)
            self.frames[F].grid(row = 0, column = 0, sticky ="nsew")
        self.show_frame(self.pages[0])
        self.data = {'df':{},'inputs':{},'conn':{}}
        self.queue=queue.Queue(maxsize=10)
        

    def show_frame(self, cont:PageTemplate):
        """
        Changes frame the app is showing and calls the frames on_enter function

        Parameters
        ----------
        cont : tk.Frame
            The new frame (class) to show.

        Returns
        -------
        None.

        """
        frame = self.frames[cont]
        frame.tkraise()
        frame.on_enter()


if __name__ == '__main__':
    PAGES=[Home]
    app = Controller(PAGES,'0.0')
    app.title('baseApp')
    app.geometry('1400x700')

    app.mainloop()