robot-sandbox

Simulator pentru brate robotice articulate


INSTALARE:

Versiunea binara (Windows): unzip and run :)



Surse (Windows):

Se instaleaza mediul de dezvoltare si bibliotecile de mai jos:
- Python 2.5
- ipython
- cgkit
- pyode (din SVN; trebuie compilat impreuna cu ODE)
  * se poate folosi versiunea precompilata: libs/pyode-cvs-bin.zip
- numpy
- pygame
- PyProtocols (from source, pyhon setup.py --without-speedups install)
- pyreadline

Pornirea programului:
python main.py

Compilare PyODE (optional, dar greu!):
- ODE (surse)
- pyrex
- instructiuni pentru compilarea ODE la http://demura.net/tutorials/ode2 
  * merge cu Google Translate
  Eu am compilat cu 
- apoi, pentru compilarea PyODE:
     - varianta binara a lui ODE trebuie sa fie in ode-x.xx.x\lib\releaselib\ode.dll
       (daca nu e acolo, se muta manual)
     - se modifica in setup.py calea spre folderul cu ODE: c:\path\to\ode-x.xx.x
     - se comenteaza setup.py comenzile specifice MSVC (CC_ARGS si LINK_ARGS)
     - se modifica in setup.py comanda pyrex in pyrex.py
     - in folderul cu PyODE:
	* setup.py build
	* python setup.py install


Linux:
sudo apt-get ... [TODO]

