// redoing everything with analogRead we reach 100kHz and we have about 1 ms dead time
// with freerun we reach 330 kHz but we have about 5 ms dead time


// I have to push from circular buffer when writing to serial -- this could increase dead time
// now it prints rubbish

#define BUFFER_SIZE 666  // circular buffer (pre-trigger data) // 2 ms 
#define STORAGE_SIZE 2666 // array (post-trigger data) // 8 ms 
 
// baud rate is ignored for USB (always at 12 Mb/s); we just put a reasonable number
#define BAUD_RATE 115200 

#define ADC_RESOLUTION 12

// declarations ------------------------------------------------------------------
// struct representing one sample (I, Q and time values)
typedef struct {
  int I, Q; //2 bytes each
  unsigned int t;
} Sample;

// struct acting as storage for values collected before trigger
// it is a FIFO circular buffer https://en.wikipedia.org/wiki/Circular_buffer
typedef struct {
  Sample *buffer;
  int start, end, active;
} CircBuffer;

int i, j, ADC_CHANNELS, I_CHANNEL_NUM, Q_CHANNEL_NUM;
Sample *s; // pointer to a single sample
Sample none, trig_on; // NONE and TRIGGER_ON signals

CircBuffer *circ_buffer; // pointer to a single circ_buffer
Sample *storage, *to_write_samples; // pointers to the first element of arrays of samples
unsigned int acquisition_time_millis, start_millis, start_micros, start_sending_millis;


// methods for CircBuffer --------------------------------------------------------
void circ_buffer_setup(CircBuffer *s) {
  s->start = 0;
  s->end = 0;
  s->active = 0;
  s->buffer = (Sample *) malloc(sizeof(Sample)*BUFFER_SIZE);
}

void push(CircBuffer *s, Sample p) {
    s->buffer[s->end] = p;
    s->end = (s->end + 1) % BUFFER_SIZE;

    if (s->active < BUFFER_SIZE) s->active++;

    //Overwriting the oldest. Move start to next-oldest
    else s->start = (s->start + 1) % BUFFER_SIZE; 
}

Sample * pop(CircBuffer *s) {
    Sample *p;

    if (!s->active) return NULL;

    p = &(s->buffer[s->start]);
    s->start = (s->start + 1) % BUFFER_SIZE;

    s->active--;
    return p;
}


// trigger -----------------------------------------------------------------------
int trigger(Sample *s) {
    if (s->I > 1270){ // just a reasonable number for now
      return 1;
    }
    else return 0;
}


// in order to reduce dead time, data must be concatenated and sent to python all in one time 
void send_data_to_serial(CircBuffer *c, Sample *s) {
  Sample *olds;
  // moves the content of circ_buffer to the beginning of 'to_write_samples'
  for(j=0; j<BUFFER_SIZE; j++) {
    olds = pop(c);
    if (olds == NULL) break;
    s[j] = *olds;
  }

  // fills the rest of the first part of 'to_write_samples' with NONE signals
  for(; j<BUFFER_SIZE; j++) s[j] = none;
  
  // tramsmitted data are:
  /* 'active' elements from circ_buffer
   * ('BUFFER_SIZE' - 'active') NONEs
   * TRIG_ON signal
   * STORAGE_SIZE' elements read after trigger
  */

  // writes the data to serial
  // flushing before and after (don't know if useful)
  SerialUSB.flush();
  SerialUSB.write((byte*)s, sizeof(Sample)*(BUFFER_SIZE + STORAGE_SIZE + 1));
  SerialUSB.flush();
}


// Arduino setup, loop and acquire_data methods ----------------------------------------------------

/* Arduino due processor datasheet:
 * https://ww1.microchip.com/downloads/en/DeviceDoc/Atmel-11057-32-bit-Cortex-M3-Microcontroller-SAM3X-SAM3A_Datasheet.pdf
 * Arduino due unofficial pinout: http://www.robgray.com/temp/Due-pinout.pdf */

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
  circ_buffer = (CircBuffer*) malloc(sizeof(CircBuffer));
  circ_buffer_setup(circ_buffer);

  // initializing signals
  none = {0, 0, 0}; // very bad, think something with more sense !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
  trig_on = {4095, 4095, 0}; // very bad, think something with more sense !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

  // to increase serial communication speed, data are put in an array and sent all in one time
  /* to_write_samples structure:
   * Circular_buffer data, (NONE, ..., NONE), TRIGGER_ON, Storage data 
  */
  to_write_samples = (Sample*) malloc(sizeof(Sample)*(BUFFER_SIZE + STORAGE_SIZE + 1));

  // the TRIGGER_ON signal is put between circular_buffer and storage data
  to_write_samples[BUFFER_SIZE] = trig_on;

  // the buffer is put before the storage, as this is the order they must have when writing to serial
  storage = &(to_write_samples[BUFFER_SIZE + 1]);
}

void acquire_data(Sample *s) {
  // waits until ADC conversion is completed for both channels
  while((ADC->ADC_ISR & ADC_CHANNELS)!=ADC_CHANNELS);
  s->I = ADC->ADC_CDR[I_CHANNEL_NUM];  // read value of I
  s->Q = ADC->ADC_CDR[Q_CHANNEL_NUM];  // read value of Q
  s->t = (unsigned int)(micros() - start_micros); // time referred to acquisition start
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
      acquire_data(s); // reads I, Q and time and puts them in the s pointer
      if (trigger(s)) {
          storage[0] = *s; // saves the sample just read in the array
          for(i=1; i<STORAGE_SIZE; i++) { // reads and saves STORAGE_SIZE samples
              acquire_data(s); // reads I, Q and time and puts them in the s pointer
              storage[i] = *s;
          }
          start_sending_millis = millis();

          // debug - measuring dead time --------------------------------------------------
          send_data_to_serial(circ_buffer, to_write_samples);
          SerialUSB.flush();
          SerialUSB.println(millis()-start_sending_millis);
          SerialUSB.flush();
          // ------------------------------------------------------------------------------
      }
      else {
        push(circ_buffer, *s); // saves the sample just read in the circular buffer
      }
    }
  }
}
