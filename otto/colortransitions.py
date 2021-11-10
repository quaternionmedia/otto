import gizeh
import moviepy.editor as e
import bezier
import numpy as np

defaultClipsize = (800,600)
defaultdur = 5
defaultfill = (0,0,0.7)
defaultbg = (0,0,0,0)
transparent = True

def translate(value, leftMin, leftMax, rightMin, rightMax):
    # Figure out how 'wide' each range is
    leftSpan = leftMax - leftMin
    rightSpan = rightMax - rightMin

    # Convert the left range into a 0-1 range (float)
    valueScaled = float(value - leftMin) / float(leftSpan)

    # Convert the 0-1 range into a value in the right range.
    return rightMin + (valueScaled * rightSpan)

def maprange(a, b, s):
	(a1, a2), (b1, b2) = a, b
	return  b1 + ((s - a1) * (b2 - b1) / (a2 - a1))


def makeClip(f):
    video = e.VideoClip(f)
    mask = e.VideoClip(lambda t: f(t)[:,:,3]/255.0, ismask=True)
    clip = e.VideoClip(lambda t: f(t)[:,:,:3]).set_mask(mask).set_position('center')
    return clip

def makeColor(
        clipsize=defaultClipsize, #tuple (x,y)
        color=(1,1,1), #tuple (r,g,b)
        position=(0,0), #tuple (x,y) from top left
        opacity=0.5,
        start=0,
        duration=5,
        **kwargs):
        return (e.ColorClip(tuple(clipsize),color=tuple(color))
                    .set_position(position)
                    .set_opacity(opacity)
                    .set_start(start)
                    .set_duration(duration)
                    .set_fps(30)
                    .crossfadein(1)
                    .crossfadeout(1)
                    )

def growBox(duration=defaultdur, clipsize=defaultClipsize, fill=defaultfill, transparent=transparent, **kwargs):
    surface = gizeh.Surface(clipsize[0],clipsize[1],bg_color=defaultbg)
    def gb(t):
        x = clipsize[0]/2
        y = clipsize[1]/2
        gstart = 0
        gend = 1
        staticduration = duration - gend
        w = 0
        h = clipsize[1]
        if(t > gstart and t < gend):
            w = t*clipsize[0]//gend
        if(t>gend and t<duration):
            w = clipsize[0]
        # print(w, h)
        rect = gizeh.rectangle(lx=w,ly=h,xy=(400,300),fill=fill)
        rect.draw(surface)

        return surface.get_npimage(transparent=transparent)
    return makeClip(gb).set_duration(duration)

def boxReveal(duration=5, clipsize=defaultClipsize, padding=(100,20), fill=(0,0,.5), **kwargs):
    w = clipsize[0]+padding[0]*2
    def br(t):
        surface = gizeh.Surface(w,clipsize[1]+padding[1]*2,bg_color=(0,0,0,0))
        x = max(w - t * (clipsize[0] + padding[0]) / duration * 6, padding[0])
        rect = gizeh.rectangle(lx=x,ly=clipsize[1]+padding[1]*2,xy=(x/2,clipsize[1]/2),fill=fill)
        rect.draw(surface)
        return surface.get_npimage(transparent=True)
    return makeClip(br).set_duration(duration)

def flyInAndGrow(duration=defaultdur, clipsize=defaultClipsize, fill=defaultfill, transparent=transparent, **kwargs):
    def fiag(t):
        surface = gizeh.Surface(clipsize[0],clipsize[1],bg_color=(0, 0, 0, 0))
        fend = 0.5
        gstart = fend
        gend = 1.5
        # staticduration = duration - gend
        w = clipsize[0]*0.1
        h = clipsize[1]
        x = clipsize[0]/2
        y = -clipsize[1]/2
        if t <= gend:
            if (t <= fend):
                y = -h/2 + t/fend*h
            else:
                y = clipsize[1]/2
                w = w + clipsize[0]*((t-fend)/(gend-gstart))
        else:
            w, h = clipsize[0], clipsize[1]
            x, y = clipsize[0]/2, clipsize[1]/2
        rect = gizeh.rectangle(lx=w,ly=h,xy=(x,y),fill=fill)
        rect.draw(surface)
        return surface.get_npimage(transparent=transparent)
    return makeClip(fiag).set_duration(duration)

def bezier2(c1x, c1y, ax, ay, c2x, c2y, **kwargs):
    # return 2nd order bezier of parameters
    nodes = np.asfortranarray([
        [c1x, ax, c2x],
        [c1y, ay, c2y]
    ])
    return bezier.Curve(nodes, degree=2)

def makeBezier(
    c1x, c1y, ax, ay, c2x, c2y,
    duration=defaultdur, 
    clipsize=defaultClipsize, 
    fill=defaultfill, 
    transparent=transparent,
    **kwargs
    ):
    curve = bezier2(c1x, c1y, ax, ay, c2x, c2y)
    
    def bez(t):
        surface = gizeh.Surface(clipsize[0],clipsize[1],bg_color=(0, 0, 0, 0))

        w = clipsize[0]
        h = clipsize[1]

        x = curve.evaluate(float(t))[0][0]*w/2
        y = curve.evaluate(float(t))[1][0]*h/2

        rect = gizeh.rectangle(lx=w, ly=h,xy=(x,y),fill=fill)
        rect.draw(surface)
        return surface.get_npimage(transparent=transparent)
    return makeClip(bez).set_duration(duration)
        

def zoomFromCenter(duration=defaultdur, clipsize=defaultClipsize, fill=defaultfill, transparent=transparent, **kwargs):
    def zfc(t):
        surface = gizeh.Surface(clipsize[0], clipsize[1], bg_color=defaultbg)
        zstart = 0
        zend = 1
        staticduration = duration - (zend-zstart)
        w = 0
        h = 0
        x = clipsize[0]/2
        y = clipsize[1]/2
        if (t < zend):
            w = t*clipsize[0]/zend
            h = t*clipsize[1]/zend
        else:
            w, h = clipsize[0]/zend, clipsize[1]/zend
        rect = gizeh.rectangle(lx=w, ly=h, xy=(x,y),fill=fill)
        rect.draw(surface)

        return surface.get_npimage(transparent=transparent)
    return makeClip(zfc).set_duration(duration)

def circleShrink(duration=defaultdur, clipsize=defaultClipsize, fill=defaultfill, transparent=transparent, **kwargs):
    def cs(t):
        surface = gizeh.Surface(clipsize[0], clipsize[1], bg_color=defaultbg)
        send = 1
        r = 10
        x = r
        if(t <= send):
            r = (send-t)*clipsize[0]/2 + r
            x = (send-t)*clipsize[0]/2
        y = clipsize[1]/2

        circle = gizeh.circle(r=r, xy=[x,y], fill=fill)
        circle.draw(surface)

        return surface.get_npimage(transparent=transparent)
    return makeClip(cs).set_duration(duration)

def boxShrink(duration=defaultdur,
        clipsize=defaultClipsize,
        fill=defaultfill,
        transparent=transparent,
        startpos=(0,0),
        endpos=(0,0),
        startwh=(0,0),
        endwh=(0,0),
        shirnkdur=1,
        direction=-1, #0-360, -1 is defaults
        **kwargs):

    #need to declare here b/c the returned function can only t passed in
    spos = startpos
    epos = endpos
    swh = startwh
    ewh = endwh

    def bs(t):
        surface = gizeh.Surface(clipsize[0], clipsize[1], bg_color=defaultbg)
        w = clipsize[0]
        h = clipsize[1]

        if(direction == -1):
            startpos=(w//2, h//2)
            startwh=(w, h)
            endpos = (w//10, h//2)
            endwh = (int(w * 0.2), int(h * 0.7))

        x = spos[0]
        y = spos[1]

        if(t <= shirnkdur):
            x = translate(t, 0, shirnkdur, spos[0], epos[0])
            y = translate(t, 0, shirnkdur, spos[1], epos[1])
            w = translate(t, 0, shirnkdur, swh[0], ewh[0])
            h = translate(t, 0, shirnkdur, swh[1], ewh[1])
        else:
            x = epos[0]
            y = epos[1]
            w = ewh[0]
            h = ewh[1]

        circle = gizeh.rectangle(lx=w, ly=h, xy=(x,y), fill=fill)
        circle.draw(surface)

        return surface.get_npimage(transparent=transparent)
    return makeClip(bs).set_duration(duration)

def drawBoxOutline(duration=defaultdur, clipsize=defaultClipsize, fill=defaultfill, transparent=transparent, **kwargs):
    def dbo(t):
        surface = gizeh.Surface(clipsize[0], clipsize[1], bg_color=defaultbg)

        dstart = 0
        dend = 1

        stroke = 20
        x = clipsize[0]/2
        y = clipsize[1]/2
        w = clipsize[0]
        h = clipsize[1]

        topline = gizeh.rectangle(lx=0, ly=0, xy=(x,stroke/2),fill=fill)
        bottomline = gizeh.rectangle(lx=0, ly=0, xy=(x,(h-(stroke/2))),fill=fill)
        rightline = gizeh.rectangle(lx=0, ly=0, xy=(w-(stroke/2),y),fill=fill)
        leftline = gizeh.rectangle(lx=0, ly=0, xy=(stroke/2,y),fill=fill)

        t1 = 0.25
        t2 = 0.5
        t3 = 1
        t4 = 1.5

        if(t<t1):
            topline = gizeh.rectangle(lx=w*(t/t1), ly=stroke, xy=(x*(t/t1),stroke/2),fill=fill)
        elif(t>=t1 and t<t2):
            topline = gizeh.rectangle(lx=w, ly=stroke, xy=(x,stroke/2),fill=fill)
            rightline = gizeh.rectangle(lx=stroke, ly=h*((t-t1)/(t2-t1)), xy=((w-(stroke/2)),y*((t-t1)/(t2-t1))), fill=fill)
        elif(t>=t2 and t<t3):
            topline = gizeh.rectangle(lx=w, ly=stroke, xy=(x,stroke/2),fill=fill)
            rightline = gizeh.rectangle(lx=stroke, ly=h, xy=(w-(stroke/2),y),fill=fill)
            bottomline = gizeh.rectangle(lx=w*((t-t2)/(t3-t2)), ly=stroke, xy=(w-(x*((t-t2)/(t3-t2))),(h-(stroke/2))),fill=fill)
        elif(t>=t3 and t<t4):
            topline = gizeh.rectangle(lx=w, ly=stroke, xy=(x,stroke/2),fill=fill)
            bottomline = gizeh.rectangle(lx=w, ly=stroke, xy=(x,(h-(stroke/2))),fill=fill)
            rightline = gizeh.rectangle(lx=stroke, ly=h, xy=(w-(stroke/2),y),fill=fill)
            leftline = gizeh.rectangle(lx=stroke, ly=(h*((t-t3)/(t4-t3))), xy=(stroke/2,h-(y*((t-t3)/(t4-t3)))),fill=fill)

        else:
            topline = gizeh.rectangle(lx=w, ly=stroke, xy=(x,stroke/2),fill=fill)
            bottomline = gizeh.rectangle(lx=w, ly=stroke, xy=(x,(h-(stroke/2))),fill=fill)
            rightline = gizeh.rectangle(lx=stroke, ly=h, xy=(w-(stroke/2),y),fill=fill)
            leftline = gizeh.rectangle(lx=stroke, ly=h, xy=(stroke/2,y),fill=fill)

        bkg = gizeh.rectangle(lx=w*2, ly=h*2, fill=(.1,.1,.1,.5))
        bkg.draw(surface)
        topline.draw(surface)
        bottomline.draw(surface)
        rightline.draw(surface)
        leftline.draw(surface)

        return surface.get_npimage(transparent=transparent)
    return makeClip(dbo).set_duration(duration)


if __name__ == '__main__':
    clips = [
                # drawBoxOutline(),
                # circleShrink(),
                # growBox(),
                # boxReveal(),
                # flyInAndGrow(),
                # zoomFromCenter(),
                # boxShrink()
                makeBezier(0,0,0,0,1,1)
                ]

    final_clips = e.concatenate_videoclips(clips)
    final_clips.write_videofile("output/transitiontest.mp4", fps=30)
