
#define BUFFER_SIZE 200  //BUFFER CIRCOLARE
#define STORAGE_SIZE 800 //ARRAY
#define BAUD_RATE 9600
#define ADC_RESOLUTION 12

typedef struct {
  int I, Q; //2 bytes each
  unsigned long t;
} Sample;

// struct acting as storage for values collected before trigger
// it is a FIFO circular buffer
typedef struct {
  Sample *buffer;
  int start, end, active;
} CircBuffer;

// methods for CircBuffer ---------------------------------------------
void circ_buffer_setup(CircBuffer *s){
  s->start = 0;
  s->end = 0;
  s->active = 0;
  s->buffer = (Sample *) malloc(sizeof(Sample) * BUFFER_SIZE);
}

void push(CircBuffer *s, Sample p)
{
    s->buffer[s->end] = p;
    s->end = (s->end + 1) % BUFFER_SIZE;

    if (s->active < BUFFER_SIZE) s->active++;
    else s->start = (s->start + 1) % BUFFER_SIZE; //Overwriting the oldest. Move start to next-oldest
}

Sample * pop(CircBuffer *s)
{
    Sample *p;

    if (!s->active) return NULL;

    p = &(s->buffer[s->start]);
    s->start = (s->start + 1) % BUFFER_SIZE;

    s->active--;
    return p;
}

int trigger(Sample *s){
    if (s->I > 1267){ // just a reasonable number
      return 1;
    }
    else return 0;
}

int i, triggering = 0;
Sample *s, *olds;
CircBuffer *circ_buffer;
Sample *storage;
String strOut = "";
long acquisition_time; // in ms

void setup()
{

  // manually set registers for faster analog reading than the normal arduino methods
  ADC->ADC_MR |= 0xC0; // set free running mode (page 1333 of the Sam3X datasheet)
  ADC -> ADC_CHER = 0xC0;   // enable channels  (see page 1338 of datasheet) on adc 7,6,5,4,3,2 (pin A0-A5)
                       // see also http://www.arduino.cc/en/Hacking/PinMappingSAM3X for the pin mapping between Arduino names and SAM3X pin names
  //ADC->ADC_CHDR = 0b1111111111111100; // disable all other channels
  ADC->ADC_CR=2;       // begin ADC conversion*/
  
  // initialise serial port
  SerialUSB.begin(BAUD_RATE); // initialize the serial port
  // baud rate is ignored for USB - always at 12 Mb/s - we just put a reasonable number
  while (!SerialUSB); // wait for USB serial port to be connected - wait for pc program to open the serial port
  
  analogReadResolution(ADC_RESOLUTION);
  s = (Sample*) malloc(sizeof(Sample));
  olds = (Sample*) malloc(sizeof(Sample));
  circ_buffer = (CircBuffer*) malloc(sizeof(CircBuffer));
  circ_buffer_setup(circ_buffer);  
  storage = (Sample*) malloc(sizeof(Sample)*STORAGE_SIZE); 
}

void concat_to_str(String *strOut, Sample *s){
  strOut->concat(s->I); 
  strOut->concat(',');
  strOut->concat(s->Q);
  strOut->concat(',');
  strOut->concat(s->t);
  strOut->concat('\n');
}

void send_data_to_serial(CircBuffer* c, Sample* s){ // i dati vanno concatenati e inviati tutti assieme per diminuire il tempo morto
  Sample *olds;
  int j;
  strOut = "";
  strOut.concat("#Data before trigger:\n");
  for(j=0; j<BUFFER_SIZE; j++){ // saving BUFFER_SIZE data points before trigger
    olds = pop(c);
    if(olds == NULL) break; // if the buffer is empty
    concat_to_str(&strOut, olds);
  }
  strOut.concat("#Data after trigger:\n");
  for(j=0; j<STORAGE_SIZE; j++){ // saving BUFFER_SIZE data points before trigger
    concat_to_str(&strOut, &(s[j]));
  }
  SerialUSB.flush();
  SerialUSB.print(strOut); // doesn't wait for write to complete before moving on
  SerialUSB.print("stop");
  SerialUSB.flush();
}

void loop() {
  int incoming = 0;
  if (SerialUSB.available() > 0) // polls whether anything is ready on the read buffer - nothing happens until there's something there
  {
    // handshake --------------------
    delay(100); // ms
    acquisition_time = SerialUSB.readString().toInt()*1000; // in ms
    // after data received, send the same back
    SerialUSB.println(acquisition_time);
    
    //wait a little time for python to be ready to receive data - (not sure if this is really necessary)
    delay(100); // ms
    // handshake ----------------------
    
    // measure start time - then acquire data for an amount of time set by the acquisition_time variable
    unsigned long start_time = millis();
    while (millis() < (start_time + acquisition_time))
    {
      while((ADC->ADC_ISR & 0x80)==0); 
      s->I = ADC->ADC_CDR[7];                        // read value A0
      s->Q = ADC->ADC_CDR[6];
      s->t = micros();
      if (trigger(s)){
          //SerialUSB.print("#TRIGGER ON - time:");
          //SerialUSB.println(micros());
          i = 0;
          storage[i] = *s;
          for(i=1; i<STORAGE_SIZE; i++){
              while((ADC->ADC_ISR & 0x80)==0); 
              s->I = ADC->ADC_CDR[7];                        // read value A0
              s->Q = ADC->ADC_CDR[6];
              s->t = micros();
              storage[i] = *s;
          }
          //SerialUSB.print("#END- time:");
          //SerialUSB.println(micros());
          send_data_to_serial(circ_buffer, storage);
      }
      else {
        push(circ_buffer, *s);
      }
    }
  }
}
