# Rendering

An Edl (`otto.models.Edl`) is a list of clips -- templates, videos, images and
sounds -- each placed on the output by its own timing. `otto.render` turns one
into media:

- `generateEdl(edl, moviesize)` builds it into a moviepy clip, picture and
  sound, and writes nothing;
- `renderMultitrack(edl, filename=..., fps=..., preset=...)` encodes that as
  a video file;
- `renderFrame(edl, t, filename, moviesize)` writes one moment of it, as a
  JPEG;
- `renderSound(edl, filename, rate)` writes only its sound, as a WAV.

`generateEdl`'s docstring is the full account of how a clip's fields combine.
The [reference](reference/render.md) has it, and every other function.
[Media files](media.md) says how otto describes a file, and how it makes demo
clips from nothing.

## A clip is checked before its media is opened

Whatever otto can tell is wrong with a clip from the Edl alone is refused as
the clip is built, before its media is fetched or opened, rather than part way
through a render or on whichever preview frame happens to show it: a type
that is missing or unknown, timing that describes no clip, a negative fade, an
opacity outside 0 to 1, a `resize` that is not positive, and a position
moviepy cannot place a clip at.

A position is one of `center`, `left`, `right`, `top` or `bottom`, or an
`(x, y)` pair whose x is a finite number or `left`, `center` or `right`, and
whose y is a finite number or `top`, `center` or `bottom`. A template clip's
`data.position` is checked the same way, since the template hands it to
moviepy too. A function of time is left for moviepy to call, and a boolean is
not a number here. An empty position, `''` or `()`, is no position: a video or
an image is then centred, and a template places itself.

moviepy reads a position only when it draws a frame. Unchecked, `'middle'` or
`('top', 'left')` would build without complaint and then raise there, as a
KeyError naming neither the clip nor the field.

## A clip is named by its place, counted from 1

What otto cannot render raises `EdlException`. When one clip is the cause, the
message starts with the clip's place in the Edl, counted from 1, and its name:
`clip 2 ('title'): ...` is the second clip. alfred counts the clips of a
timeline it refuses from 1 as well, so a message from either names the same
clip the same way.

## A clip's fades reach its sound

A clip's `fadeIn` and `fadeOut` are seconds of fade, and the only fades it
gets: templates add none of their own. They fade its picture, as a crossfade
of its mask, and its sound -- an audio clip's, and a video clip's own -- in
over the first `fadeIn` seconds and out over the last `fadeOut` seconds of the
sound it plays. That is where the clip ends, or where its source's sound runs
out when that is sooner. 0 or null is no fade.

The model's default is a second of each, so a video clip that sets no fades of
its own fades its sound in and out over a second, along with its picture.

## An encoding, by name

`renderMultitrack` encodes with libx264 and AAC. `preset` names how, one of
`PRESETS`, so a caller says how good a render should be and otto says how to
get it:

| preset | libx264 `-preset` | rate factor (`-crf`) | sound |
|---|---|---|---|
| `draft` | `ultrafast` | 30 | 128k |
| `standard` | `medium` | 23 | 192k |
| `high` | `slow` | 18 | 320k |

```python
from otto.render import renderMultitrack

renderMultitrack(edl, filename='out.mp4', moviesize=(1280, 720), preset='draft')
```

A constant-rate factor holds quality steady across easy and difficult
footage, which a fixed bitrate does not; lower is better, and larger. A slower
`-preset` is smaller at the same quality.

- **A preset decides, alone.** With one, `bitrate`, `audio_bitrate` and
  `ffmpeg_params` cannot be given too, nor a `codec` other than libx264, whose
  settings a preset is. Either is an `EdlException`, raised before anything is
  built, as is a name that is not a preset.
- **Without one, the encoding is as given.** libx264 at moviepy's own
  `medium` and its default rate factor, with any `ffmpeg_params` added to
  moviepy's options, and the sound at `audio_bitrate`, or 320k.

## One frame, as a JPEG

`renderFrame` draws what an Edl looks like `t` seconds into the output and
writes it as a JPEG, whatever the file is called, at `moviesize`. It returns
the file's name. A preview is made of these.

```python
from otto.exceptions import EdlException
from otto.render import renderFrame

try:
    renderFrame(edl, 2.5, 'frame.jpg', moviesize=(640, 360))
except EdlException as refused:
    ...  # names the clip that cannot be rendered
```

- **It is the frame a render encodes at `t`.** The whole Edl is built, as
  `generateEdl` builds it, so a clip that cannot be rendered is refused with
  the `EdlException` naming it, wherever it is on the timeline and not only
  when the frame shows it -- and nothing is written. A moment that no clip
  covers, before the first or after the last, is black.
- **Pillow's JPEG, at quality 75** (`FRAME_QUALITY`), with no transparency:
  the same image moviepy's `save_frame` writes for a `.jpg`.

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
- **A file it cannot write is an error, not a length.** moviepy never asks how
  ffmpeg exited, so the length is read back from the file: a WAV that was not
  written is an `OSError` naming it, where it would otherwise have gone
  unnoticed.

## Each video is probed once per version of its file

Before it opens a video, otto asks ffmpeg for its stored size and how far it
is turned -- a `rotate` tag, or on ffmpeg 5 and later a display matrix -- so
that it can be decoded already fitted to its box, at the proportions it is
shown at: ffmpeg turns it upright as it decodes. A preview builds the whole
Edl again for every frame it shows, so the answer is kept: per file, keyed by
its absolute path, its modification time and its size, for the last
`PROBE_CACHE_SIZE` (256) probes in the process. A file that changes is asked
about again, and a probe that fails is not kept.
