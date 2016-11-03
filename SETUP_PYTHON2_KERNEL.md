Nbparametrise should be invoked with python3, but can still handle python2 notebooks, if
it can find the python2 kernel properly. In my computer there was no information on kernels 
in mkdir /home/carolinux/.local/share/jupyter/kernels/ (it was an empty directory). But it could
still find python3 kernel since it was called from python3.

So the steps to set it up are (replace /home/carolinux with your home):
```
mkdir /home/carolinux/.local/share/jupyter/kernels/python2
cp kernel.json /home/carolinux/.local/share/jupyter/kernels/python2/
```

Kernel.json should have the executable of python that you want (can also be an anaconda path)

