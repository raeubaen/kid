#include <math.h>
#include <stdio.h>
#include <stdlib.h>

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
int sumI, sumQ, threshold, diffsumI, diffsumQ, sumI_old, sumQ_old;

double devst, sum, sumsq, diff;
FILE *f;

/* unsigned integers (4 byte sized)
 * store non-negative numbers up to 2**32 - 1
 * this data type is suitable to represent times,
 * as our acquisition window is 3 minutes (measured in microseconds),
 * that is less than the maximum representable value
 */

unsigned int acquisition_time_millis, start_sending_micros, end_millis, start_micros, time_interval;


Sample *s, *s_old;
Sample *_buffer, *_rolling; // pointer to the first element of an array of samples

CircBuffer *circ_buffer, *rolling; // pointer to a single circ_buffer

// method to set up the circular buffer
void circ_buffer_setup(CircBuffer *c, Sample *b) {
  c->end = 0;
  c->items = b; // inizializes the buffer to an array
}

// Arduino setup method -----------------------------------------------------------

void setup() {

  // allocating memory ------------------------------------------------------------
  rolling = (CircBuffer*) malloc(sizeof(CircBuffer));
  
  circ_buffer = (CircBuffer*) malloc(sizeof(CircBuffer));

  /* to increase serial communication speed, data are sent to python all in one time as an buffer
   * that shares the same memory with the circular buffer (to avoid having to copy it when writing to serial)
   */
  _buffer = (Sample*) malloc(sizeof(Sample)*(BUFFER_SIZE + 1));
  circ_buffer_setup(circ_buffer, _buffer);

  _rolling = (Sample*) malloc(sizeof(Sample)*11);
  circ_buffer_setup(rolling, _rolling);

  s = (Sample*) malloc(sizeof(Sample)); // pointer for a single sample (will be used in the loop)

  f = fopen("test.txt", "r");
}


// Methods for data handling -------------------------------------------------------------

// Method that acquires data, puts them in the buffer as a Sample and returns the pointer to it
Sample * acquire_data() {
  //  Sample *p = &(((Sample*)circ_buffer->item)[circ_buffer->end]); after declaring p, assigns to it the pointer to the Sample that will be filled
  Sample *p = &(((Sample*)circ_buffer->items)[circ_buffer->end]);
  // puts ahead the buffer index
  circ_buffer->end = (circ_buffer->end + 1) % BUFFER_SIZE;

  fscanf(f, "%d", &(p->I));
  fscanf(f, "%d", &(p->Q));
  if (fscanf(f, "%d", &(p->t)) == EOF) exit(1);

  return p;
}


void update_diffs(Sample *s) {

  s_old = &(circ_buffer->items[(circ_buffer->end - 10 + BUFFER_SIZE) % BUFFER_SIZE]);
  sumI += (s->I - s_old->I);
  sumQ += (s->Q - s_old->Q);

  rolling->items[rolling->end].I = sumI;
  rolling->items[rolling->end].Q = sumQ;
  
  Sample temp = rolling->items[rolling->end];

  rolling->end = (rolling->end + 1) % 11;

  diffsumI = sumI - rolling->items[rolling->end].I;
  diffsumQ = sumQ - rolling->items[rolling->end].Q;
}

// trigger method ------------------------------------------------------------------------
int trigger(Sample *s) {
    update_diffs(s);
    if ((abs(diffsumI) > threshold) || (abs(diffsumQ) > threshold)){
      return 1;
    }
    else return 0;
}

// Method to send one bunch of data to python
void send_data() {
  Sample *p;
  for(i=0; i<BUFFER_SIZE; i++){
    p = &(((Sample*)circ_buffer->items)[circ_buffer->end]);
    circ_buffer->end = (circ_buffer->end - 1 + BUFFER_SIZE) % BUFFER_SIZE;
    printf("%d %d %d\n", p->I, p->Q, p->t);
  }
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
int main() {
  // polls whether anything is ready on the read buffer
  // nothing happens until python writes the acquisition time (in s) to the serial

    setup();

    threshold = (int)(get_threshold()*10);

    printf("threshold: %d\n", threshold);

    while (1) {
      /* reads I, Q and time (in us),
       * saves them in the circular buffer as a Sample and returns the pointer to it
       */
      s = acquire_data();

      if (trigger(s)) {
          for(i=0; i<POST_TRIGGER_SAMPLES_NUM; i++) {
          update_diffs(acquire_data());
          }
          send_data();
      }
    }
}
