import math


from Synth.osc import wtOsc
from Synth.envelope import envelope
import Synth.filt

class lfo:
    '''
    Don't use yet, one that works is in the synth to demonstate
    '''

    def __init__(self, synth, samplerate=44100, device=None, control=None, amount=0.1,offset=-0.5, wavetype='sin', speed=1):
        self.samplerate = samplerate
        self.device = device
        self.control = control
        self.synth = synth

        self.speed = speed
        self.speed_max = 50
        self.speed_min = 0

        self.amount = amount
        self.amount_max = 1
        self.amount_min = -1

        self.offset = offset
        self.offset_max = 1
        self.offset_min = 0

        self.period = 2 * math.pi
        self.phase = 0
        self.set_speed(self.speed)

        self.wavetype = wavetype

        self.enable = True
        self.retrig = False

    def set_device_control(self, device, control):
        self.device = device
        self.control = control


    def get_retrig(self):
        if self.retrig == True:
            self.phase = 0

    def set_speed(self, speed):
        '''
            This sets the speed of the LFO and changes the phase increment
            accordingly.

                Args:
                    speed      int, representing the frequncy of the LFO in Hz

                Returns:
                    None

        '''
        self.speed = speed
        self.phaseInc = (speed/self.samplerate)*self.period


    def update_control(self, device=None, control=None):
        '''
            This function updates the desired control based on a float from -1 to 1
            generated by genOutput.

                Args:
                    device=None,    Object of the device to control, valid options are
                                    filter from filt.py, wtOsc from osc.py, envelope
                                    from envelope.py and lfo from LFO.py

                    control=None,   str, string containing the control you want to
                                    modulate. The types are documented in the synth.py
                                    docstring as well as there respective string

                Returns:
                    None

        '''
        if self.enable == False:
            return

        if control == None:
            return

        scale = self.genOutput()

        if scale > 1:
            scale = 1
        elif scale < -1:
            scale = -1



        if device == 'oscil' or device == 'oscil2':
            if control == 'wavtable position': #works
                scale = (scale/2) + 0.5
                delta = (self.synth.__dict__[device].wavetablepos_max*scale)
                delta = delta - (delta%self.synth.__dict__[device].detune_step)

                if delta > self.synth.__dict__[device].wavetablepos_max:
                    self.synth.__dict__[device].wavetablepos == self.synth.__dict__[device].wavetablepos_max

                elif delta < self.synth.__dict__[device].wavetablepos_min:
                    self.synth.__dict__[device].wavetablepos == self.synth.__dict__[device].wavetablepos_min

                else:
                    self.synth.__dict__[device].wavetablepos = delta


            if control == 'detune': #
                delta = self.synth.__dict__[device].detune_max*scale

                if delta > self.synth.__dict__[device].detune_max:
                    self.synth.__dict__[device].detune == self.synth.__dict__[device].detune_max

                elif delta < self.synth.__dict__[device].detune_min:
                    self.synth.__dict__[device].detune == self.synth.__dict__[device].detune_min

                else:
                    self.synth.__dict__[device].detune = delta

                self.synth.__dict__[device].gen_freq()

            if control == 'volume': #works
                scale = (scale/2) + 0.5
                self.synth.__dict__[device].volume = scale



        if device == 'env1' or device == 'env2':
            if control == 'attack': #works
                scale = (scale/2) + 0.5
                delta = (self.synth.__dict__[device].attack_max*scale)

                if delta > self.synth.__dict__[device].attack_max:
                    self.synth.__dict__[device].set_attack(self.synth.__dict__[device].attack_max)

                if delta < self.synth.__dict__[device].attack_min:
                    self.synth.__dict__[device].set_attack(self.synth.__dict__[device].attack_min)

                else:
                    self.synth.__dict__[device].set_attack(delta)

            if control == 'decay': #works
                scale = (scale/2) + 0.5
                delta = (self.synth.__dict__[device].decay_max*scale)


                if delta > self.synth.__dict__[device].decay_max:
                    self.synth.__dict__[device].set_decay(self.synth.__dict__[device].decay_max)

                if delta < self.synth.__dict__[device].decay_min:
                    self.synth.__dict__[device].set_decay(self.synth.__dict__[device].decay_min)

                else:
                    self.synth.__dict__[device].set_decay(delta)

            if control == 'release': #works
                scale = (scale/2) + 0.5
                delta = (self.synth.__dict__[device].release_max*scale)

                if delta > self.synth.__dict__[device].release_max:
                    self.synth.__dict__[device].set_release(self.synth.__dict__[device].release_max)

                if delta < self.synth.__dict__[device].sustain_min:
                    self.synth.__dict__[device].set_release(self.synth.__dict__[device].release_min)

                else:
                    self.synth.__dict__[device].set_release(delta)

            if control == 'sustainamp': #works
                scale = (scale/2) + 0.5
                self.synth.__dict__[device].set_sustain(self.synth.__dict__[device].sustainsamples/self.synth.__dict__[device].samplerate, scale)


        if device == 'fil1' or device == 'fil2':

            if control == 'cutoff':
                if self.synth.__dict__[device].filtertype == 'Low_Pass':
                    scale = (scale/2) + 0.5
                    delta = (self.synth.__dict__[device].set_cutoff_lowpass_max*scale)


                    if delta > self.synth.__dict__[device].set_cutoff_lowpass_max:
                        self.synth.__dict__[device].set_cutoff_lowpass(self.synth.__dict__[device].set_cutoff_lowpass_max)

                    if delta < self.synth.__dict__[device].set_cutoff_lowpass_min:
                        self.synth.__dict__[device].set_cutoff_lowpass(self.synth.__dict__[device].set_cutoff_lowpass_min)


                    else:
                        self.synth.__dict__[device].set_cutoff_lowpass(delta)

                if self.synth.__dict__[device].filtertype == 'High_Pass':
                    scale = (scale/2) + 0.5
                    delta = (self.synth.__dict__[device].set_cutoff_highpass_max*scale)


                    if delta > self.synth.__dict__[device].set_cutoff_highpass_max:
                        self.synth.__dict__[device].set_cutoff_highpass(self.synth.__dict__[device].set_cutoff_highpass_max)

                    if delta < self.synth.__dict__[device].set_cutoff_highpass_max:
                        self.synth.__dict__[device].set_cutoff_highpass(self.synth.__dict__[device].set_cutoff_highpass_min)


                    else:
                        self.synth.__dict__[device].set_cutoff_highpass(delta)

        if device == 'lfo1' or device == 'lfo2' or device == 'lfo3':

            if control == 'speed': # works
                scale = (scale/2) + 0.5
                delta = (self.synth.__dict__[device].speed_max*scale)

                if delta > self.synth.__dict__[device].speed_max:
                    self.synth.__dict__[device].set_speed(self.synth.__dict__[device].speed_max)

                if delta < self.synth.__dict__[device].speed_min:
                    self.synth.__dict__[device].set_speed(self.synth.__dict__[device].speed_min)

                else:
                    self.synth.__dict__[device].set_speed(delta)

            if control == 'amount': #works
                scale = (scale/2) + 0.5

                if scale > self.synth.__dict__[device].amount_max:
                    self.synth.__dict__[device].amount = self.synth.__dict__[device].speed_max

                if scale < self.synth.__dict__[device].amount_min:
                    self.synth.__dict__[device].amount = self.synth.__dict__[device].speed_min

                else:
                    self.synth.__dict__[device].amount = scale

            if control == 'offset': #works

                if scale > self.synth.__dict__[device].amount_max:
                    self.synth.__dict__[device].offset = self.synth.__dict__[device].offset_max

                if scale < self.synth.__dict__[device].offset_min:
                    self.synth.__dict__[device].offset = self.synth.__dict__[device].offset_min

                else:
                    self.synth.__dict__[device].offset = scale






    def genOutput(self):
        '''
        '''
        self.phase = self.phase + self.phaseInc

        if self.phase > self.period:
            self.phase = self.phase%self.period

        if self.wavetype == 'sin':
            scale = math.sin(self.phase) * self.amount + self.offset
            return scale

        elif self.wavetype == 'square':
            if self.phase <= math.pi:
                scale = self.offset
            elif self.phase > math.pi:
                scale = self.amount + self.offset
            return scale


        elif self.wavetype == 'saw':
            scale = ((-1/math.pi)*self.phase + 1) * self.amount + self.offset
            return scale
