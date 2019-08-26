
# kernprof

```
Total time: 28.8102 s
Function: PIL_rotate at line 29

Line #      Hits         Time  Per Hit   % Time  Line Contents
==============================================================
    29                                           @profile
    30                                           def PIL_rotate():
    31         1        364.0    364.0      0.0      rotations = [i for i in range(361) if i != 0]
    32         2       1946.0    973.0      0.0      for root, __, files in os.walk("images", topdown=False):
    33       101        789.0      7.8      0.0          for file in files:
    34       100      13807.0    138.1      0.0              source_path = os.path.join(root, file)
    35       100     218056.0   2180.6      0.2              img = Image.open(source_path)
    36       100       5280.0     52.8      0.0              c = choice(rotations)
    37       100   62392540.0 623925.4     63.4              img = img.rotate(c, resample=Image.BICUBIC, expand=True)
    38       100   35480957.0 354809.6     36.0              img.save(source_path)
    39       100     357759.0   3577.6      0.4              img.close()



Total time: 140.056 s
Function: SCI_rotate at line 42

Line #      Hits         Time  Per Hit   % Time  Line Contents
==============================================================
    42                                           @profile
    43                                           def SCI_rotate():
    44         1        385.0    385.0      0.0      rotations = [i for i in range(361) if i != 0]
    45         2       2089.0   1044.5      0.0      for root, __, files in os.walk("images", topdown=False):
    46       101       1952.0     19.3      0.0          for file in files:
    47       100      14384.0    143.8      0.0              source_path = os.path.join(root, file)
    48       100   13333862.0 133338.6      2.8              img = io.imread(source_path)
    49       100       7684.0     76.8      0.0              c = choice(rotations)
    50       100  338185279.0 3381852.8     70.6              img = rotate(img, c, order=3)
    51       100  127155766.0 1271557.7     26.6              io.imsave(source_path, img)



Total time: 2.18328 s
Function: current_method at line 54

Line #      Hits         Time  Per Hit   % Time  Line Contents
==============================================================
    54                                           @profile
    55                                           def current_method():
    56         1         15.0     15.0      0.0      images = []
    57         2       2222.0   1111.0      0.0      for root, __, files in os.walk("images", topdown=False):
    58       101        374.0      3.7      0.0          for file in files:
    59       100       8965.0     89.7      0.1              source_path = os.path.join(root, file)
    60       100        458.0      4.6      0.0              images.append(source_path)
    61         1    7450250.0 7450250.0     99.8      a = [Image.open(img) for img in images]
    62         1         32.0     32.0      0.0      images = []
```

# memory_profiler

```
Line #    Mem usage    Increment   Line Contents
================================================
    15     18.5 MiB     18.5 MiB   @profile
    16                             def image_set():
    17     18.5 MiB      0.0 MiB       images = set()
    18     26.2 MiB      0.0 MiB       for i in range(100000):
    19     26.2 MiB      2.0 MiB           images.add(i)
    20     27.2 MiB      0.5 MiB       [image for image in images]



Line #    Mem usage    Increment   Line Contents
================================================
     7     18.8 MiB     18.8 MiB   @profile
     8                             def image_list():
     9     18.8 MiB      0.0 MiB       images = []
    10     23.3 MiB      0.0 MiB       for i in range(100000):
    11     23.3 MiB      0.7 MiB           images.append(i)
    12     24.1 MiB      0.7 MiB       [image for image in images]
```

## Notes
	* it seems that rotating the image is one of the things that take up most time
		- However Pillow(PIL) still seems the most reliable module
