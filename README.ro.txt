robot-sandbox

Simulator pentru brate robotice articulate


INSTALARE:


WINDOWS: 

unzip and run :)

Se pot modifica sursele din sim-files/*.py
Programele robot se afla in robot-programs.

Nu este necesar sa aveti Python instalat pentru a modifica sursele.
In folderul sim-files/dist este inclus Python 2.5 impreuna cu bibliotecile necesare.

Daca aveti deja Python instalat (impreuna cu bibliotecile):

python sim-files\main.py   # porneste programul cu Python-ul instalat pe calculator
robot-sandbox.cmd          # porneste cu Python 2.5 inclus in "dist" 


LINUX:

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



