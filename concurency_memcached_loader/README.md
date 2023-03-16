# Concurrency memcache load
Fast version of memc_load.py

Multiprocessing with multithreading

The main process creates several worker processes (prioritized by the number of files for parsing). 
For each memcached address, threads are created in each process to write data to the memcache. 

Multithreading works on the producer-consumer principle using the Queue

# requirements
  - Python v3
  - Memcache

# How to run

1. Add data to /data from
    - https://cloud.mail.ru/public/2hZL/Ko9s8R9TA
    - https://cloud.mail.ru/public/DzSX/oj8RxGX1A
    - https://cloud.mail.ru/public/LoDo/SfsPEzoGc

2. Install memcache
```
sudo apt install memcached
memcached -l 0.0.0.0:33013,0.0.0.0:33014,0.0.0.0:33015,0.0.0.0:33016
```

3. Python3 memc_load_concurrency.py -h
```
Usage: memc_load_concurrency.py [options]

Options:
  -h, --help            show this help message and exit
  -t, --test            
  -l LOG, --log=LOG     
  -w WORKERS, --workers=WORKERS
  --dry                 
  --pattern=PATTERN     
  --idfa=IDFA           
  --gaid=GAID           
  --adid=ADID           
  --dvid=DVID  
```

# Working time tracking

non-cocurrency version with option dry:

```
real	2m58.935s
user	2m58.293s
sys	  0m0.581s
```

cocurrency version with option dry:
```
real	1m47.157s
user	5m16.966s
sys	  0m1.554s
```
