# for graphics
import tkinter
from tkinter.constants import *

# various custom widgets
import dialwidget
import graphwidget
import menuwidget

''' Constants controlling the default appearance
of the panels. These constants only affect the
panels themselves and not the widgets within them. '''
PANEL_HEIGHT = 100
PANEL_WIDTH = 256
PANEL_GS_HEIGHT = 64
PANEL_GS_WIDTH = PANEL_WIDTH
PANEL_FONT = "Fixed"


class SynthPanel:
    ''' Base control panel widget. Every control panel has three panels:
    a Top panel, containing a label and a toggle;
    a Middle panel, containing a graphscreen (optional);
    and a Bottom panel, containing some Dials.

    Parameters:
        parent: (Widget) tk-style parent widget
        target: (Synth component) the component to control

    This is a base class. It should not be directly placed on screen.
    Instead, the subclasses OscPanel, EnvPanel, FiltPanel, and LFOPanel
    should be used. '''


    ''' Subclasses can override this to change the label on the panel. '''
    _label = "Panel"

    ''' This can be overridden to False in a subclass to make
    a panel with no graph. '''
    _has_graph = True


    def __init__(self, parent, target):
        ''' Initializer for SynthPanel. Creates a three-frame panel
        with a label and toggle at the top, a graph screen in the
        middle (unless disabled by _has_graph), and a row of dials
        at the bottom. The dials are set up in _dials, which can be
        overridden by subclasses. This function should not be overridden;
        to set up subclass-specific data/widgets _special_init can
        be used. '''

        # regular data
        self.target = target
        self.enabled = False

        # encapsulated widget
        self.widget = tkinter.Frame(
            parent,
            height=PANEL_HEIGHT,
            width=PANEL_WIDTH,
            relief=RAISED,
            bg="black",
            bd=1,
            highlightthickness=0,
        )

        # three panels
        self.w_top, self.w_mid, self.w_bot = (tkinter.Frame(
            self.widget,
            width=PANEL_WIDTH,
            bd=0,
            bg="black",
            highlightthickness=0,

        ) for _ in range(3))

        self.w_top.pack(side=TOP, fill=BOTH, padx=5, pady=5)
        self.w_mid.pack(side=TOP, fill=BOTH, padx=5, pady=5)
        self.w_bot.pack(side=TOP, fill=BOTH, padx=5, pady=5)

        # label and toggle
        self.w_label = tkinter.Label(
            self.w_top,
            text=self._label,
            justify=CENTER,
            font=PANEL_FONT+" 9",
            bg="black",
            fg="white",
            bd=0,
            highlightthickness=0,
        )
        self.w_toggle = tkinter.Button(
            self.w_top,
            text="###",
            justify=CENTER,
            font=PANEL_FONT+" 9",
            command=self._toggle_enabled,
            bg="black",
            fg="white",
            highlightthickness=0,
        )

        self.w_toggle.pack(side=LEFT, padx=1)
        self.w_label.pack(side=LEFT, fill=BOTH, padx=4)

        # graph screen (if enabled)
        if self._has_graph:
            self.w_graph = graphwidget.GraphScreen(
                parent=self.w_mid,
                width=PANEL_GS_WIDTH,
                height=PANEL_GS_HEIGHT,
                fx=self._graph_fx,
            )

            self.w_graph.pack(side=TOP, padx=1)

        # set up subclass-specific items
        self._special_init()

        self._make_dials()

        # toggle from False to True for consistency
        self._toggle_enabled()


    def _special_init(self):
        ''' Subclasses can override this to set up specific
        widgets without having to modify __init__ itself. It
        is called just before the dials are generated. '''
        pass


    def _dials(self):
        ''' This should be overridden on subclasses to specify
        exactly what dials should be created. This function
        should return a list of dictionaries, each one specifying
        the parameters of a Dial plus the identifier (as a string)
        of a target parameter that the dial should set. (see _add_dial) '''
        pass


    def _graph_fx(self, x):
        ''' This is the function that will be displayed on the graph.
        It should be overridden in each subclass by a function that
        takes an integer and returns an integer. '''
        pass


    def redraw(self):
        ''' Redraws the panel's graph screen. '''
        if self._has_graph:
            self.w_graph.redraw()


    def _make_dials(self):
        ''' Generates all the panel's dials as specified by
        self._dials in the subclass. '''

        # generate dials from _dials:
        # _dial_targets will store dial labels --> target member names;
        # _dial_causes_update will contain labels of dials which have
        # graph_update enabled and should thus cause a redraw of the graph;
        # _w_dials just holds all the dial widgets in order
        self._dial_targets = dict()
        self._dial_causes_update = set()
        self._w_dials = list()
        for dial in self._dials():
            self._add_dial(**dial)


    def _add_dial(self, **kwargs):
        ''' Called once for each element returned from _dials.
        Accepts all the keyword arguments accepted by Dial.__init__
        (which will be passed directly to the dial) as well as:
            target: (str) the python name of a data member of
                self.target. When the dial's value changes,
                this member will be updated to the new value.
                Conflicts with Dial.callback.
            update_graph: (bool) if True, the panel's graph screen
                will be redrawn whenever the dial's value changes.
                Works for both 'target' and 'callback' based dials.
        '''

        def print_warning(msg):
            ''' Prints a formatted warning if a subclass is doing
            something that is probably wrong. '''
            print("*** SynthPanel WARNING: Dial {} of widget {} ".format(
                  kwargs['label'], self._label) + msg)

        # make sure this dial actually does something
        if 'callback' not in kwargs and 'target' not in kwargs:
            print_warning("does not target a parameter or specify a callback "
                          "and will therefore be completely useless.")

        # but not two conflicting things
        if 'callback' in kwargs and 'target' in kwargs:
            print_warning("specifies both target parameter and callback. "
                          "Only the callback will function.")

        # convert targets to callbacks
        if 'callback' not in kwargs and 'target' in kwargs:
            kwargs['callback'] = self._set_param
            target = kwargs['target']

            if target not in self.target.__dict__:
                print_warning("targets parameter {} of {}, which doesn't look "
                              "like it exists.".format(target, self.target))

            del kwargs['target']
        elif 'callback' in kwargs:
            # convert callbacks to callbacks
            target = kwargs['callback']
            kwargs['callback'] = self._callback

        # check update_graph
        if 'update_graph' in kwargs and kwargs['update_graph']:
            if not self._has_graph:
                print_warning("specifies update_graph, but the panel"
                              "has no graph.")
            self._dial_causes_update.add(kwargs['label'])
            del kwargs['update_graph']

        # save target
        self._dial_targets[kwargs['label']] = target

        # instantiate dial
        dial = dialwidget.Dial(
            parent=self.w_bot,
            **kwargs
        )
        dial.pack(side=LEFT, expand=1)
        self._w_dials.append(dial)


    def remake_dials(self):
        ''' Resets the widget's dial panel, allowing the dials to
        be updated dynamically. NOTE this function *should not* be
        called from a dial callback as this will loop indefinitely. '''

        if not '_w_dials' in self.__dict__:
            # if this function is called in a callback, don't
            # trigger it unless dials have been made yet.
            # Ideally this should account for being called within
            # a dial callback and trigger only if not in the
            # initialization phase, but this situation never
            # actually occurs in the synthesizer interface.
            return

        for dial in self._w_dials:
            dial.widget.destroy()

        self._make_dials()


    def _toggle_enabled(self):
        ''' Toggles the ON/OFF switch of the panel and enables/disables
        the target synth component. '''

        if self.enabled:
            self.w_toggle.config(text="OFF", bg="red")
        else:
            self.w_toggle.config(text=" ON", bg="green")

        self.enabled = not self.enabled
        self.target.enable = self.enabled


    def _set_param(self, value, label):
        ''' Sets the parameter named by _dial_targets[label]
        (set up by _add_dial) to the value. This is a callback
        function which will be called by a Dial widget which
        has been instantiated with the 'target' argument. '''

        iden = self._dial_targets[label]
        self.target.__dict__[iden] = value


        # update graph if requested
        if label in self._dial_causes_update:
            self.redraw()


    def _callback(self, value, label):
        ''' Invokes a dial callback function set up by _add_dial.
        This intermediate function exists to allow functionality
        like update_graph while maintaining the callback chain. '''

        callback = self._dial_targets[label]

        if callback.__code__.co_argcount == 2:
            # two-argument form self, value
            callback(value)
        elif callback.__code__.co_argcount == 3:
            # three-argument form self, value, label
            callback(value, label)
        else:
            raise RuntimeError("Invalid callback signature in dial")

        # update graph if requested
        if label in self._dial_causes_update:
            self.redraw()


    def pack(self, **kwargs):
        ''' Packs the underlying widget. '''
        self.widget.pack(**kwargs)


class OscPanel(SynthPanel):
    ''' SynthPanel for an Oscillator component. '''

    _label = "Oscillator"


    def _special_init(self):
        ''' Adds a wavetable selector menu. '''

        wts = self._get_wavetables()
        initial = wts[0]

        self.w_menu = menuwidget.Menu(
            parent=self.w_top,
            title="Wavetable File",
            initial=initial[0],
            choices=self._get_wavetables(),
            callback=self._set_wavetable,
        )
        self.w_menu.pack(side=RIGHT, fill=X)
        self._set_wavetable(initial[1])


    def _dials(self):
        return [
            {'label': "Waveshape",
             'dmin': 0, 'dmax': self.target.wave_tables_num-1, 'dincrement': 1,
             'dinitial': 0,
             'valformat': "[{:.0f}]",
             'callback': self._set_waveshape,
             'update_graph': True },
            {'label': "Volume",
             'dmin': 0.0, 'dmax': 1.0,
             'dinitial': 0.75,
             'valformat': "{:.0%}",
             'target': 'volume' },
            {'label': "Detune",
             'dmin': -24, 'dmax': 24, 'dincrement': 1,
             'dinitial': 0,
             'valformat': "{:+.0f}",
             'target': 'detune' },
             {'label': "Phase Off",
              'dmin': 0, 'dmax': 2024, 'dincrement': 1,
              'dinitial': 0,
              'valformat': "{:+.0f}",
              'target': 'pOffset' }
        ]


    def _graph_fx(self, x):
        ''' Gets the graph shape from the oscillator's wavetable. '''

        # converts x in (0, width) to (framestart, framestart+framesize)
        # for lookup in wavetable.
        wtx = self.target.wavetablepos + (
              (self.target.wavetsize * x) // PANEL_GS_WIDTH)

        # looks up wtx in wavetable and converts unsigned to signed
        wtval = (self.target.wave_tables[wtx] + 32768) % 65536

        # scales wtval to panel height size
        return PANEL_GS_HEIGHT * wtval // 65536


    def _set_waveshape(self, value, label):
        ''' Callback to set the oscillator waveshape. '''

        # + 0.001 accounts for float error in the dial value
        self.target.wavetablepos = int(value + 0.001) * self.target.wavetsize


    def _get_wavetables(self):
        ''' Looks up the available wavetables. '''

        import pathlib
        here = pathlib.Path('./Synth/wavetables')

        return [
            (str(path.parts[-1]), str(path))
            for path in here.glob('*.wav')
        ]


    def _set_wavetable(self, value):
        ''' Sets the wavetable of the underlying oscillator. '''

        self.target.set_wavetable(value)

        # reset waveshape dial maximum
        self.remake_dials()


class EnvPanel(SynthPanel):
    ''' SynthPanel for an Envelope component. '''

    _label = "Envelope"


    def _dials(self):
        return [
            {'label': "Attack",
             'dmin': 0.001, 'dmax': 1,
             'dinitial': 0.07,
             'callback': self.target.set_attack,
             'update_graph': True },
            {'label': "Decay",
             'dmin': 0, 'dmax': 1,
             'dinitial': 0.08,
             'callback': self.target.set_decay,
             'update_graph': True },
            {'label': "Sustain",
             'dmin': 0, 'dmax': 1,
             'dinitial': 0.8,
             'valformat': "{:.1f}",
             'callback': self.target.set_sustain,
             'update_graph': True },
            {'label': "Release",
             'dmin': 0.001, 'dmax': 1,
             'dinitial': 0.1,
             'callback': self.target.set_release,
             'update_graph': True }
        ]


    def _graph_fx(self, x):
        ''' Checks the envelope response for each moment in time.
        Uses the actual envelope function so should be accurate. '''

        # set a representative note length. this makes the graph
        # look better and should be overwritten before any notes
        # are actually played.
        self.target.sustainsamples = 0.25 * self.target.samplerate

        # converts x in (0, width) to time domain for a scale of 1
        t = ((1 * x / PANEL_GS_WIDTH) * self.target.samplerate)

        # gets unscaled envelope response for that time
        envval = self.target.gen_env(t, 1)

        # converts to panel scale
        return int(envval * (PANEL_GS_HEIGHT - 4))


class FiltPanel(SynthPanel):
    ''' SynthPanel for a Filter component. '''

    _label = "Filter"


    def _special_init(self):
        ''' Sets band type and adds band toggle button. Also creates
        a variable to store the last dial value so it can be
        remembered when the band changes. '''

        self.band = "Low Pass"
        self._last_value = -5

        # Low-pass/High-pass toggle
        self.w_band = tkinter.Button(
            self.w_bot,
            text="###",
            justify=CENTER,
            font=PANEL_FONT+" 9",
            command=self._toggle_band,
            bg="black",
            bd=1,
            highlightthickness=0,
        )
        self.w_band.pack(side=LEFT, fill=X, padx=3)

        # for consistency
        self._toggle_band()


    def _toggle_band(self):
        ''' Switches the band of the filter. '''

        if self.band == "Low Pass":
            self.w_band.config(text="HIGH", bg="darkcyan")
            self.band = "High Pass"
            self._log_set_cutoff(self._last_value, None)
        else:
            self.w_band.config(text=" LOW", bg="blue")
            self.band = "Low Pass"
            self._log_set_cutoff(self._last_value, None)

        # redraw graph
        self.redraw()


    def _dials(self):
        return [
            {'label': "Cutoff",
             'dmin':0, 'dmax':6, # (logarithmic scaled)
             'dinitial': 0,
             'valformat': "E{:+.0f}",
             'callback': self._log_set_cutoff,
             'update_graph': True }
        ]


    def _graph_fx(self, x):
        ''' Generates a graph for the filter. This method doesn't
        actually use the real filter object (since it's in time-domain
        and the graph is in frequency-domain) but instead uses the
        theoretical corresponding frequency formula - so, theoretically,
        the graph is correct, but this is not guaranteed because it
        is generated independently of the actual filter. '''

        if 'band' not in self.__dict__:
            return None

        # convert from logarithmic to linear
        freq = 10**(((x * 2 / PANEL_GS_WIDTH) - 1) * 5)

        # frequency curve calculation and scaling
        if self.band == "High Pass":
            return int(PANEL_GS_HEIGHT / (1 + self.target.cutoff_hp / freq))
        else:
            return int(PANEL_GS_HEIGHT / (1 + freq / self.target.cutoff_lp))


    def _log_set_cutoff(self, value, label):
        ''' Converts the dial value from logarithmic scale to linear
        scale and sets the appropriate cutoff and filter mode based
        on the panel's band setting. '''

        # save for later band switching
        self._last_value = value

        # set cutoff and band
        if self.band == "High Pass":
            self.target.set_cutoff_highpass(10**value)
        else:
            self.target.set_cutoff_lowpass(10**value)


class LFOPanel(SynthPanel):
    ''' SynthPanel for an LFO component. '''

    _label = "LFO"

    # LFO does not have a graph - it's not really
    # necessary and removing it avoids running out
    # of room for the sequencer
    _has_graph = False


    def _special_init(self):
        ''' Sets up device and parameter menus and
        ret/con toggle button. '''

        self._choices_osc = [
            ("Frame", 'wavtable position'),
            ("Detune", 'detune'),
            ("Volume", 'volume')
        ]

        self._choices_env = [
            ("Attack", 'attack'),
            ("Decay", 'decay'),
            ("Sustain", 'sustainamp'),
            ("Release", 'release')
        ]

        self._choices_fil = [
            ("Cutoff", 'cutoff')
        ]

        self._choices_lfo = [
            ("Freq", 'speed'),
            ("Range", 'amount'),
            ("Offset", 'offset')
        ]

        self.w_menu_p = menuwidget.Menu(
            parent=self.w_top,
            title="Parameter",
            initial="",
            choices=[],
            callback=self._set_target_param,
        )
        self.w_menu_p.pack(side=RIGHT, fill=X)

        self.w_menu_t = menuwidget.Menu(
            parent=self.w_top,
            title="Device",
            initial="None",
            choices=[
                ("None", (None, None)),
                ("Osc1", ('oscil', self._choices_osc)),
                ("Osc2", ('oscil2', self._choices_osc)),
                ("Env1", ('env1', self._choices_env)),
                ("Env2", ('env2', self._choices_env)),
                ("Fil1", ('fil1', self._choices_fil)),
                ("Fil2", ('fil2', self._choices_fil)),
                ("LFO1", ('lfo1', self._choices_lfo)),
                ("LFO2", ('lfo2', self._choices_lfo)),
                ("LFO3", ('lfo3', self._choices_lfo))
            ],
            callback=self._set_target,
        )
        self.w_menu_t.pack(side=RIGHT, fill=X)


        # ret/con toggle
        self.ret_enabled = True
        self.w_ret = tkinter.Button(
            self.w_bot,
            text="###",
            justify=CENTER,
            font=PANEL_FONT+" 9",
            command=self._toggle_retrig,
            bg="black",
            bd=1,
            highlightthickness=0,
        )
        self.w_ret.pack(side=RIGHT, fill=X, padx=3)


        self.target.set_device_control(None, None)
        self._toggle_retrig()


    def _dials(self):
        return [
            {'label': "Frequency",
             'dmin': 0, 'dmax': 2,
             'dinitial': 0.2,
             'target': 'speed' },
            {'label': "Scale",
             'dmin': -1, 'dmax': 1,
             'dinitial': 0.5,
             'target': 'amount' },
            {'label': "Offset",
             'dmin': -1, 'dmax': 1,
             'dinitial': 0,
             'target': 'offset' },
            {'label': "Waveshape",
             'dmin': 0, 'dmax': 2, 'dincrement': 1,
             'dinitial': 0,
             'valcallback': self._get_waveshape_name,
             'callback': self._set_waveshape }
        ]


    def _get_waveshape_name(self, value):
        ''' Gets the short waveshape name for each dial index. '''

        # correcting for float error of dial value
        idx = int(value + 0.001)

        return ['SIN', 'SQR', 'SAW'][idx]


    def _set_waveshape(self, value):
        ''' Sets the waveshape of the LFO based on the dial index. '''

        # correcting for float error of dial value
        idx = int(value + 0.001)

        # these are the 'long' names used by the LFO class
        ws = ['sin', 'square', 'saw'][idx]

        self.target.wavetype = ws


    def _set_target(self, target):
        ''' Sets the target component for the LFO. '''
        if target[0] is not None:
            self.lfo_target = target[0]
            self.w_menu_p.set_choices(target[1])
        else:
            self.lfo_target = None
            self.w_menu_p.set_choices([])
        self.w_menu_p.set_label("")

        self.target.set_device_control(self.lfo_target, None)


    def _set_target_param(self, target):
        ''' Sets the target parameter for the LFO. '''
        self.target.set_device_control(self.lfo_target, target)


    def _toggle_retrig(self):
        ''' Toggles retrig/continuity for the LFO. '''

        if self.ret_enabled:
            self.w_ret.config(text="Cnt", bg="purple")
        else:
            self.w_ret.config(text="Ret", bg="magenta")

        self.ret_enabled = not self.ret_enabled
        self.target.retrig = self.ret_enabled


    def bind_to_synth(self, synth):
        ''' Sets a Synth object from which the LFO will draw
        its references to devices. '''
        self.synth = synth
