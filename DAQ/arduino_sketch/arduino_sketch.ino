  /* Two channels analog reading with Arduino DUE at about 333 kHz using the ADC in free-running mode.
   The ADC readings are recorded 2 ms before and 8 ms after an auto-trigger is activated.
*/

#include <math.h>

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
  Sample *items;
  int end;
} CircBuffer;

// THRESHOLD will be used for the trigger
int i, j;
int ADC_CHANNELS, I_CHANNEL_NUM, Q_CHANNEL_NUM;
int sumI, sumQ, threshold, diffsumI, diffsumQ, sumI_old, sumQ_old;

double devst, sum, sumsq, diff;

/* unsigned integers (4 byte sized)
   store non-negative numbers up to 2**32 - 1
   this data type is suitable to represent times,
   as our acquisition window is 3 minutes (measured in microseconds),
   that is less than the maximum representable value
*/
unsigned int acquisition_time_millis, start_sending_micros, end_millis, start_micros, t1, t2;

Sample *s, *s_old;
Sample *_buffer, *_rolling; // pointer to the first element of an array of samples

CircBuffer *circ_buffer, *rolling;

// method to set up the circular buffer
void circ_buffer_setup(CircBuffer*c, Sample *b) {
  c->end = 0;
  c->items = b; // inizializes the buffer to an array
}

// Arduino setup method -----------------------------------------------------------

void setup() {

  // allocating memory ------------------------------------------------------------
  rolling = (CircBuffer*) malloc(sizeof(CircBuffer));

  circ_buffer = (CircBuffer*) malloc(sizeof(CircBuffer));

  /* to increase serial communication speed, data are sent to python all in one time as an buffer
     that shares the same memory with the circular buffer (to avoid having to copy it when writing to serial)
  */
  _buffer = (Sample*) malloc(sizeof(Sample) * (BUFFER_SIZE + 1));
  circ_buffer_setup(circ_buffer, _buffer);

  _rolling = (Sample*) malloc(sizeof(Sample) * 10);
  circ_buffer_setup(rolling, _rolling);

  /* initializes the last element of the buffer, that will be used to send to python the
      amount of time (in us) needed to send a bunch of data (see send function)
  */
  _buffer[BUFFER_SIZE] = {0, 0, 0};

  s = (Sample*) malloc(sizeof(Sample)); // pointer for a single sample (will be used in the loop)

  // manually setting registers for faster analog reading -----------------------------

  /* Arduino due processor datasheet:
     https://ww1.microchip.com/downloads/en/DeviceDoc/Atmel-11057-32-bit-Cortex-M3-Microcontroller-SAM3X-SAM3A_Datasheet.pdf
     Arduino due unofficial pinout:
     http://www.robgray.com/temp/Due-pinout.pdf */

  analogReadResolution(12);

  // sets free running mode (7th bit) and fast wake up (6th bit)
  // see page 1333 of the datasheet
  ADC->ADC_MR |= 1 << 7 | 1 << 6;

  /* Setting the ADC to read the pins with I and Q signal.
     see the pinout for the mapping between Arduino pins and ADC channels
     ch7: A0, ..., ch0: A7 - ch10: A8, ..., ch13: A11
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
  Sample *p = &(circ_buffer->items[circ_buffer->end]);
  // puts ahead the buffer index
  circ_buffer->end = (circ_buffer->end + 1) % BUFFER_SIZE;

  // waits until ADC conversion is completed for both channels
  while ((ADC->ADC_ISR & ADC_CHANNELS) != ADC_CHANNELS);
  p->I = ADC->ADC_CDR[I_CHANNEL_NUM];  // read value of I
  p->Q = ADC->ADC_CDR[Q_CHANNEL_NUM];  // read value of Q
  p->t = (unsigned int)(micros() - start_micros);
  return p;
}

// Method to send one bunch of data to python
void send_data() {
  start_sending_micros = micros();
  // in order to reduce dead time, data are sent to python all in one time as an array of bytes
  SerialUSB.write((byte*)_buffer, sizeof(Sample) * (BUFFER_SIZE + 1));
  // saves the time needed by arduino to send data
  _buffer[BUFFER_SIZE].Q = micros() - start_sending_micros;
}

void update_diffs(Sample *s) {

  s_old = &(circ_buffer->items[(circ_buffer->end - 10 + BUFFER_SIZE) % BUFFER_SIZE]);
  sumI += (s->I - s_old->I);
  sumQ += (s->Q - s_old->Q);

  rolling->items[rolling->end].I = sumI;
  rolling->items[rolling->end].Q = sumQ;
  
  rolling->end = (rolling->end + 1) % 11;

  diffsumI = sumI - rolling->items[rolling->end].I;
  diffsumQ = sumQ - rolling->items[rolling->end].Q;
}

int trigger(Sample *s) {
  update_diffs(s);
  if ((abs(diffsumI) > threshold) || (abs(diffsumQ) > threshold)) {
    return 1;
  }
  else return 0; /////////////////// OCCHIOOOOOOOOOOOOOOOOOO - così è attivo - per disattivarlo mettere 1
}

void initialize_rolling_means() {

  for (i = 0; i < 11; i++) {
    // puts ahead the buffer index
    sumI = 0;
    sumQ = 0;
    for (j = 0; j < 10; j++) {
      s = &(circ_buffer->items[(circ_buffer->end - i - j + BUFFER_SIZE) % BUFFER_SIZE]);
      sumI += s->I;
      sumQ += s->Q;
    }
    rolling->items[rolling->end].I = sumI;
    rolling->items[rolling->end].Q = sumQ;

    rolling->end = (rolling->end - 1 + 11) % 11;
  }
  
  rolling->end = (rolling->end + 10) % 11;
}

double get_threshold() {
  sum = 0;
  sumsq = 0;
  int n = BUFFER_SIZE;
  for (i = 0; i < 40; i++) {
    acquire_data();
  }
  initialize_rolling_means();
  s = acquire_data();
  update_diffs(s);

  for (i = 0; i < n; i++) {
    s = acquire_data();
    update_diffs(s);
    diff = (double)diffsumI / 10;
    sum += diff;
    sumsq += diff * diff;
  }

  devst = sqrt((double)sumsq / n - (double)sum * sum / (n * n));
  return devst * 5.8;
}

// Arduino loop -------------------------------------------------------------------------
void loop() {
  // polls whether anything is ready on the read buffer
  // nothing happens until python writes the acquisition time (in s) to the serial
  if (SerialUSB.available() > 0) {
    // handshake - start ----------------------------

    //waiting a little time for arduino to be ready to receive data
    delay(100); // ms
    // reads from python the acquisition time in seconds
    acquisition_time_millis = SerialUSB.readString().toInt() * 1000;

    threshold = 160; //(int)(get_threshold() * 10); // scommentare per avere la soglia mobile
    SerialUSB.println(threshold);

    //waiting a little time for python to be ready to receive data
    delay(100); // ms

    // handshake - end -------------------------------

    end_millis = millis() + acquisition_time_millis;

    start_micros = micros();

    // starting acquisition (for an amount of time set by the acquisition_time variable)
    while (millis() < end_millis) {
      /* reads I, Q and time (in us),
         saves them in the circular buffer as a Sample and returns the pointer to it
      */
      s = acquire_data();

      if (trigger(s)) {
        for (i = 0; i < POST_TRIGGER_SAMPLES_NUM; i++) {
          update_diffs(acquire_data());
        }
        send_data();
      }

    }
  }
}
