# mondeja's pre-comit hooks

## Hooks

### **`wavelint`**

Check if your WAVE files have the correct number of channels, frame rate,
durations...

#### Parameters

- **`-nchannels=N`** (*int*): Number of channels that your sounds must have.
- **`-sample-width=N`** (*int*): Number of bytes that your sounds must have.
- **`-frame-rate=N`** (*int*): Sampling frequency that your sounds must have.
- **`-nframes=N`** (*int*): Exact number of frames that your sounds must have.
- **`-comptype=TYPE`** (*str*): Compression type that your sounds must have.
- **`-compname=NAME`** (*int*): Compression that your sounds must have.
- **`-min-duration=TIME`** (*float*): Minimum duration in seconds that your
 sounds must have.
- **`-max-duration=TIME`** (*float*): Maximum duration in seconds that your
 sounds must have.
