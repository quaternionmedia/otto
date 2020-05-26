from moviepy.editor import TextClip, ColorClip, ImageClip, VideoClip
from moviepy.video.compositing.CompositeVideoClip import CompositeVideoClip
from colortransitions import drawBoxOutline, circleShrink, growBox, flyInAndGrow, zoomFromCenter, boxReveal
from PIL.ImageColor import getcolor
from getdata import scale

def title(text,
            data=None,
            color=None,
            fontsize=None,
            size=(1920,1080),
            font='Segoe UI Black',
            method='caption',
            duration=5,
            position='center',
            opacity=.4,
            fps=30):
    if not color:
        color = data['FONTCOLOR']
    t = (TextClip(text.strip(),
        color=color,
        fontsize=fontsize,
        size=size,
        font=font,
        method=method,
        stroke_color=None)
            .set_position(position)
    )
    boxclip = boxReveal(duration=duration, size=size, fill=getcolor(data['THEMECOLOR'], 'RGB')).set_position(position)

    return (CompositeVideoClip([t, boxclip], size=size)
            .set_position(position)
            .set_fps(fps)
            .set_duration(duration)
            .crossfadein(1)
            .crossfadeout(1)
            )

def initial(text,
            data=None,
            color=None,
            fontsize=None,
            size=(1920,1080),
            font='Segoe UI Black',
            method='caption',
            start=0,
            duration=5,
            position='center',
            opacity=.4,
            fps=30,
            ):
    if not color:
        color = data['FONTCOLOR']
    text = text.split('.')
    text = [t.strip() for t in text if t.strip()]
    texts = [TextClip(t.strip(),
                color=color,
                fontsize=fontsize,
                size=size,
                font=font,
                method=method,
                stroke_color=None,
                align='west'
                ).set_start(i*duration)
                .set_duration(duration or 2 + pow(len(t.strip().split(' ')), .5))
                .set_position(position)
                .crossfadein(1)
                .crossfadeout(1) for i, t in enumerate(text) if t.strip()]

    bkgs = [ColorClip((t.w, t.h),color=getcolor(data['THEMECOLOR'], 'RGB'))
                .set_duration(t.duration)
                .set_start(t.start)
                .set_position(t.pos)
                .set_opacity(opacity)
                .crossfadein(1)
                .crossfadeout(1)
                for i, t in enumerate(texts)]
    return (CompositeVideoClip([*bkgs, *texts], size=size)
            .set_position(position)
            .set_fps(30))

def bullets(text,
            data=None,
            color=None,
            fontsize=None,
            size=(1920,1080),
            font='Segoe UI Black',
            method='caption',
            start=0,
            duration=None,
            position='center',
            opacity=.4,
            fps=30,
            align='west'):
    if not color:
        color = data['FONTCOLOR']
    text = text.split('\u2022')
    text = [t.strip() for t in text if t.strip()]
    print('bullet texts', text, )
    clips = []
    st = 0
    for t in text:
        d = duration or 2 + pow(len(t.split(' ')), .5)
        clip = (TextClip(t,
                    color=color,
                    fontsize=fontsize,
                    size=size,
                    font=font,
                    method=method,
                    stroke_color=None,
                    align='west'
                    ).set_start(st)
                    .set_duration(d)
                    .set_position(position)
                    .crossfadein(1)
                    .crossfadeout(1)
        )
        st += d
        bkg = (ColorClip((clip.w, clip.h),color=getcolor(data['THEMECOLOR'], 'RGB'))
                    .set_duration(clip.duration)
                    .set_start(clip.start)
                    .set_position(clip.pos)
                    .set_opacity(opacity))

        fx = (circleShrink(
                duration=clip.duration, size=clip.size, fill=getcolor(data['THEMECOLOR'], 'RGB'))
                    .set_position(('left', 'bottom'))
                    .set_start(clip.start))
        clips.append(CompositeVideoClip([bkg, clip, fx])
                    .crossfadein(1)
                    .crossfadeout(1))

    return (CompositeVideoClip(clips, size=(1920,1080))
            .set_position(position)
            .set_fps(30))

def final(text,
            data=None,
            color=None,
            fontsize=None,
            size=(1920,1080),
            font='Segoe UI Black',
            method='caption',
            start=0,
            duration=5,
            position='center',
            opacity=.4,
            fps=30,):
    if not color:
        color = data['FONTCOLOR']
    texts = [
        TextClip(text, color=color,
            fontsize=fontsize,
            size=scale(1.5),
            font=font,
            method='label',
            stroke_color=None,
            align='north').set_position(('center', 'top')),
        TextClip(data['ADDRESS'], color=color,
            fontsize=fontsize or 120,
            size=scale(2),
            font=font,
            method=method,
            stroke_color=None,
            align='west').set_position(('left', 'center')),
        TextClip(data['WEBSITE'], color=color,
            fontsize=fontsize,
            size=scale(1.5),
            font=font,
            method=method,
            stroke_color=None,
            align='south').set_position(('center', 'bottom')),
        TextClip(data['PHONE'], color=color,
            fontsize=fontsize or 120,
            size=scale(1.5),
            font=font,
            method='label',
            stroke_color=None,
            align='east').set_position(('right', 'center')),
    ]

    fiag = flyInAndGrow(size=size, duration=duration, fill=getcolor(data['THEMECOLOR'], 'RGB'), transparent=True)


    return (CompositeVideoClip([fiag, *texts], size=size)
            .set_fps(fps)
            .set_duration(duration)
            .crossfadein(1)
            .crossfadeout(1))
