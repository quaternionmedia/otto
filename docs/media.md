# Media files

Besides rendering, otto says what a media file holds, and makes demo clips
for an install with none. Both run the ffmpeg otto encodes with (moviepy's
`FFMPEG_BINARY`, imageio-ffmpeg's unless set), so a consumer needs no ffmpeg
of its own.

## What a file holds

`otto.media.probe(path, type=None)` returns a `MediaInfo`: duration, picture
width and height, frame rate, and whether the file has sound. Anything
unknown is None.

```python
from otto.media import UNKNOWN, probe

found = probe('videos/talk.mp4', 'video')
found.duration  # 62.5
found.size      # (1080, 1920): as shown, a quarter turn applied
found.fps       # 59.94
found.sound     # True
```

- **Headers only.** ffmpeg describes the input and exits, decoding nothing;
  `otto.media.parse` reads the description. The file is named to ffmpeg as
  `file:<path>`, so a name is only ever a file, never another protocol.
- **Size as shown.** A `rotate` tag or a display matrix of a quarter turn
  swaps width and height.
- **`type` is the clip the file is for:** `video`, `image` or `audio`; None
  reads everything ffmpeg describes. An image is a still, with no duration,
  frame rate or sound whatever ffmpeg says (it gives a still a nominal 25
  fps, and an animated GIF its own). Audio has no picture, so an MP3's cover
  art is not one.
- **A file ffmpeg cannot describe is `UNKNOWN`:** not media, or not there.
- **Slow is not unknown.** ffmpeg gets `timeout` seconds (`PROBE_TIMEOUT`,
  10); longer is a `TimeoutError` naming the file, so a caller that keeps
  answers can retry rather than remember the file as unknown. An ffmpeg that
  cannot be started is an `OSError`.

Each call starts ffmpeg once and keeps nothing. A caller that asks often
keeps the answers itself, keyed by what says a file has changed (alfred's
media library: path, modification time and size). Rendering keeps its own
probes of the videos it opens; see
[Rendering](rendering.md#each-video-is-probed-once-per-version-of-its-file).

## Demo clips

`otto.demo.demoClip(filename, source='bars')` synthesises a short clip from
one of ffmpeg's test sources, with no file, download or network, and returns
its name.

```python
from otto.demo import demoClip

demoClip('videos/demo-bars.mp4', 'bars')
demoClip('videos/demo-colour.mp4', 'color', duration=5)
demoClip('videos/bars-and-tone.mp4', 'bars', tone=1000)
```

| source | picture |
|---|---|
| `bars` | SMPTE colour bars |
| `testcard` | ffmpeg's test card: a moving pattern with a counter |
| `color` | a plain dark blue-grey, `#101820` |

- **Small and short.** 320x180, 24 frames a second, 3 seconds, unless asked
  otherwise (`size`, `fps`, `duration`). It encodes in about a second and
  costs a few kilobytes.
- **An MP4 a browser plays**, in yuv420p, whatever the file is called.
- **Silent, unless `tone` is set:** a sine in Hz, at -18 dBFS, for the whole
  clip. Bars at 1000 is bars and tone.
- **Whole or not at all.** ffmpeg writes beside the file under a hidden
  temporary name (`.<name>.<random>.part`), moved into place when it
  finishes. A listing never offers half a clip; a failed run leaves nothing
  new and keeps any clip already there.
- **Errors.** A source, length, size, rate or tone it cannot make is a
  `ValueError` before ffmpeg runs. ffmpeg failing is an `FFmpegException`
  (`otto.exceptions`), whose `stderr` is everything ffmpeg said. An ffmpeg
  that cannot be started is an `OSError`.
