"""Templates

Prebuilt Template blocks, designed to be rendered to Clips.

`TEMPLATES` lists the ones an Edl may name. A template raises when it cannot
be built from what it was given; it never returns None.
"""

import numpy as np
from moviepy.editor import TextClip, ColorClip
from moviepy.video.compositing.CompositeVideoClip import CompositeVideoClip
from moviepy.video.compositing.concatenate import concatenate_videoclips
from otto.colortransitions import (
    makeColor,
    boxReveal,
    boxShrink,
    drawBoxOutline,
    toRgb,
)
from otto import colortransitions as ct
from otto.config import defaults
from otto.utils import rgbToDec


def _straight(clip):
    """`clip` with its colours no longer scaled by its own opacity.

    A transparent CompositeVideoClip blends its layers over black, so where it
    is partly transparent its colours are already multiplied by its opacity --
    and the composite it is placed in multiplies them by it again. A box drawn
    at 40% inside a template showed at 16%, and the antialiased edges of text
    went dark over a bright picture. Dividing by the mask here leaves the
    outer composite as the only thing that applies it.
    """
    if clip.mask is None:
        return clip
    # Read here and again by the composite this clip is placed in.
    mask = clip.mask.set_memoize(True)

    def straighten(get_frame, t):
        rgb = get_frame(t)
        alpha = mask.get_frame(t)[..., None]
        out = np.divide(rgb, alpha, out=np.zeros(rgb.shape), where=alpha > 0)
        return np.minimum(out, 255)

    return clip.fl(straighten).set_mask(mask)


def _transition(clip, index, count, seconds=1):
    """Fade one item of a sequence in from the item before it and out to the next.

    The first item does not fade in and the last does not fade out: those are
    the edges of the whole template clip, and the fades there are the clip's
    own `fadeIn` and `fadeOut`, which the engine applies.
    """
    if index > 0:
        clip = clip.crossfadein(seconds)
    if index < count - 1:
        clip = clip.crossfadeout(seconds)
    return clip


FX_CURVES = {'bezier2': ct.bezier2}
"""The effects a template's `fxs` may name: curves the template moves along."""

FX_SECONDS = 1
"""How long an effect's movement lasts, from the start of the clip."""


def _motion(fxs):
    """A position function that moves a clip along the curves `fxs` describe.

    Each fx is `{'name': <a key of FX_CURVES>, 'data': <its control points>}`,
    or an FX model. For its first FX_SECONDS the clip is offset by the point
    each curve has reached, the curve's parameter running from 0 to 1 over
    that time, summed over the fxs, in fractions of the frame; after that it
    rests at (0, 0). A curve moves the clip horizontally -- the fly-in alfred's
    seeded projects are written for, whose curves end a frame below where they
    start -- unless its data says `axes: 'xy'`, or `'y'`.

    Raises ValueError, here rather than when a frame is drawn, for an fx that
    names no curve or lacks the data its curve needs.
    """
    curves = []
    for fx in fxs:
        if isinstance(fx, dict):
            name, data = fx.get('name'), fx.get('data')
        else:
            name, data = getattr(fx, 'name', None), getattr(fx, 'data', None)
        make_curve = FX_CURVES.get(name)
        if make_curve is None:
            raise ValueError(
                f'no fx is named {name!r}; the fxs are {", ".join(FX_CURVES)}'
            )
        data = dict(data or {})
        axes = data.pop('axes', 'x')
        if axes not in ('x', 'y', 'xy'):
            raise ValueError(f'fx {name!r}: axes must be x, y or xy, not {axes!r}')
        try:
            curves.append((make_curve(**data), axes))
        except (TypeError, ValueError) as exc:
            raise ValueError(
                f'fx {name!r} needs data c1x, c1y, ax, ay, c2x and c2y: {exc}'
            ) from exc

    def position(t):
        if t >= FX_SECONDS:
            return (0, 0)
        x = y = 0.0
        for curve, axes in curves:
            point = curve.evaluate(t / FX_SECONDS)
            if 'x' in axes:
                x += float(point[0][0])
            if 'y' in axes:
                y += float(point[1][0])
        return (x, y)

    return position


def title(
    text,
    data=None,
    color=None,
    themecolor=None,
    fontsize=None,
    clipsize=(1920, 1080),
    textsize=None,
    font='Open-Sans',
    method='caption',
    duration=5,
    position='center',
    opacity=0.4,
    fps=30,
    bg=None,
    **kwargs,
):
    """Render a large Title block of text"""
    color = color or defaults['fontcolor']
    themecolor = themecolor or defaults['themecolor']
    textsize = textsize or (clipsize[0] // 2, clipsize[1] // 2)
    t = TextClip(
        text.strip(),
        color=color,
        fontsize=fontsize,
        size=textsize,
        font=font,
        method=method,
        stroke_color=None,
    ).set_position(position)
    boxclip = boxReveal(
        duration=duration, clipsize=textsize, fill=rgbToDec(themecolor)
    ).set_position(position)
    layers = [t, boxclip]
    if bg:
        # makeColor takes no opacity: passing one did nothing, so the box
        # meant to sit half-transparent behind the title was opaque.
        layers.insert(
            0,
            makeColor(textsize, color=bg, duration=duration)
            .set_position(position)
            .set_opacity(opacity),
        )
    return _straight(
        CompositeVideoClip(layers, size=clipsize)
        .set_position(position)
        .set_fps(fps)
        .set_duration(duration)
    )


def initial(
    text,
    data=None,
    color=None,
    themecolor=None,
    fontsize=None,
    clipsize=(1920, 1080),
    textsize=None,
    font='Open-Sans',
    method='caption',
    start=0,
    duration=None,
    position='center',
    opacity=0.4,
    fps=30,
    bg=None,
    fxs=None,
    **kwargs,
):
    """**DEPRICATED** Initial screen for video. Use textBox instead"""

    data = data or defaults
    color = color or data['fontcolor']
    themecolor = themecolor or data['themecolor']
    textsize = textsize or (clipsize[0] // 2, clipsize[1] // 2)
    text = text.split('. ')
    text = [t.strip() for t in text if t.strip()]
    texts = []
    bkgs = []
    st = 0
    d = 0
    tlen = len(text) - 1
    for i, t in enumerate(text):
        d = 2 + pow(len(t.split(' ')), 0.6)
        if duration and st + d > duration:
            d = duration - st
        if duration and i == tlen and st + d < duration:
            d = duration - st
        tc = (
            TextClip(
                t,
                color=color,
                fontsize=fontsize,
                size=textsize,
                font=font,
                method=method,
                stroke_color=None,
                # align='west'
            )
            .set_start(st)
            .set_duration(d)
            .set_position(position)
            .resize(textsize)
        )
        texts.append(_transition(tc, i, len(text)))
        if bg:
            bkgs.append(
                _transition(
                    ColorClip((tc.w, tc.h), color=toRgb(bg))
                    .set_duration(tc.duration)
                    .set_start(tc.start)
                    .set_position(tc.pos)
                    .set_opacity(opacity),
                    i,
                    len(text),
                )
            )
        st += d
    made = (
        CompositeVideoClip([*bkgs, *texts], size=clipsize)
        .set_position(position)
        .set_duration(duration or d)
        .set_fps(30)
    )
    if fxs:
        made = made.set_position(_motion(fxs), relative=True)
    return _straight(made)


def bullets(
    text,
    data=None,
    color=None,
    themecolor=None,
    fontsize=None,
    textsize=None,
    clipsize=(1920, 1080),
    font='Open-Sans',
    method='caption',
    start=0,
    duration=None,
    position=('center', 'center'),
    opacity=0.4,
    fps=30,
    fxs=None,
    **kwargs,
):
    """**DEPRICATED** Render bullet points to a video. Use textBox instead."""

    data = data or defaults
    color = color or data['fontcolor']
    themecolor = themecolor or data['themecolor']
    textsize = textsize or (clipsize[0] // 2, clipsize[1] // 2)
    text = text.split('\u2022')
    text = [t.strip() for t in text if t.strip()]
    if not text:
        raise ValueError('bullets needs text: bullet points separated by \u2022')
    # Built for each call. It was appended to the mutable default `fxs=[]`, so
    # the first call's overlay was reused by every later one; and an fx passed
    # in through `fxs` -- a dict -- was handed to CompositeVideoClip as a clip.
    overlay = boxShrink(clipsize=textsize, fill=rgbToDec(themecolor)).set_position(
        ('left', 'bottom')
    )
    items = []
    st = 0
    for t in text:
        d = 2 + pow(len(t.split(' ')), 0.6)
        if duration and st + d > duration:
            break
        clip = TextClip(
            t,
            color=color,
            fontsize=fontsize,
            size=textsize,
            font=font,
            method=method,
            stroke_color=None,
        ).set_position(position)
        bkg = (
            ColorClip((clip.w, clip.h), color=toRgb(themecolor))
            .set_position(clip.pos)
            .set_opacity(opacity)
        )
        items.append(
            CompositeVideoClip([bkg, clip, overlay], size=clipsize).set_duration(d)
        )
        st += d
    if duration and st < duration:
        # Nothing for the rest of the duration: a bullet that does not fit is
        # left out, and frames past the last bullet raised IndexError inside
        # concatenate_videoclips, failing any render whose bullets fell short.
        items.append(
            CompositeVideoClip([ColorClip(clipsize, color=(0, 0, 0, 0))]).set_duration(
                duration - st
            )
        )
    clips = [_transition(item, i, len(items)) for i, item in enumerate(items)]
    final = concatenate_videoclips(clips)
    if duration:
        final = final.set_duration(duration)
    if fxs:
        final = final.set_position(_motion(fxs), relative=True)
    return _straight(final)


def final(
    text,
    address=None,
    website=None,
    phone=None,
    data=None,
    color=None,
    themecolor=None,
    fontsize=None,
    clipsize=(1920, 1080),
    font='Segoe-UI-Bold',
    method='caption',
    start=0,
    duration=5,
    position='center',
    opacity=0.4,
    fps=30,
    **kwargs,
):
    """**DEPRICATED** Render an "End Credits" style information block"""
    data = data or defaults
    color = color or data['fontcolor']
    themecolor = themecolor or data['themecolor']
    fontsize = fontsize or pow(clipsize[1], 0.9) / 6 - 10
    texts = [
        TextClip(
            text,
            color=color,
            fontsize=fontsize * 1.5,
            size=clipsize,
            font=font,
            method=method,
            stroke_color=None,
            # align='north').set_position(('center', 'top')),
        ).set_position((0, -clipsize[1] // 4)),
        TextClip(
            address or data['address'],
            color=color,
            fontsize=fontsize * 0.75,
            size=clipsize,
            font=font,
            method=method,
            stroke_color=None,
            # align='west').set_position(('left', 'center')),
        ).set_position((0, -clipsize[1] // 24)),
        TextClip(
            website or data['website'],
            color=color,
            fontsize=fontsize,
            size=clipsize,
            font=font,
            method=method,
            stroke_color=None,
            # align='south').set_position(('center', 'bottom')),
        ).set_position((0, clipsize[1] // 8)),
        TextClip(
            phone or data['phone'],
            color=color,
            fontsize=fontsize,
            size=clipsize,
            font=font,
            method='label',
            stroke_color=None,
            # align='east').set_position(('right', 'center')),
        ).set_position((0, clipsize[1] // 4)),
    ]

    # fiag = flyInAndGrow(size=size,
    #         duration=duration,
    #         fill=rgbToDec(themecolor),
    #         transparent=True)

    dbo = drawBoxOutline(
        clipsize=(int(clipsize[0] * 0.85), int(clipsize[1] * 0.85)),
        duration=duration,
        fill=rgbToDec(themecolor),
        transparent=True,
    )

    return _straight(
        CompositeVideoClip([dbo, *texts], size=clipsize)
        .set_fps(fps)
        .set_duration(duration)
        .set_position((0, 0))
    )


def textBox(
    text,
    data=None,
    color=None,
    themecolor=None,
    fontsize=None,
    clipsize=(1920, 1080),
    textsize=None,
    font='Open-Sans',
    method='label',
    start=0,
    duration=None,
    position='center',
    opacity=0.4,
    fps=30,
    bg=None,
    align='center',
    fxs=None,
    **kwargs,
):
    """Render a block of text in a bounding box

    With `bg`, the box is filled with that colour at `opacity`, behind the
    text.
    """

    color = color or defaults['fontcolor']
    themecolor = themecolor or defaults['themecolor']
    textsize = textsize or (clipsize[0] // 2, clipsize[1] // 2)
    text = text.strip()
    words = (
        TextClip(
            text,
            color=color,
            fontsize=fontsize,
            size=textsize,
            font=font,
            method=method,
            stroke_color=None,
            align=align,
        )
        .set_start(start)
        .set_duration(duration)
        .set_position(position)
        .set_fps(fps)
    )
    layers = [words]
    if bg:
        # This box used to be built and then dropped, so `bg` did nothing.
        layers.insert(
            0,
            ColorClip(words.size, color=toRgb(bg))
            .set_start(start)
            .set_duration(duration)
            .set_position(position)
            .set_opacity(opacity),
        )
    tc = CompositeVideoClip(layers, size=clipsize)
    if fxs:
        tc = tc.set_position(_motion(fxs), relative=True)
    return _straight(tc)


TEMPLATES = {
    'title': title,
    'textBox': textBox,
    'initial': initial,
    'bullets': bullets,
    'final': final,
    'makeColor': makeColor,
}
"""Every template a clip may name, keyed by that name.

`generateEdl` resolves a template clip's `name` here and nowhere else. This
module's namespace also holds what the templates are built from -- TextClip,
ColorClip, concatenate_videoclips, rgbToDec, the colortransitions helpers --
and resolving names against the namespace made all of those callable from an
Edl.
"""

__all__ = ['TEMPLATES', *TEMPLATES]
