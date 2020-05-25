import moviepy.editor as e
import colortransitions as ct
import PIL.ImageColor as ic

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
    t = (e.TextClip(text.rstrip().lstrip(),
        color=color,
        fontsize=fontsize,
        size=size,
        font=font,
        method=method,
        stroke_color=None)
            .set_position(position)
    )
    boxclip = ct.boxReveal(duration=duration, size=size, fill=ic.getcolor(data['THEMECOLOR'], 'RGB')).set_position(position)

    return (e.CompositeVideoClip([t, boxclip], size=size)
            .set_position('center')
            .set_fps(fps)
            .set_duration(duration)
            # .resize(lambda t: min(t+.01, 1))
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
    text = [t.lstrip().rstrip() for t in text if t.lstrip().rstrip()]
    texts = [e.TextClip(t.rstrip().lstrip(),
                color=color,
                fontsize=fontsize,
                size=size,
                font=font,
                method=method,
                stroke_color=None,
                align='west'
                ).set_start(i*duration)
                .set_duration(duration or 2 + pow(len(t.rstrip().lstrip().split(' ')), .5))
                .set_position(position)
                .crossfadein(1)
                .crossfadeout(1) for i, t in enumerate(text) if t.rstrip().lstrip()]

    bkgs = [e.ColorClip((t.w, t.h),color=ic.getcolor(data['THEMECOLOR'], 'RGB'))
                .set_duration(t.duration)
                .set_start(t.start)
                .set_position(t.pos)
                .set_opacity(opacity)
                .crossfadein(1)
                .crossfadeout(1)
                for i, t in enumerate(texts)]
    return (e.CompositeVideoClip([*bkgs, *texts], size=size)
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
            duration=5,
            position='center',
            opacity=.4,
            fps=30,
            align='west'):
    if not color:
        color = data['FONTCOLOR']
    text = text.split('\u2022')
    text = [t.lstrip().rstrip() for t in text if t.lstrip().rstrip()]
    print('bullet texts', text)
    texts = [e.TextClip(t,
                color=color,
                fontsize=fontsize,
                size=size,
                font=font,
                method=method,
                stroke_color=None,
                align='west'
                ).set_start(i*duration)
                .set_duration(duration)
                .set_position(position)
                .crossfadein(1)
                .crossfadeout(1) for i, t in enumerate(text) if t.rstrip().lstrip()]

    bkgs = [e.ColorClip((t.w, t.h),color=ic.getcolor(data['THEMECOLOR'], 'RGB'))
                .set_duration(t.duration)
                .set_start(t.start)
                .set_position(t.pos)
                .set_opacity(opacity)
                .crossfadein(1)
                .crossfadeout(1)
                for i, t in enumerate(texts)]
    return (e.CompositeVideoClip([*bkgs, *texts], size=size)
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
        e.TextClip(text, color=color,
            fontsize=fontsize,
            size=size,
            font=font,
            method='label',
            stroke_color=None,
            align='north').set_position(('center', 'top')),
        e.TextClip(data['ADDRESS'], color=color,
            fontsize=fontsize,
            size=size,
            font=font,
            method=method,
            stroke_color=None,
            align='west').set_position(('left', 'center')),
        e.TextClip(data['WEBSITE'], color=color,
            fontsize=fontsize,
            size=size,
            font=font,
            method=method,
            stroke_color=None,
            align='south').set_position(('center', 'bottom')),
        e.TextClip(data['PHONE'], color=color,
            fontsize=fontsize,
            size=size,
            font=font,
            method=method,
            stroke_color=None,
            align='east').set_position(('right', 'center')),
    ]

    fiag = ct.flyInAndGrow(size=size, duration=duration, fill=ic.getcolor(data['THEMECOLOR'], 'RGB'), transparent=True)#, size=scale(2))


    return (e.CompositeVideoClip([fiag, *texts], size=size)
            .set_fps(fps)
            .set_duration(duration)
            .crossfadein(1)
            .crossfadeout(1))
