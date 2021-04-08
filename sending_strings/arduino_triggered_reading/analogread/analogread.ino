#define BUFFER_SIZE 200  // circular buffer (pre-trigger data)
#define STORAGE_SIZE 800 // array (post-trigger data)

// baud rate is ignored for USB (always at 12 Mb/s); we just put a reasonable number
#define BAUD_RATE 115200 

#define ADC_RESOLUTION 12

// declarations ------------------------------------------------------------------
// struct representing one sample (I, Q and time values)
typedef struct {
  int I, Q; //2 bytes each
} Sample;

// struct acting as storage for values collected before trigger
// it is a FIFO circular buffer https://en.wikipedia.org/wiki/Circular_buffer
typedef struct {
  Sample *buffer;
  int start, end, active;
} CircBuffer;

int i, j, ADC_CHANNELS, I_CHANNEL_NUM, Q_CHANNEL_NUM;
Sample *s; // single pointer to a sample
CircBuffer *circ_buffer;
Sample *storage; // pointer to the first element of an array of samples
String strOut = "";
unsigned long acquisition_time_millis, start_millis, start_micros; // in ms


// methods for CircBuffer --------------------------------------------------------
void circ_buffer_setup(CircBuffer *s) {
  s->start = 0;
  s->end = 0;
  s->active = 0;
  s->buffer = (Sample *) malloc(sizeof(Sample) * BUFFER_SIZE);
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
    if (s->I > 1285){ // just a reasonable number for now
      return 1;
    }
    else return 0;
}


// serial communication methods --------------------------------------------------
void concat_to_str(String *strOut, Sample *s) {
  strOut->concat(s->I); 
  strOut->concat(',');
  strOut->concat(s->Q);
  strOut->concat('\n');
}

// in order to reduce dead time, data must be concatenated and sent to python all in one time 
void send_data_to_serial(CircBuffer* c, Sample* s) {
  unsigned long sending_time_start = micros();
  Sample *olds;
  strOut.concat("\n#Data before trigger:\n");
  for(j=0; j<BUFFER_SIZE; j++){ // saving BUFFER_SIZE data points before trigger
    olds = pop(c);
    if(olds == NULL) break; // if the buffer is empty
    concat_to_str(&strOut, olds);
  }
  strOut.concat("#Data after trigger:\n");
  for(j=0; j<STORAGE_SIZE; j++){ // saving STORAGE_SIZE data points after trigger
    concat_to_str(&strOut, &(s[j]));
  }
  strOut.concat("\n\n");
  SerialUSB.flush();
  SerialUSB.print(strOut); // doesn't wait for write to complete before moving on
  SerialUSB.flush();
  SerialUSB.println(micros() - sending_time_start); // to evaluate dead time
  SerialUSB.println(micros() - sending_time_start); // to evaluate dead time
}


// Arduino setup, loop and acquire_data methods ----------------------------------------------------

/* Arduino due processor datasheet:
 * https://ww1.microchip.com/downloads/en/DeviceDoc/Atmel-11057-32-bit-Cortex-M3-Microcontroller-SAM3X-SAM3A_Datasheet.pdf
 * Arduino due unofficial pinout: http://www.robgray.com/temp/Due-pinout.pdf */

void setup() {
  analogReadResolution(ADC_RESOLUTION);

  // initialising serial port ------------------------------------------------------------
  SerialUSB.begin(BAUD_RATE); // initialize the serial port
  while (!SerialUSB); // wait for USB serial port to be connected or wait for pc program to open the serial port

  // allocating space for pointers -------------------------------------------------------
  s = (Sample*) malloc(sizeof(Sample)); // pointer for a single sample 
  circ_buffer = (CircBuffer*) malloc(sizeof(CircBuffer));
  circ_buffer_setup(circ_buffer);  
  storage = (Sample*) malloc(sizeof(Sample)*STORAGE_SIZE); // pointer for a sample array
}

void acquire_data(Sample *s) {
  s->I = analogRead(A0);  // read value of I
  s->Q = analogRead(A1);  // read value of Q
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
          strOut = "trigger on at time: ";
          strOut.concat(micros()-start_micros);
          storage[0] = *s; // saves the sample just read in the array
          for(i=1; i<STORAGE_SIZE; i++) { // reads and saves STORAGE_SIZE samples
              acquire_data(s); // reads I, Q and time and puts them in the s pointer
              storage[i] = *s;
          }
          strOut.concat("trigger off at time: ");
          strOut.concat(micros()-start_micros);
          send_data_to_serial(circ_buffer, storage);
      }
      else {
        push(circ_buffer, *s); // saves the sample just read in the circular buffer
      }
    }
  }
}
