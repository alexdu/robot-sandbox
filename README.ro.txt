robot-sandbox

Simulator pentru brate robotice articulate

Aceasta versiune (lite) este doar pentru cei care au deja instalat 
Python si bibliotecile necesare. 

Pentru versiunea "unzip and run" descarcati ramura MASTER.


Se instaleaza mediul de dezvoltare si bibliotecile de mai jos:
- Python 2.5 sau 2.6 
- ipython
- cgkit
- pyode (din SVN; trebuie compilat impreuna cu ODE)
- numpy
- pygame
- PyProtocols (from source, pyhon setup.py --without-speedups install)
- pyreadline

Pornirea programului:
cd sim-files
python main.py


------------------------------------------------
Compilare PyODE pe Windows (optional, dar greu!):
- ODE (surse)
- pyrex
- instructiuni pentru compilarea ODE la http://demura.net/tutorials/ode2 
  * merge cu Google Translate
  Eu am compilat cu mingw
- apoi, pentru compilarea PyODE:
     - varianta binara a lui ODE trebuie sa fie in ode-x.xx.x\lib\releaselib\ode.dll
       (daca nu e acolo, se muta manual)
     - se modifica in setup.py calea spre folderul cu ODE: c:\path\to\ode-x.xx.x
     - se comenteaza setup.py comenzile specifice MSVC (CC_ARGS si LINK_ARGS)
     - se modifica in setup.py comanda pyrex in pyrex.py
     - in folderul cu PyODE:
	* setup.py build
	* python setup.py install



