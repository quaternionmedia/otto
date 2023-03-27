"""Templates

Prebuilt Template blocks, designed to be rendered to Clips
"""

from moviepy.editor import TextClip, ColorClip
from moviepy.video.compositing.CompositeVideoClip import CompositeVideoClip
from moviepy.video.compositing.concatenate import concatenate_videoclips
from otto.colortransitions import makeColor, boxReveal, boxShrink, drawBoxOutline
from otto import colortransitions as ct
from otto.config import defaults
from otto.utils import rgbToDec


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
    try:
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
            duration=duration, size=textsize, fill=rgbToDec(themecolor)
        ).set_position(position)
        bgvid = makeColor(
            textsize, color=rgbToDec(bg) if bg else (0, 0, 0), opacity=0.5 if bg else 0
        ).set_position(position)
        return (
            CompositeVideoClip(
                [bgvid, t, boxclip] if bg else [t, boxclip], size=clipsize
            )
            .set_position(position)
            .set_fps(fps)
            .set_duration(duration)
            .crossfadein(1)
            .crossfadeout(1)
        )
    except Exception as e:
        print('error making title', e)


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
    fxs=[],
    **kwargs,
):
    """**DEPRICATED** Initial screen for video. Use textBox instead"""

    try:
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
                .crossfadein(1)
                .crossfadeout(1)
            )
            texts.append(tc)
            if bg:
                bkgs.append(
                    ColorClip((tc.w, tc.h), color=rgbToDec(bg))
                    .set_duration(tc.duration)
                    .set_start(tc.start)
                    .set_position(tc.pos)
                    .set_opacity(opacity)
                    .crossfadein(1)
                    .crossfadeout(1)
                )
            st += d
        print('initial', bkgs, texts)
        return (
            CompositeVideoClip([*bkgs, *texts, *fxs], size=clipsize)
            .set_position(position)
            .set_duration(duration or d)
            .set_fps(30)
        )
    except Exception as e:
        print('error making initial', e)


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
    fxs=[],
    **kwargs,
):
    """**DEPRICATED** Render bullet points to a video. Use textBox instead."""

    try:
        data = data or defaults
        color = color or data['fontcolor']
        themecolor = themecolor or data['themecolor']
        textsize = textsize or (clipsize[0] // 2, clipsize[1] // 2)
        text = text.split('\u2022')
        text = [t.strip() for t in text if t.strip()]
        print(
            'bullet texts',
            text,
        )
        clips = []
        st = 0
        for t in text:
            d = 2 + pow(len(t.split(' ')), 0.6)
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
                ColorClip((clip.w, clip.h), color=rgbToDec(themecolor))
                .set_position(clip.pos)
                .set_opacity(opacity)
            )
            if len(fxs) == 0:
                fxs.append(
                    (
                        boxShrink(
                            duration=clip.duration,
                            size=textsize,
                            fill=rgbToDec(themecolor),
                        ).set_position(('left', 'bottom'))
                    )
                )
            if not duration or st + d <= duration:
                clips.append(
                    CompositeVideoClip([bkg, clip, *fxs], size=clipsize)
                    # .set_start(st)
                    .set_duration(d)
                    .crossfadein(1)
                    .crossfadeout(1)
                )
                print('added clip', t, clip, st, d)
            if duration and st + d > duration:
                # clips.append(CompositeVideoClip([''], duration=duration - st))
                print('adding blank clip', st, duration - st)
                clips.append(
                    CompositeVideoClip(
                        [ColorClip(clipsize, color=(0, 0, 0, 0))]
                    ).set_duration(duration - st)
                )
                break
            st += d
        final = concatenate_videoclips(clips)
        if duration:
            final = final.set_duration(duration)
        return final
    except Exception as e:
        print('error making bullets', e)


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
    try:
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
            size=(int(clipsize[0] * 0.85), int(clipsize[1] * 0.85)),
            duration=duration,
            fill=rgbToDec(themecolor),
            transparent=True,
        )

        return (
            CompositeVideoClip([dbo, *texts], size=clipsize)
            .set_fps(fps)
            .set_duration(duration)
            .set_position((0, 0))
            .crossfadein(1)
            .crossfadeout(1)
        )
    except Exception as e:
        print('error making final', e)


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
    """Render a block of text in a bounding box"""

    try:
        color = color or defaults['fontcolor']
        themecolor = themecolor or defaults['themecolor']
        textsize = textsize or (clipsize[0] // 2, clipsize[1] // 2)
        text = text.strip()
        tc = CompositeVideoClip(
            [
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
                # .resize(textsize)
                .set_fps(fps)
                .crossfadein(1)
                .crossfadeout(1)
            ],
            size=clipsize,
        )
        if fxs:
            for fx in fxs:
                effect = getattr(ct, fx['name'])
                tc = tc.set_position(
                    lambda t: (
                        effect(**fx['data']).evaluate(t).tolist()[0][0] if t < 1 else 0,
                        0,
                    ),
                    relative=True,
                )
        bkgs = []
        if bg:
            bkgs.append(
                ColorClip((tc.w, tc.h), color=rgbToDec(bg))
                .set_duration(tc.duration)
                .set_start(tc.start)
                .set_position(tc.pos)
                .set_opacity(opacity)
                .crossfadein(1)
                .crossfadeout(1)
            )

        print('textBox', bkgs, fxs)
        return tc
    except Exception as e:
        print('error making textBox', e)
