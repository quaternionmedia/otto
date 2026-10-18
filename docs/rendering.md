# Rendering

An Edl (`otto.models.Edl`) is a list of clips -- templates, videos, images and
sounds -- each placed on the output by its own timing. `otto.render` turns one
into media:

- `generateEdl(edl, moviesize)` builds it into a moviepy clip, picture and
  sound, and writes nothing;
- `renderMultitrack(edl, filename=..., fps=...)` encodes that as a video file;
- `renderSound(edl, filename, rate)` writes only its sound, as a WAV.

`generateEdl`'s docstring is the full account of how a clip's fields combine.
The [reference](reference/render.md) has it, and every other function.

## A timeline's sound, alone

`renderSound` writes what an Edl sounds like to a mono, 16-bit PCM WAV at the
rate asked for, and returns the file's length in seconds. It is for whatever
needs to hear a timeline rather than watch it: alfred has a speech engine
transcribe it into captions, at 16 kHz.

```python
from otto.exceptions import NoSoundException
from otto.models import Edl
from otto.render import renderSound

edl = Edl.parse_obj({
    'clips': [
        {'type': 'template', 'name': 'makeColor', 'duration': 7,
         'data': {'color': '#203040'}},
        {'type': 'audio', 'name': 'speech.wav', 'start': 1, 'duration': 4},
        {'type': 'video', 'name': 'talking.mp4', 'start': 5, 'duration': 2},
    ]
})
try:
    seconds = renderSound(edl, 'timeline.wav', rate=16000)  # 7.0
except NoSoundException:
    ...  # nothing in the Edl makes a sound
```

- **It is the render's sound.** Every clip is timed, faded and mixed as
  `generateEdl` does it, so the WAV holds the sound `renderMultitrack` would
  encode for the same Edl, less a soundtrack passed as `audio`. It runs from 0
  to the end of the output -- `Edl.duration`, or where the last clip ends, a
  template or an image included -- with silence where nothing sounds, so a
  moment in the WAV is the same moment in the video.
- **One channel, at the rate asked for.** The sound is mixed at `AUDIO_FPS`
  (48 kHz), and ffmpeg folds it into one channel and resamples it to `rate` as
  it writes. Resampling filters out what is too high for `rate` to carry,
  where sampling the mix at `rate` would fold it back down among what is heard.
  Without a `rate` the WAV is at 48 kHz. The file is a WAV whatever it is
  called.
- **Only what can sound is built.** Video and audio clips (`SOUND_TYPES`) are
  opened. A template or an image is never heard, and drawing one can cost an
  ImageMagick run, so it is not built: only its type and its timing are read,
  for the length. An error still names a clip by its place in the whole Edl.
- **Nothing to hear is an answer.** When the Edl has no video or audio clip,
  or no audio clip and no video clip with sound where it plays, `renderSound`
  raises `NoSoundException`, an `EdlException`, and writes nothing. A `rate`
  that is not a positive whole number is an `EdlException` too.
