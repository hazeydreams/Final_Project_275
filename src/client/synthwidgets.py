import tkinter
from tkinter.constants import *

import dialwidget

''' Synthesizer controller widgets:
        Selector - radio button bar
        OscController - visual oscillator controller
'''


class _SelElem:
    ''' Selector Bar Element - class representing a single
    element of a Selector bar. Encapsulates a button widget
    which calls the parent's callback function when pressed.
    (See synthwidgets.Selector for more information)
    
    Parameters:
        sel_parent: (Selector) the selector this step is a member of.
        idx: (int) index of this element in the selector.
        text: (str) text to appear on the encapsulated button.
    '''
        
    def __init__(self, sel_parent, idx, text):
        ''' Initializer for _SelElem (see class documentation)'''
        # regular data
        self.sel_parent = sel_parent
        self.idx = idx
        
        # encapsulated widget
        self.widget = tkinter.Button(
            sel_parent.widget,
            text=text,
            font="Fixed 9",
            command=self._parent_select
        )
        
        # set to deselected by default, for consistency
        self.deselect()
        
        # automatically pack encapsulated widget left to right
        # (NOTE in a really complete implementation, one
        #  could imagine Selectors pointing in different
        #  directions (top to bottom, right to left...)
        #  created by parameterizing this packing)
        self.widget.pack(side=LEFT)
    
    
    def select(self):
        ''' Visually sets this step to selected. '''
        self.widget.config(bg='blue')
    
    
    def deselect(self):
        ''' Visually sets this step to deselected. '''
        self.widget.config(bg='black')
    
    def _parent_select(self):
        ''' Calls parent callback with this element's index. '''
        self.sel_parent._select(self.idx)
    


class Selector:
    ''' Selector Bar Widget - a radio-button style selector bar.
    
    Parameters:
        parent: (Widget) tk-style parent widget.
        elements: (list[str]) (or anything convertible to str)
            Elements of the selector. Each element will appear
            as a button in the selector with the specified text.
        callback: (function) will be called when an element
            is selected, passing the index of the element. None
            can be specified for no callback.
        init_idx: (int) index of the initially selected element.
            Default 0.
    '''
    
    def __init__(self, parent, elements, callback=None, init_idx=0):
        ''' Initializer for Selector (see class documentation)'''
        # regular data
        self.parent = parent
        self.callback = callback
        
        # encapsulated widget
        self.widget = tkinter.Frame(parent)
        
        # elements
        self.elements = [_SelElem(self, i, str(s))
                         for i, s in enumerate(elements)]
        
        # start with an element selected
        self._selected = init_idx
        self.elements[init_idx].select()
    
    
    def pack(self, **kwargs):
        ''' Packs the encapsulated widget.
        
        Arguments:
            same as underlying pack() function.
        '''
        
        self.widget.pack(**kwargs)
    
    
    def _select(self, idx):
        ''' Called by the elements of the selector when clicked.
        Sets the appropriate selected/deselected states and
        calls the callback function. '''
        
        self.elements[self._selected].deselect()
        self._selected = idx
        self.elements[idx].select()
        
        if self.callback is not None:
            self.callback(idx)
    


class OscController:
    def __init__(self, parent, oscillator, volume, offset, detune):
        # regular data
        self.volume = volume
        self.offset = offset
        self.detune = detune
        self.enabled = False
        self.oscillator = oscillator
        
        # encapsulated widget
        self.widget = tkinter.Frame(parent, bd=1, relief=RAISED, pady=3,
            padx=3)
        self.widget.pack(side=LEFT)
        
        
        # individual controls
        
        # The top frame controls the volume
        self.w_top_frame = tkinter.Frame(self.widget, pady=5)
        
        # top frame --> volume dial
        self.w_amplitude = dialwidget.dialwidget(
            self.w_top_frame,
            text="Volume",
            dmin=0.0,
            dmax=1.0,
            dinitial=1.0,
            dmintext='0%',
            dmaxtext='100%',
            callback=self.set_volume
        )
        
        # top frame --> label
        self.w_label = tkinter.Label(
            self.w_top_frame,
            text="Oscillator",
            font="Fixed 8",
            padx=5
        )
        
        # top frame --> disable-completely toggle
        self.w_toggle = tkinter.Button(
            self.w_top_frame,
            font="Fixed 9",
            command=self.toggle_enabled
        )
        
        # pack top frame
        self.w_amplitude.pack(side=RIGHT)
        self.w_label.pack(side=RIGHT, expand=1)
        self.w_toggle.pack(side=LEFT)
        self.w_top_frame.pack(side=TOP)
        
        # Middle frame: waveshape selector
        
        # Bottom frame: detune and octave offset controls
        self.w_bot_frame = tkinter.Frame(self.widget)
        
        # bottom frame --> octave offset dial
        self.w_octave = dialwidget.dialwidget(
            self.w_bot_frame,
            text="Octave",
            dmin=-4,
            dmax=4,
            dinitial=0,
            dincrement=1,
            dmintext='-4',
            dmaxtext='+4',
            callback=self.set_offset
        )
        
        # bottom frame --> detune dial
        self.w_detune = dialwidget.dialwidget(
            self.w_bot_frame,
            text="Detune",
            dmin=-24,
            dmax=24,
            dinitial=0,
            dmintext='-24',
            dmaxtext='+24',
            callback=self.set_detune
        )
        self.w_octave.pack(side=LEFT)
        self.w_detune.pack(side=LEFT)
        self.w_bot_frame.pack(side=TOP)
        
        # starts FALSE, set TRUE
        self.toggle_enabled()
    
    
    def toggle_enabled(self):
        if self.enabled:
            self.w_toggle.config(text="OFF", bg="red")
        else:
            self.w_toggle.config(text=" ON", bg="green")
        self.enabled = not self.enabled
    
    
    def set_offset(self, value):
        # (correcting for float error)
        self.offset = int(value+0.001)
    
    
    def set_detune(self, value):
        self.detune = value
    
    
    def set_volume(self, value):
        self.volume = value
    
    
    def apply(self):
        ''' Applies the settings to the underlying oscillator. '''
        if not self.enabled:
            self.oscillator.volume = 0.0
        else:
            # (Octave offset is applied at generation time.)
            self.oscillator.volume = self.volume
            self.oscillator.detune = self.detune
    
