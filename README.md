# IFE_SEARCH

Looking for Interplanetary Field Enhancements (IFEs) (Russell et al. 1985a) in ACE magnetometer data (GSE coordinates). IFEs were first identified in associated with the passage of an asteroid with the Venusian orbit and are believed to be the result of charged dust interactions with the flowing solar wind. The evolution and geoeffectiveness of IFEs is still an area of active research, so fast and objective identification of IFEs at 1 AU is important.


__Selection Criteria (Lai et al. 2017):__
1. Total Magnetic field enhancement > 25% (relative to ambient |B|)
2. Duration of enhancement > 10 minutes
3. Current sheet is present at or within the peak of |B|

# To Run Code
1. Download or clone repo
2. Input data must be in GSE Coordinates

Required packages: 

2. Running code:
```python ife_processing.py -F <filename>.txt```

# Current Output

With event:
```
trimmed mean = -0.814758658791
25% cutoff = -0.611068994093
time cutoff = 10 minutes
size of datetime: 14371 seconds, 239.52 minutes
total events = 3
average event length 22.2056 minutes
```
Without events:
```
trimmed mean = -0.56126
25% cutoff = -0.420945
time cutoff = 10 minutes
size of datetime: 6
```

Example of Identified Event:
![event_example](https://github.com/unaschneck/IFE_SEARCH/blob/master/example_event.png)

# To Do

1. Adapt code to take in STEREO in GSE coordinates
