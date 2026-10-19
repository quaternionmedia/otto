# Media files

Besides rendering an Edl, otto answers two questions about media for the
programs that use it: what a file holds, and -- for an install that has none
-- something to edit. Both run the ffmpeg otto encodes with (moviepy's
`FFMPEG_BINARY`, imageio-ffmpeg's unless set), so a consumer needs no ffmpeg
of its own.

## What a file holds

`otto.media.probe(path, type=None)` answers a `MediaInfo`: how long the file
runs, its picture's width and height, its frame rate, and whether it has a
sound. Anything unknown is None.

```python
from otto.media import UNKNOWN, probe

found = probe('videos/talk.mp4', 'video')
found.duration  # 62.5
found.size      # (1080, 1920): as shown, a quarter turn applied
found.fps       # 59.94
found.sound     # True
```

- **It reads the headers, and decodes nothing.** ffmpeg describes the input
  and exits; `otto.media.parse` reads the description. The file is named to
  ffmpeg as `file:<path>`, so a name is only ever a file, never another
  protocol.
- **As shown.** The width and height are the picture's as it is displayed: a
  `rotate` tag or a display matrix of a quarter turn swaps them.
- **`type` is the clip the file is for**, one of `video`, `image` or `audio`.
  An image is a still, so it has no duration, frame rate or sound, whatever
  ffmpeg says -- it gives a still a nominal 25 fps, and an animated GIF its
  own -- and audio has no picture, so an MP3's cover art is not one. None
  reads everything ffmpeg describes.
- **A file ffmpeg cannot describe is `UNKNOWN`**: one that is not media, or
  is not there.
- **Slow is not unknown.** ffmpeg gets `timeout` seconds (`PROBE_TIMEOUT`,
  10); longer is a `TimeoutError` naming the file, so a caller that keeps
  answers can try a slow file again rather than remember it as unknown. An
  ffmpeg that cannot be started is an `OSError`.

Each call starts ffmpeg once, and nothing is kept. A caller that asks about
the same files often keeps the answers itself, keyed by what says a file has
changed: alfred keys its media library's by path, modification time and size.
(Rendering keeps its own probes of the videos it opens; see
[Rendering](rendering.md).)

## Demo clips

`otto.demo.demoClip(filename, source='bars')` synthesises a short clip from
one of ffmpeg's own test sources -- no file, download or network -- and
returns its name.

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

- **Small and short.** 320x180 at 24 frames a second for 3 seconds unless
  asked otherwise (`size`, `fps`, `duration`): it encodes in about a second
  and costs a few kilobytes.
- **An MP4 a browser plays**, in yuv420p, whatever the file is called.
- **Silent, or bars and tone.** `tone` is a sine in Hz, at -18 dBFS, for the
  clip's whole length.
- **Whole or not at all.** ffmpeg writes beside the file under a hidden
  temporary name (`.<name>.<random>.part`), moved into place when it has
  finished: a listing taken meanwhile cannot offer half a clip, and a failed
  run leaves nothing new and keeps a clip that was already there.
- **Errors.** A source, length, size, rate or tone it cannot make is a
  `ValueError` before ffmpeg runs. ffmpeg failing is an `FFmpegException`
  (`otto.exceptions`), whose `stderr` is everything ffmpeg said; an ffmpeg
  that cannot be started is an `OSError`.
