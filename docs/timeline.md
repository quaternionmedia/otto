# The timeline

An Edl (`otto.models.Edl`) is a timeline: a list of clips, each placed on the
output by its own timing. [Rendering](rendering.md) is what otto makes of one,
and the [reference](reference/models.md) has the models.

```json
{"duration": 6, "clips": [
  {"type": "video", "name": "videos/talk.mp4", "inpoint": 12, "outpoint": 18},
  {"type": "template", "name": "textBox", "start": 1, "duration": 3,
   "data": {"text": "Chapter one", "position": ["center", "bottom"]}},
  {"type": "audio", "name": "music.mp3", "duration": 6, "fadeOut": 2}
]}
```

## The Edl

### `clips`

`list[Clip]`, required. The clips, in stacking order: each sits where its
own timing puts it, and where clips overlap a later one is drawn over an
earlier one, so the first is at the bottom. What a clip leaves transparent (a
template around its text, a fade, an `opacity` below 1) shows what is under
it. Audio clips are mixed, never drawn. otto renders no Edl without clips.

### Edl `duration`

`float | None = None`. The output's length in seconds, positive: it cuts off
clips that run past it, and runs on past the last. Without one, the output
ends with its last clip. A moment no clip covers is black and silent.

## A clip

Every field has a default, but every clip needs a `type` and a `name`. Keys
the model lacks are dropped without an error; a number sent for text is text.
otto checks the rest [before opening a clip's media](rendering.md#a-clip-is-checked-before-its-media-is-opened).

### `type`

`str | None = None`. `template`, `video`, `image` or `audio`
(`otto.render.CLIP_TYPES`). Any other, or none, is refused.

### `name`

`str | None = None`. For a template clip, the [template](#template-data) to
draw. For media, a file's path, or an `http` or `https` URL that otto fetches
first (`otto.getdata.download`): a JPEG, PNG, MP4 or MP3 of a known size.

### `duration`

`float = 5`. How long the clip plays, in seconds, when it has no `outpoint`;
then it must be positive. With an `outpoint` it is not read. Null is refused.

### `start`

`float | None = None`. Where it begins in the output, in seconds; absent is 0.

### `inpoint`

`float | None = None`. Where playback begins in the clip's source, in seconds.
Absent is 0. An image's inpoint changes nothing: it is one picture throughout.

### `outpoint`

`float | None = None`. Where playback ends in the source, in seconds, after
the `inpoint`. With one, the clip plays for `outpoint - inpoint` seconds.

### `offset`

`float | None = None`. Deprecated: use `start` or `inpoint`. A positive
offset is added to `start`; a negative one skips that far into the source:
`-2` adds 2 to `inpoint`.

### `fadeIn`

`float | None = 1`. Seconds of [fade](rendering.md#a-clips-fades-reach-its-sound)
at the clip's start, of its picture and its sound; 0 or null is none, negative
is refused. A template adds none at its edges.

### `fadeOut`

`float | None = 1`. Seconds of fade at the clip's end, as `fadeIn`. A sound
that ends before its clip does fades out where it ends.

### `opacity`

`float | None = None`. From 0, invisible, to 1, as drawn: it scales the
clip's own transparency. Outside 0 to 1 is refused.

### `position`

`tuple | str | None = None`. Where the clip sits in the frame: `center`;
`left`, `right`, `top` or `bottom`, against that side and centred along it;
or an (x, y) pair, x a number, `left`, `center` or `right`, and y a number,
`top`, `center` or `bottom`. A number places the clip's top left corner, as
[`relative`](#relative) says. With none, or an empty one, a video or an image
is centred and a template stays where it draws itself.

### `relative`

`bool | None = True`. Whether `position`'s numbers are fractions of the
frame, so `(0.5, 0)` puts the clip's top left corner halfway along the top,
or pixels from the frame's top left corner (false or null).

### `resize`

`float | tuple | None = None`. Scales the clip once it is fitted or drawn:
by a positive factor, or to exactly (width, height) pixels.

### `clipsize`

`tuple | None = None`. For a template, the (width, height) it is drawn at;
for a video or an image, the box it is fitted into, up or down, keeping its
proportions. The frame (`moviesize`) by default.

### `data`

`TemplateData | None = None`. What a template clip draws, and must have; see
[template data](#template-data). Other clips ignore it.

## Timing

- **`outpoint` wins over `duration`.** A clip plays for `outpoint - inpoint`
  seconds when it has an outpoint, and for `duration` seconds when it has
  none: `{"duration": 5, "inpoint": 0, "outpoint": 3}` plays for 3.
- **Timing that describes no clip is refused:** a negative start or inpoint,
  an outpoint not after the inpoint, a duration that is not positive when
  there is no outpoint, an inpoint past the end of a video or a sound.
- **A video shorter than its clip** holds its last frame; a sound is followed
  by silence. A template is drawn long enough to reach its outpoint.
- `otto.render.clipTiming(clip)` reads a clip's timing by these rules, as a
  `Timing` of `start`, `inpoint`, `length` and `outpoint`.

## Template data

A template clip's `name` is a key of `otto.templates.TEMPLATES`, the only
templates an Edl can draw:

| template | draws |
|---|---|
| `title` | `text`, uncovered by a box in `themecolor` that shrinks to a bar at its left |
| `textBox` | `text`, over a box in `bg` when one is given |
| `makeColor` | its `clipsize` filled with `color`, `#0000bb` unless given |
| `initial` (deprecated) | the sentences of `text`, one after another |
| `bullets` (deprecated) | the points of `text`, split at `•`, in turn, each over a box in `themecolor` |
| `final` (deprecated) | `text`, over otto's default address and website, which `data` cannot change, in an outline in `themecolor` |

Its `data`, a `TemplateData`, says what to draw. A field that is not null is
passed to the template, which ignores what it does not use; one left out
keeps the template's own default. Colours are written `#rrggbb`.

| field | type | default | what it is |
|---|---|---|---|
| `text` | `str` | none | the words; every template but `makeColor` needs them |
| `textsize` | `tuple` | half the `clipsize` each way | the (width, height) the text is set in |
| `color` | `str` | `#FFFFFF` | the text's colour, and `makeColor`'s fill |
| `themecolor` | `str` | `#FFFF00` | `title`'s box, `bullets`' boxes, `final`'s outline |
| `bg` | `str` | none | a box behind the text at 40% opacity: `title`, `textBox`, `initial` |
| `fontsize` | `float` | fitted to `textsize`; `final`, from `clipsize`'s height | the text's size |
| `font` | `str` | `Open-Sans`; `final`, `Segoe-UI-Bold` | a font name as ImageMagick lists it |
| `method` | `str` | `label` | `label` keeps the text's lines; `caption` wraps it to `textsize`'s width. The model's `label` reaches every template, `title` included |
| `align` | `str` | `center` | how `textBox`'s lines line up: an ImageMagick gravity, such as `west` or `east` |
| `position` | `tuple` or `str` | the template's own | where the text sits in the template's frame, as a [`position`](#position) is given, in pixels: `relative` does not reach it |
| `fxs` | `list[FX]` | none | movement; see [`fxs`](#fxs) |

A template is drawn at its `clipsize`, the frame unless the clip gives one.
The clip's `position` places the whole of it, replacing the template's own
placement and movement. `title` and `initial` place their whole frame by
`data.position`, as well as their text.

### `fxs`

`list[FX] | None = None`, each `FX` a `name` and a `data` dict. Moves a
`textBox`, `initial` or `bullets` template over its first second
(`FX_SECONDS`): it is offset by the sum of the points its curves have reached,
in fractions of the frame, and then rests at (0, 0). The one curve is
`bezier2` (`FX_CURVES`), from (`c1x`, `c1y`), pulled towards (`ax`, `ay`), to
(`c2x`, `c2y`); it moves along x alone unless its `data` has `axes: 'y'` or
`'xy'`. An unknown name, or a missing point, is refused. A clip has no `fxs`
of its own; one on a clip is dropped.
