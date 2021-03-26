
#define BUFFER_SIZE 200  //BUFFER CIRCOLARE
#define STORAGE_SIZE 800 //ARRAY
#define BAUD_RATE 9600
#define ADC_RESOLUTION 12

typedef struct {
  int I, Q; //2 bytes each
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
    if (s->I > 0){
      return 1;
    }
    else return 0;
}

int i, triggering = 0;
Sample *s, *olds;
CircBuffer *circ_buffer;
Sample *storage;
String strOut = "";

void setup()
{
  SerialUSB.begin(BAUD_RATE);                           // initialize the serial port
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
  strOut->concat('\n');
}

void send_data_to_serial(CircBuffer* c, Sample* s){ // i dati vanno concatenati e inviati tutti assieme per diminuire il tempo morto
  Sample *olds;
  int j;
  strOut = "";
  //strOut.concat("Data before trigger:\n");
  for(j=0; j<BUFFER_SIZE; j++){ // saving BUFFER_SIZE data points before trigger
    olds = pop(c);
    if(olds == NULL) break; // if the buffer is empty
    concat_to_str(&strOut, olds);
  }
  //strOut.concat("Data after trigger:\n");
  for(j=0; j<STORAGE_SIZE; j++){ // saving BUFFER_SIZE data points before trigger
    concat_to_str(&strOut, &(s[j]));
  }
  SerialUSB.print(strOut);
}

void loop() {
  s->I = analogRead(A0);                        // read value A0
  s->Q = analogRead(A1);                        // read value A1
  if (trigger(s)){
      //SerialUSB.print("TRIGGER ON - time:");
      //SerialUSB.println(micros());
      i = 0;
      storage[i] = *s;
      for(i=1; i<STORAGE_SIZE; i++){
          s->I = analogRead(A0);                        // read value A0
          s->Q = analogRead(A1);
          storage[i] = *s;
      }
      //SerialUSB.print("END- time:");
      //SerialUSB.println(micros());
      send_data_to_serial(circ_buffer, storage);
  }
  else {
    push(circ_buffer, *s);
  }
}
