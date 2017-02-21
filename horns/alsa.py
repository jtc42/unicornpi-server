import unicornhat as unicorn

import numpy as np
import math
import time
import audioop
import alsaaudio as aa
from struct import unpack


def init(self):

    self.colormode=0
    
    self.navg=6

    #INITIAL MATRICES

    self.matrix=[0,0,0,0,0,0,0,0]
    
    self.multiplier=2 #Depends on "normal" output volume from device
    self.weighting = [1,2,6,8,16,32,64,64] # Change these according to taste
    self.scalefactor = [x*self.multiplier for x in self.weighting]


    # Set up audio
    self.no_channels = 2
    self.sample_rate = 44100
    self.chunk = 256 # Sample size. Use a multiple of 8

    #Set sound card
    devname='Device,DEV=0'
    cardindex=1

    try:
        self.data_in = aa.PCM(aa.PCM_CAPTURE, aa.PCM_NORMAL,devname,cardindex) #DEV=0 device number, 1 card number, both found on 'arecord -l'
    except:
        self.enabled=False
        print "USB ALSA device disconnected. ALSA will be disabled"
        pass
    else:
        self.enabled=True
        print "USB ALSA device connected"
        self.data_in.setchannels(self.no_channels)
        self.data_in.setrate(self.sample_rate)
        self.data_in.setformat(aa.PCM_FORMAT_S16_LE)
        self.data_in.setperiodsize(self.chunk)
        
        self.volmix=aa.Mixer('Speaker',0,cardindex,devname)
        self.micmix=aa.Mixer('Mic',0,cardindex,devname)






#Calculate power
def piff(self, val):
    return int(2*self.chunk*val/self.sample_rate)

#Calculate levels
def calculate_levels(self, data, chunk, sample_rate):
    matrix=[0,0,0,0,0,0,0,0]
    # Convert raw data to numpy array
    data = unpack("%dh"%(len(data)/2),data)
    data = np.array(data, dtype='h')
    # Apply FFT - real data so rfft used
    fourier=np.fft.rfft(data)
    # Remove last element in array to make it the same size as chunk
    fourier=np.delete(fourier,len(fourier)-1)
    # Find average 'amplitude' for specific frequency ranges in Hz
    power = np.abs(fourier)
    matrix[0]=float(np.mean(power[piff(self,56):piff(self,156):1]))
    matrix[1]=float(np.mean(power[piff(self,156):piff(self,313):1]))
    matrix[2]=float(np.mean(power[piff(self,313):piff(self,625):1]))
    matrix[3]=float(np.mean(power[piff(self,625):piff(self,1250):1]))
    matrix[4]=float(np.mean(power[piff(self,1250):piff(self,2500):1]))
    matrix[5]=float(np.mean(power[piff(self,2500):piff(self,5000):1]))
    matrix[6]=float(np.mean(power[piff(self,5000):piff(self,10000):1]))
    matrix[7]=float(np.mean(power[piff(self,10000):piff(self,20000):1]))
    # Tidy up column values for the LED matrix. Applies weighting, multiplier factor, and should put all values roughly 0<n<8
    matrix=np.divide(np.multiply(matrix,self.scalefactor),1000000)
    # Set floor at 0 and ceiling at 8 for LED matrix. Values are floats so this won't significantly reduce effective "bit-depth"
    matrix=matrix.clip(0,8)
    
    #Remove NaN values from list, replace with zeros
    matrix=np.nan_to_num(matrix)
    #Convert numpy array to float list
    matrix=matrix.tolist()
    return matrix









def start(self):
    
    print "MODE:", self.colormode
    
    fftlist=[0,0,0,0,0,0,0,0]
    
    self.matrixav=[[0. for i in range(8)] for j in range(self.navg)]
    




def loop(self):
    """Note: The ugly use of exceptions here serves two pruposes:
        Firstly, it deals with any capture errors born out of asynchronous threading of ALSA.
        Secondly, if no audio device is present, it should catch most errors.
        The API will prevent commands from being sent to ALSA when it is disabled.
    """
    
    # Read data from device   
    try: #Catch read error
        self.l,self.data = self.data_in.read()
    except Exception as e: 
        print str(e)
    
    try: #Catch pause error
        self.data_in.pause(True) # Pause capture whilst RPi processes data
    except Exception as e:
        print str(e)
    
    #Set brightness
    self.scalefactor = [x*self.multiplier for x in self.weighting]
    
    if self.l: #If captured data exists
        try: #Catch frame error

            try: #Try to update matrix
                #Set self.matrix to newest FFT
                self.matrix=calculate_levels(self, self.data, self.chunk, self.sample_rate)
                
                #Enforce proper type for self.matrix
                for i in range(0,8):
                    self.matrix[i]=float(self.matrix[i])
            
            except Exception as e: 
                print str(e)
            

            #Move moving average list
            self.matrixav.append(self.matrix)
            del self.matrixav[0]
            
            #Initialise moving average
            average=[0,0,0,0,0,0,0,0]
            
            #Calculate moving average from moving average list
            for i in range(0,len(average)):
                for j in range(0,len(self.matrixav)):
                    average[i]+=self.matrixav[j][i]
                average[i]=average[i]/len(self.matrixav)
            
            
            
            #DRAW
            if self.colormode==1: #MODE ONE, SPECTRUM
                for i in range (0,8):
                    split=list(math.modf(average[i]))
                    split[1]=int(split[1])
                    
                    #Colours
                    rscale=1-(i/8.0)
                    gscale=abs(i-3.5)/3.5
                    bscale=(i/8.0)
                    
                    if split[1]>1: #Fills
                        for j in range (0,split[1]):
                            unicorn.set_pixel(7-i, j, int(rscale*255), int(gscale*255), int(bscale*255))
                            
                    if split[1] < 8: #Remainders
                        unicorn.set_pixel(7-i, split[1], int(rscale*255*split[0]), int(gscale*255*split[0]), int(bscale*255*split[0]))
                        
                    for j in range(split[1]+1,8): #Blanks
                        unicorn.set_pixel(7-i, j, 0, 0, 0)
                        
                        
                            
            elif self.colormode==2: #MODE TWO, OCEAN
                for i in range (0,8):
                    split=list(math.modf(average[i]))
                    split[1]=int(split[1])
                    
                    #Colours
                    bscale=1-(i/8.0)
                    gscale=(i/16.0)+0.5
                    
                    if split[1]>1: #Fills
                        for j in range (0,split[1]):
                            unicorn.set_pixel(7-i, j, 0, int(255*gscale*0.7), int(bscale*255))
                            
                    if split[1] < 8: #Remainders
                        unicorn.set_pixel(7-i, split[1], 0, int(255*gscale*split[0]), int(bscale*255*split[0]))
                        
                    for j in range(split[1]+1,8): #Blanks
                        unicorn.set_pixel(7-i, j, 0, 0, 0)
                        
                        
            
            elif self.colormode==3: #MODE THREE, PINKDROP
                for i in range (0,8):
                    split=list(math.modf(average[i]))
                    split[1]=int(split[1])
                    
                    #Colours
                    rscale=1-(i/8.0)
                    bscale=(i/8.0)
                    
                    if split[1]>1: #Fills
                        for j in range (0,split[1]):
                            unicorn.set_pixel(7-i, j, int(rscale*255), 0, int(bscale*255))
                            
                    if split[1] < 8: #Remainders
                        unicorn.set_pixel(7-i, split[1], int(rscale*255*split[0]), 0, int(bscale*255*split[0]))
                        
                    for j in range(split[1]+1,8): #Blanks
                        unicorn.set_pixel(7-i, j, 0, 0, 0)
                        
                        
                        
            elif self.colormode==4: #MODE FOUR, RAINBOW
                for i in range (0,8):
                    split=list(math.modf(average[i]))
                    split[1]=int(split[1])
                    
                    #Colours
                    rscale=1-(i/8.0)
                    gscale=1-(abs(i-3.5))/3.5
                    bscale=(i/8.0)
                    
                    if split[1]>1: #Fills
                        for j in range (0,split[1]):
                            unicorn.set_pixel(7-i, j, int(rscale*255), int(gscale*255), int(bscale*255))
                            
                    if split[1] < 8: #Remainders
                        unicorn.set_pixel(7-i, split[1], int(rscale*255*split[0]), int(gscale*255*split[0]), int(bscale*255*split[0]))
                        
                    for j in range(split[1]+1,8): #Blanks
                        unicorn.set_pixel(7-i, j, 0, 0, 0)
                      
                        
            elif self.colormode==5: #MODE TWO, CHILLI
                for i in range (0,8):
                    split=list(math.modf(average[i]))
                    split[1]=int(split[1])
                    
                    #Colours
                    rscale=1-((1-0.4)/8.0)*i
                    gscale=((1-0.4)/8.0)*i +0.4
                    
                    if split[1]>1: #Fills
                        for j in range (0,split[1]):
                            unicorn.set_pixel(7-i, j, int(255*rscale), int(gscale*255), 0)
                            
                    if split[1] < 8: #Remainders
                        unicorn.set_pixel(7-i, split[1], int(255*rscale*split[0]), int(gscale*255*split[0]), 0)
                        
                    for j in range(split[1]+1,8): #Blanks
                        unicorn.set_pixel(7-i, j, 0, 0, 0)
                        
            elif self.colormode==6: #MODE SIX, ZUNE
                for i in range (0,8):
                    split=list(math.modf(average[i]))
                    split[1]=int(split[1])
                    
                    #Colours
                    gval=np.clip(0.4082*i**2 - 18.571*i + 120, 0, 255)
                    bval=np.clip(2.2857*i**2 - 1.7143*i + 30, 0, 255)
                    
                    if split[1]>1: #Fills
                        for j in range (0,split[1]):
                            unicorn.set_pixel(7-i, j, int(240), int(gval), int(bval))
                            
                    if split[1] < 8: #Remainders
                        unicorn.set_pixel(7-i, split[1], int(240*split[0]), int(gval*split[0]), int(bval*split[0]))
                        
                    for j in range(split[1]+1,8): #Blanks
                        unicorn.set_pixel(7-i, j, 0, 0, 0)
                        
                        
            elif self.colormode==7: #MODE SEVEN, ZUNE 2
                for i in range (0,8):
                    split=list(math.modf(average[i]))
                    split[1]=int(split[1])
                    
                    def g(j):
                        return np.clip(0.4082*j**2 - 18.571*j + 120, 0, 255)
                    def b(j):
                        return np.clip(1.2245*j**2 + 5.7143*j + 30, 0, 255)
                    
                    if split[1]>1: #Fills
                        for j in range (0,split[1]):
                            #Colours
                            gval=g(j)
                            bval=b(j)
                            
                            unicorn.set_pixel(7-i, j, int(240), int(gval), int(bval))
                            
                    if split[1] < 8: #Remainders
                        #Colours
                        gval=g(split[1])
                        bval=b(split[1])
                        
                        unicorn.set_pixel(7-i, split[1], int(240*split[0]), int(gval*split[0]), int(bval*split[0]))
                        
                    for j in range(split[1]+1,8): #Blanks
                        unicorn.set_pixel(7-i, j, 0, 0, 0)
            
            
                        
            else: #MODE ZERO, CLASSIC
                for i in range (0,8):
                    split=list(math.modf(average[i]))
                    split[1]=int(split[1])
                    
                    def r(j):
                        return ((1-0.5)/7)*j +0.5
                    def g(j):
                        return 1.0-(j/12.0)
                    
                    if split[1]>1: #Fills
                        for j in range (0,split[1]):
                            #Colours
                            rscale=r(j)
                            gscale=g(j)
                            
                            unicorn.set_pixel(7-i, j, int(rscale*255), int(gscale*255), 0)
                            
                    if split[1] < 8: #Remainders
                        #Colours
                        rscale=r(split[1])
                        gscale=g(split[1])
                        
                        unicorn.set_pixel(7-i, split[1], int(rscale*255*split[0]), int(gscale*255*split[0]), 0)
                        
                    for j in range(split[1]+1,8): #Blanks
                        unicorn.set_pixel(7-i, j, 0, 0, 0)

            unicorn.show()

        except Exception as e:
            print str(e)

    
    time.sleep(0.001) # Rest

    try: #Catch unpause error
        self.data_in.pause(False) # Resume capture
    except:
        print "Unpausing read failed"
