/* Two channels analog reading with Arduino DUE at about 333 kHz using the ADC in free-running mode.
 * The ADC readings are recorded 2 ms before and 8 ms after an auto-trigger is activated.
*/


#define BUFFER_SIZE 3332 // number of samples captured in 10 ms, sampling every 3 us
#define POST_TRIGGER_SAMPLES_NUM 2667 // number of samples captured in 8 ms


// declarations ------------------------------------------------------------------

// struct representing one sample (containing values of I, Q and time)
typedef struct {
  int I, Q; // 4 bytes each
  unsigned int t; // 4 bytes
} Sample; // 12 bytes

// FIFO circular buffer for Sample objects: 
// see https://dl.acm.org/doi/pdf/10.5555/1074100.1074180
typedef struct {
  Sample *buffer;
  int end;
} CircBuffer;

// THRESHOLD is the noise RMS
int i, ADC_CHANNELS, I_CHANNEL_NUM, Q_CHANNEL_NUM, THRESHOLD = 0;

/* unsigned integers (4 byte sized)
 * store non-negative numbers up to 2**32 - 1
 * this data type is suitable to represent times,
 * as our acquisition window is 3 minutes (measured in microseconds),
 * that is less than the maximum representable value
 */
unsigned int acquisition_time_millis, start_sending_micros, end_millis, start_micros, time_interval;

Sample *s, *r; // pointer to a single sample
Sample *buffer; // pointer to the first element of an array of samples

CircBuffer *circ_buffer; // pointer to a single circ_buffer

// method to set up the circular buffer
void circ_buffer_setup(CircBuffer *c, Sample *b) {
  c->end = 0;
  c->buffer = b; // inizializes the buffer to an array
}

// Arduino setup method -----------------------------------------------------------

void setup() {

  // allocating memory --------------------------------------------------------
  circ_buffer = (CircBuffer*) malloc(sizeof(CircBuffer));

  /* to increase serial communication speed, data are sent to python all in one time as an buffer
   * that shares the same memory with the circular buffer (to avoid having to copy it when writing to serial)
   */
  buffer = (Sample*) malloc(sizeof(Sample)*(BUFFER_SIZE + 1));
  circ_buffer_setup(circ_buffer, buffer);

  /* initializes the last element of the buffer, that will be used to send to python the 
   *  amount of time (in us) needed to send a bunch of data (see send function)
   */
  buffer[BUFFER_SIZE] = {0, 0, 0};


  s = (Sample*) malloc(sizeof(Sample)); // pointer for a single sample (will be used in the loop)
  r = (Sample*) malloc(sizeof(Sample)); // pointer for a single sample (will be used in the loop)

  // manually setting registers for faster analog reading -----------------------------
  
  /* Arduino due processor datasheet:
   * https://ww1.microchip.com/downloads/en/DeviceDoc/Atmel-11057-32-bit-Cortex-M3-Microcontroller-SAM3X-SAM3A_Datasheet.pdf
   * Arduino due unofficial pinout: 
   * http://www.robgray.com/temp/Due-pinout.pdf */

  analogReadResolution(12);
  
  // sets free running mode (7th bit) and fast wake up (6th bit) 
  // see page 1333 of the datasheet
  ADC->ADC_MR |= 1 << 7 | 1 << 6;

  /* Setting the ADC to read the pins with I and Q signal.
   * see the pinout for the mapping between Arduino pins and ADC channels
   * ch7: A0, ..., ch0: A7 - ch10: A8, ..., ch13: A11
   */
  I_CHANNEL_NUM = 7; //A0
  Q_CHANNEL_NUM = 13; //A11

  // see page 1338 of the datasheet
  ADC_CHANNELS = (1 << I_CHANNEL_NUM) | (1 << Q_CHANNEL_NUM);
  
  ADC->ADC_CHER = ADC_CHANNELS; // enables channels
  ADC->ADC_CR |= 1 << 1; // begins ADC conversion (1st bit on)


  // initializing serial port ------------------------------------------------------------
  
  SerialUSB.begin(115200); // initializes the serial port and sets the baud rate
  // waits for the USB serial port to be connected or wait for python to open the serial port
  while (!SerialUSB);

}


// Methods for data handling -------------------------------------------------------------

// Method that acquires data, puts them in the buffer as a Sample and returns the pointer to it
Sample * acquire_data() {
  // after declaring p, assigns to it the pointer to the Sample that will be filled
  Sample *p = &(circ_buffer->buffer[circ_buffer->end]);
  // puts ahead the buffer index
  circ_buffer->end = (circ_buffer->end + 1) % BUFFER_SIZE;

  // waits until ADC conversion is completed for both channels
  while((ADC->ADC_ISR & ADC_CHANNELS)!=ADC_CHANNELS);
  p->I = ADC->ADC_CDR[I_CHANNEL_NUM];  // read value of I
  p->Q = ADC->ADC_CDR[Q_CHANNEL_NUM];  // read value of Q
  p->t = (unsigned int)(micros() - start_micros);

  return p;
}

// Method to send one bunch of data to python
void send_data() {
  start_sending_micros = micros();
  // in order to reduce dead time, data are sent to python all in one time as an array of bytes
  SerialUSB.write((byte*)buffer, sizeof(Sample)*(BUFFER_SIZE + 1));
  // saves the time needed by arduino to send data
  buffer[BUFFER_SIZE].Q = micros() - start_sending_micros;
}

// trigger method -----------------------------------------------------------------------
int trigger(Sample *s, Sample *r) {
    /*if (abs(s->I - r->I) > THRESHOLD){
      return 1;
    }
    else return 0;*/
    return 1;
}


// Arduino loop --------------------------------------------------------------------------
void loop() {
  // polls whether anything is ready on the read buffer
  // nothing happens until python writes the acquisition time (in s) to the serial
  if (SerialUSB.available() > 0) {
    // handshake - start ----------------------------
    
    //waiting a little time for arduino to be ready to receive data
    delay(100); // ms
    // reads from python the acquisition time in seconds
    acquisition_time_millis = SerialUSB.readString().toInt()*1000;
    // after receiving the value, sends back it in milliseconds to complete handshake
    SerialUSB.println(acquisition_time_millis);
    //waiting a little time for python to be ready to receive data
    delay(100); // ms
    
    // handshake - end -------------------------------
    
    end_millis = millis() + acquisition_time_millis;

    start_micros = micros();
    
    // starting acquisition (for an amount of time set by the acquisition_time variable)
    while (millis() < end_millis) {
      /* reads I, Q and time (in us),
       * saves them in the circular buffer as a Sample and returns the pointer to it
       */
      r = s;
      s = acquire_data();

      if (trigger(s, r)) {
          for(i=0; i<POST_TRIGGER_SAMPLES_NUM; i++) {
            acquire_data();
          }
          send_data();
      }
      
    }
  }
}
