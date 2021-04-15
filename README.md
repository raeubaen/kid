funzionano:
tutti (miracolo)

testato in lab:
sending_strings (analogread)

dati:
sending_bytes:
triggered: 4.4 ms di tempo morto, legge a 333 kHz
continous: 2/3 ms di tempo morto, legge a 50kHz 
  (l'ho usato per registrare audio come test)

sending_strings:
triggered: 14 ms di tempo morto con analogread (130 kHz)
molto di più con freerun (333kHz)
continous: ...

logger_v3 legge tutto in una volta per ridurre il tempo morto
logger_v4 legge trigger per trigger (è più sicuro) e ha lo stesso tempo morto di v3
