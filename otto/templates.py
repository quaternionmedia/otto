from moviepy.editor import TextClip, ColorClip, ImageClip, VideoClip
from moviepy.video.compositing.CompositeVideoClip import CompositeVideoClip
from moviepy.video.compositing.concatenate import concatenate_videoclips
from PIL.ImageColor import getcolor
from otto.getdata import scale
from otto.colortransitions import *
from otto.defaults import defaults

def rgbToDec(rgb):
    color = getcolor(rgb, 'RGB')
    color = [c / 255 for c in color]
    return color

def title(text,
            data=None,
            color=None,
            themecolor=None,
            fontsize=None,
            clipsize=(1920,1080),
            textsize=None,
            font='Segoe-UI-Black',
            method='caption',
            duration=5,
            position='center',
            opacity=.4,
            fps=30,
            bg=None,
            **kwargs):
    try:
        data = data or defaults
        color = color or data['fontcolor']
        themecolor = themecolor or data['themecolor']
        textsize = textsize or (clipsize[0]//2, clipsize[1]//2)
        t = (TextClip(text.strip(),
            color=color,
            fontsize=fontsize,
            size=textsize,
            font=font,
            method=method,
            stroke_color=None)
                .set_position(position)
        )
        boxclip = boxReveal(duration=duration, size=textsize, fill=rgbToDec(themecolor)).set_position(position)
        if(bg is None):
            bgvid = makeColor(clipsize,color=(0,0,0),opacity=0)
        else:
            bgvid = resize(clipsize).set_position(position)
        return (CompositeVideoClip([bgvid, t, boxclip], size=clipsize)
                .set_position('center')
                .set_fps(fps)
                .set_duration(duration)
                .crossfadein(1)
                .crossfadeout(1)
                # .resize(size)
                )
    except Exception as e:
        print('error making title', e)

def initial(text,
            data=None,
            color=None,
            themecolor=None,
            fontsize=None,
            clipsize=(1920,1080),
            textsize=None,
            font='Segoe-UI-Black',
            method='caption',
            start=0,
            duration=5,
            position='center',
            opacity=.4,
            fps=30,
            fxs=[],
            **kwargs
            ):
    try:
        data = data or defaults
        color = color or data['fontcolor']
        themecolor = themecolor or data['themecolor']
        textsize = textsize or (clipsize[0]//2, clipsize[1]//2)
        text = text.split('.')
        text = [t.strip() for t in text if t.strip()]
        texts = []
        bkgs = []
        st = 0
        for t in text:
            d = 2 + pow(len(t.split(' ')), .6)
            if st + d > duration:
                d = duration - st
            tc = (TextClip(t,
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
            bkgs.append(ColorClip((tc.w, tc.h),color=rgbToDec(themecolor))
                    .set_duration(tc.duration)
                    .set_start(tc.start)
                    .set_position(tc.pos)
                    .set_opacity(opacity)
                    .crossfadein(1)
                    .crossfadeout(1)
            )
            st += d
        if(len(fxs) is 0):
          t = textsize

          fx = [boxShrink(size=(t[0], t[1]),
                  duration=duration,
                  fill=rgbToDec(themecolor),
                  transparent=True,
                  direction=0,
                  startpos=(t[0]//2, t[1]//2),
                  endpos=(t[0]//2, 9*t[1]//10),
                  startwh=(t[0],t[1]),
                  endwh=(int(t[0]*0.8), int(t[1]*0.1))
                  ).crossfadeout(1)]
        print('initial', bkgs, texts)
        return (CompositeVideoClip([*bkgs, *texts, *fxs], size=clipsize)
                .set_position(position)
                .set_duration(duration)
                .set_fps(30))
    except Exception as e:
        print('error making initial', e)

def bullets(text,
            data=None,
            color=None,
            themecolor=None,
            fontsize=None,
            textsize=None,
            clipsize=(1920,1080),
            font='Segoe-UI-Black',
            method='caption',
            start=0,
            duration=None,
            position=('center', 'center'),
            opacity=.4,
            fps=30,
            fxs=[],
            **kwargs):
    try:
        data = data or defaults
        color = color or data['fontcolor']
        themecolor = themecolor or data['themecolor']
        textsize = textsize or (clipsize[0]//2, clipsize[1]//2)
        text = text.split('\u2022')
        text = [t.strip() for t in text if t.strip()]
        print('bullet texts', text, )
        clips = []
        st = 0
        for t in text:
            d = 2 + pow(len(t.split(' ')), .6)
            clip = (TextClip(t,
                        color=color,
                        fontsize=fontsize,
                        size=textsize,
                        font=font,
                        method=method,
                        stroke_color=None
                        )
                        .set_position(position)
            )
            bkg = (ColorClip((clip.w, clip.h),color=rgbToDec(themecolor))
                        .set_position(clip.pos)
                        .set_opacity(opacity))
            if(len(fxs) is 0):
                fxs.append((boxShrink(
                        duration=clip.duration, size=textsize, fill=rgbToDec(themecolor))
                            .set_position(('left', 'bottom'))
                            ))
            if not duration or st + d <= duration:
                clips.append(CompositeVideoClip([bkg, clip, *fxs], size=clipsize)
                        # .set_start(st)
                        .set_duration(d)
                        .crossfadein(1)
                        .crossfadeout(1)
                        )
                print('added clip', t, clip, st, d)
            if duration and st + d > duration:
                # clips.append(CompositeVideoClip([''], duration=duration - st))
                print('adding blank clip', st, duration - st)
                clips.append(CompositeVideoClip([ColorClip(clipsize, color=(0,0,0,0))]).set_duration(duration - st))
                break
            st += d
        final = concatenate_videoclips(clips)
        if duration:
            final = final.set_duration(duration)
        return final
    except Exception as e:
        print('error making bullets', e)

def final(text,
            address=None,
            website=None,
            phone=None,
            data=None,
            color=None,
            themecolor=None,
            fontsize=None,
            clipsize=(1920,1080),
            font='Segoe-UI-Bold',
            method='caption',
            start=0,
            duration=5,
            position='center',
            opacity=.4,
            fps=30,
            **kwargs):
    try:
        data = data or defaults
        color = color or data['fontcolor']
        themecolor = themecolor or data['themecolor']
        fontsize = fontsize or pow(clipsize[1], .9)/6 - 10
        texts = [
            TextClip(text,
                color=color,
                fontsize=fontsize*1.5,
                size=clipsize,
                font=font,
                method=method,
                stroke_color=None,
                # align='north').set_position(('center', 'top')),
                ).set_position((0,-clipsize[1]//4)),
            TextClip(address or data['address'],
                color=color,
                fontsize=fontsize*.75,
                size=clipsize,
                font=font,
                method=method,
                stroke_color=None,
                # align='west').set_position(('left', 'center')),
                ).set_position((0,-clipsize[1]//24)),
            TextClip(website or data['website'],
                color=color,
                fontsize=fontsize,
                size=clipsize,
                font=font,
                method=method,
                stroke_color=None,
                # align='south').set_position(('center', 'bottom')),
                ).set_position((0,clipsize[1]//8)),
            TextClip(phone or data['phone'],
                color=color,
                fontsize=fontsize,
                size=clipsize,
                font=font,
                method='label',
                stroke_color=None,
                # align='east').set_position(('right', 'center')),
                ).set_position((0,clipsize[1]//4)),
        ]

        # fiag = flyInAndGrow(size=size,
        #         duration=duration,
        #         fill=rgbToDec(themecolor),
        #         transparent=True)

        dbo = drawBoxOutline(
                size=(int(clipsize[0]*0.85), int(clipsize[1]*0.85)),
                duration=duration,
                fill=rgbToDec(themecolor),
                transparent=True)


        return (CompositeVideoClip([dbo, *texts], size=clipsize)
                .set_fps(fps)
                .set_duration(duration)
                .set_position((0,0))
                .crossfadein(1)
                .crossfadeout(1)
                )
    except Exception as e:
        print('error making final', e)
