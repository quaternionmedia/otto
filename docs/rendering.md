# Rendering

An Edl (`otto.models.Edl`) is a list of clips (templates, videos, images and
sounds), each placed on the output by its own timing. `otto.render` turns one
into media:

| function | does |
|---|---|
| `generateEdl(edl, moviesize)` | builds a moviepy clip, picture and sound; writes nothing |
| `renderMultitrack(edl, filename=..., fps=..., preset=...)` | encodes a video file |
| `renderFrame(edl, t, filename, moviesize)` | writes one moment as a JPEG |
| `renderSound(edl, filename, rate)` | writes only the sound, as a WAV |

The [reference](reference/render.md) has every function; `generateEdl`'s
docstring is the full account of how a clip's fields combine.
[Media files](media.md) covers describing a file and making demo clips.

## A clip is checked before its media is opened

otto refuses what it can tell is wrong from the Edl alone as it builds the
clip, before fetching or opening its media, not part way through a render or
on whichever preview frame shows the clip:

- a type that is missing or unknown;
- timing that describes no clip;
- a negative fade;
- an opacity outside 0 to 1;
- a `resize` that is not positive;
- a position moviepy cannot place a clip at.

A position is one of `center`, `left`, `right`, `top` or `bottom`, or an
`(x, y)` pair where:

- x is a finite number, `left`, `center` or `right`;
- y is a finite number, `top`, `center` or `bottom`.

A template clip's `data.position` is checked too, since the template hands it
to moviepy. A function of time is left for moviepy to call. A
boolean is not a number here. An empty position (`''` or `()`) is no
position: a video or an image is centred, and a template places itself.

Unchecked, moviepy would accept `'middle'` or `('top', 'left')` and raise
only when it draws a frame, as a KeyError naming neither the clip nor the
field.

## A clip is named by its place, counted from 1

What otto cannot render raises `EdlException`. When one clip is the cause,
the message starts with its place in the Edl, counted from 1 as alfred
counts, and its name: `clip 2 ('title'): ...` is the second clip.

## A clip's fades reach its sound

`fadeIn` and `fadeOut` are seconds of fade, and the only fades a clip gets:
templates add none. They fade the picture (as a crossfade of its mask) and
the sound (an audio clip's, or a video clip's own), over the first `fadeIn`
and the last `fadeOut` seconds of the sound the clip plays. That sound ends
with the clip, or sooner if its source's sound runs out. 0 or null is no
fade.

The model's default is a second of each, so a video clip that sets no fades
fades its sound along with its picture.

## An encoding, by name

`renderMultitrack` encodes with libx264 and AAC. `preset`, one of `PRESETS`,
says how good a render should be, and otto picks the settings:

| preset | libx264 `-preset` | rate factor (`-crf`) | sound |
|---|---|---|---|
| `draft` | `ultrafast` | 30 | 128k |
| `standard` | `medium` | 23 | 192k |
| `high` | `slow` | 18 | 320k |

```python
from otto.render import renderMultitrack

renderMultitrack(edl, filename='out.mp4', moviesize=(1280, 720), preset='draft')
```

A rate factor holds quality steady across easy and difficult footage, which a
fixed bitrate does not; lower is better, and larger. A slower `-preset` is
smaller at the same quality.

- **A preset decides alone.** With one, `bitrate`, `audio_bitrate` and
  `ffmpeg_params` cannot be given, nor a `codec` other than libx264, since a
  preset is libx264's settings. Either is an `EdlException`, raised before
  anything is built, as is a name that is not a preset.
- **Without one, the encoding is as given:** libx264 at moviepy's `medium`
  and its default rate factor, any `ffmpeg_params` added to moviepy's
  options, and the sound at `audio_bitrate`, or 320k.

## One frame, as a JPEG

`renderFrame` draws an Edl `t` seconds into the output, at `moviesize`,
writes it as a JPEG whatever the file is called, and returns the file's name.
Previews are made of these.

```python
from otto.exceptions import EdlException
from otto.render import renderFrame

try:
    renderFrame(edl, 2.5, 'frame.jpg', moviesize=(640, 360))
except EdlException as refused:
    ...  # names the clip that cannot be rendered
```

- **It is the frame a render encodes at `t`.** The whole Edl is built, as
  `generateEdl` builds it, so a clip that cannot be rendered is refused (the
  `EdlException` names it) wherever it sits on the timeline, and nothing is
  written. A moment no clip covers, before the first or after the last, is
  black.
- **Pillow's JPEG, at quality 75** (`FRAME_QUALITY`), with no transparency:
  the image moviepy's `save_frame` writes for a `.jpg`.

## A timeline's sound, alone

`renderSound` writes what an Edl sounds like to a mono, 16-bit PCM WAV at the
rate asked for, and returns the file's length in seconds. It is for hearing a
timeline rather than watching it: alfred has a speech engine transcribe it
into captions, at 16 kHz.

```python
from otto.exceptions import NoSoundException
from otto.models import Edl
from otto.render import renderSound

edl = Edl.model_validate({
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

- **It is the render's sound:** every clip timed, faded and mixed as
  `generateEdl` does it, which is what `renderMultitrack` would encode for
  the same Edl, less a soundtrack passed as `audio`. It runs from
  0 to the end of the output (`Edl.duration`, or where the last clip ends,
  templates and images included), silent where nothing sounds, so a moment
  in the WAV is the same moment in the video.
- **One channel, at the rate asked for.** The sound is mixed at `AUDIO_FPS`
  (48 kHz, the WAV's rate without a `rate`), and ffmpeg folds it into one
  channel and resamples it to `rate` as it writes. Resampling filters out
  what is too high for `rate` to carry; sampling the mix at `rate` would fold
  it back down among what is heard. The file is a WAV whatever it is called.
- **Only what can sound is built:** video and audio clips (`SOUND_TYPES`). A
  template or an image is never heard, and drawing one can cost an
  ImageMagick run, so only its type and timing are read, for the length.
  Errors still name a clip by its place in the whole Edl.
- **Nothing to hear is an answer.** When the Edl has no video or audio clip,
  or no audio clip and no video clip with sound where it plays, `renderSound`
  raises `NoSoundException`, an `EdlException`, and writes nothing. A `rate`
  that is not a positive whole number is an `EdlException` too.
- **A file it cannot write is an error, not a length.** moviepy never checks
  how ffmpeg exited, so the length is read back from the file. A WAV that was
  not written is an `OSError` naming it.

## Each video is probed once per version of its file

Before opening a video, otto asks ffmpeg for its stored size and rotation (a
`rotate` tag, or on ffmpeg 5 and later a display matrix), so that ffmpeg
decodes it upright, at its displayed proportions, already fitted to its box.
A preview builds the whole Edl again for every frame, so the answers are kept
per file, keyed by absolute path, modification time and size, for the last
`PROBE_CACHE_SIZE` (256) probes in the process. A file that changes is probed
again; a probe that fails is not kept.
