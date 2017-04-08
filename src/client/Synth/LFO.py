import math


from Synth.osc import wtOsc
from Synth.envelope import envelope
import Synth.filt

class lfo:
    '''
    Don't use yet, one that works is in the synth to demonstate
    '''

    def __init__(self, samplerate=44100, device=None, control=None, amount=0.75, wavetype='sin', speed=1):
        self.samplerate = samplerate
        self.device = device
        self.control = control
        self.speed = speed
        self.period = 2 * math.pi
        self.phase = 0
        self.set_speed(self.speed)
        self.amount = amount
        self.wavetype = wavetype
        self.enabled = True


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
        if self.enabled == False:
            return

        if control or device == None:
            return

        scale = self.genOutput()
        print(scale)

        if isinstance(device, wtOsc):
            if control == 'wavtable position':
                delta = (device.wavetablepos_max*scale)
                delta = delta - (delta%device.detune_step)

                if device.wavetablepos > device.wavetablepos_max:
                    device.wavetablepos == device.wavetablepos_max

                elif device.wavetablepos < device.wavetablepos_min:
                    device.wavetablepos == device.wavetablepos_min

                else:
                    device.wavetablepos = device.wavetablepos_max + delta


            if control == 'detune':
                delta = (device.detune_max*scale)
                delta = delta - (delta%device.detune_step)

                if device.detune > device.detune_max:
                    device.detune == device.detune_max

                elif device.detune < device.detune_min:
                    device.detune == device.detune_min

                else:
                    device.detune = device.detune + delta

            if control == 'volume':
                scale = (scale/2) + 0.5
                device.volume = scale


        if isinstance(device, envelope):
            if control == 'attack':
                delta = (device.attack_max*scale)
                time = device.attacksamples/device.samplerate
                new_value = time + delta


                if new_value > device.attack_max:
                    device.set_attack(device.attack_max)

                if new_value < device.attack_min:
                    device.set_attack(device.attack_min)


                else:
                    device.set_attack(new_value)

            if control == 'decay':
                delta = (device.decay_max*scale)
                time = device.decaysamples/device.samplerate
                new_value = time + delta

                if new_value > device.decay_max:
                    device.set_decay(device.decay_max)

                if new_value < device.decay_min:
                    device.set_decay(device.decay_min)


                else:
                    device.set_decay(new_value)

            if control == 'sustain':
                delta = (device.sustain_max*scale)
                time = device.sustainsamples/device.samplerate
                new_value = time + delta


                if new_value > device.sustain_max:
                    device.set_sustain(device.decay_max, device.sustain_amp)

                if new_value < device.sustain_min:
                    device.set_sustain(device.sustain_min, device.sustain_amp)


                else:
                    device.set_sustain(new_value, device.sustain_amp)

            if control == 'release':
                delta = (device.release_max*scale)
                time = device.releasesamples/device.samplerate
                new_value = time + delta


                if new_value > device.release_max:
                    device.set_release(device.release_max)

                if new_value < device.sustain_min:
                    device.set_release(device.release_min)


                else:
                    device.set_release(new_value)

            if control == 'sustainamp':
                scale = (scale/2) + 0.5
                device.set_sustain(device.sustainsamples/device.samplerate, scale)


        if isinstance(device, Synth.filt.filter):

            if control == 'cutoff':
                if device.filtertype == 'Low Pass':
                    delta = (device.set_cutoff_lowpass_max*scale)
                    old = device.cutoff_lp
                    new_value = old + delta

                    if new_value > device.set_cutoff_lowpass_max:
                        device.set_cutoff_lowpass(device.set_cutoff_lowpass_max)

                    if new_value < device.set_cutoff_lowpass_min:
                        device.set_cutoff_lowpass(device.set_cutoff_lowpass_min)


                    else:
                        device.set_cutoff_lowpass(new_value)

                if device.filtertype == 'High Pass':
                    delta = (device.set_cutoff_highpass_max*scale)
                    old = device.cutoff_hp
                    new_value = old + delta

                    if new_value > device.set_cutoff_highpass_max:
                        device.set_cutoff_highpass(device.set_cutoff_highpass_max)

                    if new_value < device.set_cutoff_highpass_max:
                        device.set_cutoff_highpass(device.set_cutoff_highpass_min)


                    else:
                        device.set_cutoff_highpass(new_value)






    def genOutput(self):
        '''
        '''
        self.phase = self.phase + self.phaseInc

        if self.phase > self.period:
            self.phase = self.phase%self.period

        if self.wavetype == 'sin':
            scale = math.sin(self.phase) * self.amount
            return scale

        elif self.wavetype == 'square':
            if phase <= math.pi:
                scale = 0
            elif phase > math.pi:
                scale = self.amount
            return scale


        elif self.wavetype == 'saw':
            scale = ((-1/math.pi)*self.phase + 1) * self.amount
            return scale