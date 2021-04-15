// redoing everything with analogRead we reach 100kHz and we have about 1 ms dead time
// with freerun we reach 330 kHz but we have about 5 ms dead time

#define STORAGE_SIZE 1000 // array (post-trigger data)

// baud rate is ignored for USB (always at 12 Mb/s); we just put a reasonable number
#define BAUD_RATE 115200

#define ADC_RESOLUTION 12

// declarations ------------------------------------------------------------------
// struct representing one sample (I, Q and time values)
typedef struct {
  int I, Q;
  unsigned int t;
} Sample;

int i, j, ADC_CHANNELS, I_CHANNEL_NUM, Q_CHANNEL_NUM;
Sample *s; // single pointer to a sample
Sample *storage; // pointer to the first element of an array of samples
unsigned int acquisition_time_millis, start_millis, start_micros; // in ms

// in order to reduce dead time, data must be concatenated and sent to python all in one time 
void send_data_to_serial(Sample* storage) {
  // converts to byte pointes and writes to serial all in one time
  SerialUSB.write((byte*)storage, sizeof(Sample)*STORAGE_SIZE);
}


// Arduino setup, loop and acquire_data methods ----------------------------------------------------

/* Arduino due processor datasheet:
 * https://ww1.microchip.com/downloads/en/DeviceDoc/Atmel-11057-32-bit-Cortex-M3-Microcontroller-SAM3X-SAM3A_Datasheet.pdf
 * Arduino due unofficial pinout: 
 * http://www.robgray.com/temp/Due-pinout.pdf */

void setup() {
  analogReadResolution(ADC_RESOLUTION);

  // manually setting registers for faster analog reading -----------------------------
  // set free running mode (7th bit) and fast wake up (6th bit) (page 1333 of the Sam3X datasheet)
  ADC->ADC_MR |= 1 << 7 | 1 << 6; 

  // see the pinout for the mapping between Arduino pins and ADC channels
  // ch7: A0, ..., ch0: A7 - ch10: A8, ..., ch13: A11 // is it a joke?
  I_CHANNEL_NUM = 7; //A0
  Q_CHANNEL_NUM = 13; //A11
  
  ADC_CHANNELS = (1 << I_CHANNEL_NUM) | (1 << Q_CHANNEL_NUM); // (see page 1338 of datasheet)
  
  ADC->ADC_CHER = ADC_CHANNELS;   // enable channels  
  ADC->ADC_CR = 1 << 1; // begin ADC conversion (1st bit on)

  // initialising serial port ------------------------------------------------------------
  SerialUSB.begin(BAUD_RATE); // initialize the serial port
  while (!SerialUSB); // wait for USB serial port to be connected or wait for pc program to open the serial port

  // allocating space for pointers -------------------------------------------------------
  s = (Sample*) malloc(sizeof(Sample)); // pointer for a single sample 
  storage = (Sample*) malloc(sizeof(Sample)*STORAGE_SIZE); // pointer for a sample array
}

void acquire_data(Sample *s) {
  // waits until ADC conversion is completed for both channels
  while((ADC->ADC_ISR & ADC_CHANNELS)!=ADC_CHANNELS);
  s->I = ADC->ADC_CDR[I_CHANNEL_NUM];  // read value of I
  s->Q = ADC->ADC_CDR[Q_CHANNEL_NUM];  // read value of Q
  s->t = (unsigned int)(micros() - start_micros); // time referred to acquisition start
  delayMicroseconds(17); // to sample audio at 50kHz 
}

void loop() {
  // polls whether anything is ready on the read buffer
  // nothing happens until python writes the acquisition_time (in s) to serial
  if (SerialUSB.available() > 0) {
    // handshake - start -----------------------------------------------------------------
    //waiting a little time for arduino to be ready to receive data - (not sure if this is really necessary)
    delay(100); // ms
    acquisition_time_millis = SerialUSB.readString().toInt()*1000;
    // after data received, send the same back to complete handshake
    SerialUSB.println(acquisition_time_millis);
    
    //waiting a little time for python to be ready to receive data - (not sure if this is really necessary)
    delay(100); // ms
    // handshake - end --------------------------------------------------------------------
    
    // measuring acquisition start time
    start_millis = millis();
    start_micros = micros();
    
    // starting acquisition (for an amount of time set by the acquisition_time variable)
    while (millis() < (start_millis + acquisition_time_millis)) {
      for(i=0; i<STORAGE_SIZE; i++) { // reads and saves STORAGE_SIZE samples
          acquire_data(s); // reads I, Q and time and puts them in the s pointer
          storage[i] = *s;
      }
      send_data_to_serial(storage);
    }
  }
}
