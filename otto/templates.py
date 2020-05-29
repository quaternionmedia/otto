# from moviepy.editor import TextClip, ColorClip, ImageClip, VideoClip
import moviepy.editor as e
from moviepy.video.compositing.CompositeVideoClip import CompositeVideoClip
# from colortransitions import drawBoxOutline, circleShrink, growBox, flyInAndGrow, zoomFromCenter, boxReveal
import colortransitions as ct
# from PIL.ImageColor import getcolor
import PIL.ImageColor as ic
from getdata import scale


def title(text,
            data=None,
            color=None,
            fontsize=None,
            clipsize=(1920,1080),
            textsize=(1920//2, 1080//2),
            font='Segoe UI Black',
            method='caption',
            duration=5,
            position='center',
            opacity=.4,
            fps=30,
            bg=None):
    if not color:
        color = data['FONTCOLOR']
    t = (e.TextClip(text.strip(),
        color=color,
        fontsize=fontsize,
        size=textsize,
        font=font,
        method=method,
        stroke_color=None)
            .set_position(position)
    )
    boxclip = ct.boxReveal(duration=duration, size=textsize, fill=ic.getcolor(data['THEMECOLOR'], 'RGB')).set_position(position)
    if(bg is None):
        bgvid = ct.makeColor(clipsize,color=(0,0,0),opacity=0)
    else:
        bgvid = bg.resize(clipsize).set_position(position)
    return (CompositeVideoClip([bgvid, t, boxclip], size=clipsize)
            .set_position('center')
            .set_fps(fps)
            .set_duration(duration)
            .crossfadein(1)
            .crossfadeout(1)
            # .resize(size)
            )

def initial(text,
            data=None,
            color=None,
            fontsize=None,
            clipsize=(1920,1080),
            textsize=(1920//2, 1080//2),
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
    texts = []
    bkgs = []
    st = 0
    for t in text:
        d = 2 + pow(len(t.split(' ')), .6)
        if st + d > duration:
            d = duration - st
        tc = (e.TextClip(t,
                    color=color,
                    fontsize=fontsize,
                    size=textsize,
                    font=font,
                    method=method,
                    stroke_color=None,
                    # align='west'
                ).set_start(st)
                .set_duration(d)
                .set_position(position)
                .resize(textsize)
                .crossfadein(1)
                .crossfadeout(1)
                )
        texts.append(tc)
        bkgs.append(e.ColorClip((tc.w, tc.h),color=ic.getcolor(data['THEMECOLOR'], 'RGBA'))
                .set_duration(tc.duration)
                .set_start(tc.start)
                .set_position(tc.pos)
                .set_opacity(opacity)
                .crossfadein(1)
                .crossfadeout(1)
        )
        st += d
    # zfc = ct.zoomFromCenter(size=textsize,
    #         duration=duration,
    #         fill=ic.getcolor(data['THEMECOLOR'], 'RGB'),
    #         transparent=True)
    print('initial', bkgs, texts)
    return (CompositeVideoClip([*bkgs, *texts], size=clipsize)
            .set_position(position)
            .set_fps(30))

def bullets(text,
            data=None,
            color=None,
            fontsize=None,
            textsize=(1920//2, 1080//2),
            clipsize=(1920,1080),
            font='Segoe UI Black',
            method='caption',
            start=0,
            duration=None,
            position=('center', 'center'),
            opacity=.4,
            fps=30):
    if not color:
        color = data['FONTCOLOR']
    text = text.split('\u2022')
    text = [t.strip() for t in text if t.strip()]
    print('bullet texts', text, )
    clips = []
    st = 0
    for t in text:
        d = 2 + pow(len(t.split(' ')), .6)
        clip = (e.TextClip(t,
                    color=color,
                    fontsize=fontsize,
                    size=textsize,
                    font=font,
                    method=method,
                    stroke_color=None
                    )
                    .set_position(position)
        )
        bkg = (e.ColorClip((clip.w, clip.h),color=ic.getcolor(data['THEMECOLOR'], 'RGB'))
                    .set_position(clip.pos)
                    .set_opacity(opacity))

        fx = (ct.boxShrink(
                duration=clip.duration, size=textsize, fill=ic.getcolor(data['THEMECOLOR'], 'RGB'))
                    .set_position(position)
                    )
        if st + d <= duration:
            clips.append(CompositeVideoClip([bkg, clip, fx], size=clipsize)
                        # .set_start(st)
                        .set_duration(d)
                        .crossfadein(1)
                        .crossfadeout(1)
                        )
        st += d
    return clips

def final(text,
            data=None,
            color=None,
            fontsize=20,
            clipsize=(1920,1080),
            font='Segoe UI Bold',
            method='caption',
            start=0,
            duration=5,
            position='center',
            opacity=.4,
            fps=30,):
    if not color:
        color = data['FONTCOLOR']
    texts = [
        e.TextClip(text,
            color=color,
            fontsize=60,
            size=clipsize,
            font=font,
            method=method,
            stroke_color=None,
            # align='north').set_position(('center', 'top')),
            ).set_position((0,-clipsize[1]//5)),
        e.TextClip(data['ADDRESS'],
            color=color,
            fontsize=50,
            size=clipsize,
            font=font,
            method=method,
            stroke_color=None,
            # align='west').set_position(('left', 'center')),
            ).set_position((0,-clipsize[1]//10)),
        e.TextClip(data['WEBSITE'],
            color=color,
            fontsize=60,
            size=clipsize,
            font=font,
            method=method,
            stroke_color=None,
            # align='south').set_position(('center', 'bottom')),
            ).set_position((0,clipsize[1]//10)),
        e.TextClip(data['PHONE'],
            color=color,
            fontsize=60,
            size=clipsize,
            font=font,
            method='label',
            stroke_color=None,
            # align='east').set_position(('right', 'center')),
            ).set_position((0,clipsize[1]//5)),
    ]

    # fiag = ct.flyInAndGrow(size=size,
    #         duration=duration,
    #         fill=ic.getcolor(data['THEMECOLOR'], 'RGB'),
    #         transparent=True)

    dbo = ct.drawBoxOutline(
            size=(int(clipsize[0]*0.7), int(clipsize[1]*0.7)),
            duration=duration,
            fill=ic.getcolor(data['THEMECOLOR'], 'RGB'),
            transparent=True)


    return (CompositeVideoClip([dbo, *texts], size=clipsize)
            .set_fps(fps)
            .set_duration(duration)
            .set_position((0,0))
            .crossfadein(1)
            # .crossfadeout(1)
            )
