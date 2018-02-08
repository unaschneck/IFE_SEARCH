# IFE_SEARCH

Looking for Interplanetary Field Enhancements (IFEs) (Russell et al. 1985a) in STEREO, WIND, and ACE magnetometer data.


__Selection Criteria (Lai et al. 2017):__
1. Total Magnetic field enhancement > 25% (relative to ambient |B|)
2. Duration > 10 minutes
3. Current sheet is present at or within the peak of |B|
4. One of the three magnetic field component doesn't rotate during the enhancement

# To Run Code
1. Download or clone repo

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
![example_output](https://github.com/unaschneck/IFE_SEARCH/blob/master/output_img/JUNE_2009_STEREO_A.png)

Without events:
```
trimmed mean = -0.56126
25% cutoff = -0.420945
time cutoff = 10 minutes
size of datetime: 6
```
![example_output](https://github.com/unaschneck/IFE_SEARCH/blob/master/output_img/JUNE_TEST.png)
