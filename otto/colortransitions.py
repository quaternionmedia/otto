import gizeh
import moviepy.editor as e

clipsize = (800,600)
defaultdur = 5
defaultfill = (0,0,0.7)
defaultbg = (0,0,0,0)
transparent = True


def makeClip(f):
    video = e.VideoClip(f)
    mask = e.VideoClip(lambda t: f(t)[:,:,3]/255.0, ismask=True)
    clip = e.VideoClip(lambda t: f(t)[:,:,:3]).set_mask(mask).set_position('center')
    return clip

def makeColor(
        size, #tuple (x,y)
        color=(1,1,1), #tuple (r,g,b)
        position=(0,0), #tuple (x,y) from top left
        opacity=0.5,
        start=0,
        duration=5
        ):
        return (e.ColorClip(size,color=color)
                    .set_position(position)
                    .set_opacity(opacity)
                    .set_start(start)
                    .set_duration(duration)
                    .set_fps(30)
                    .crossfadein(1)
                    .crossfadeout(1)
                    )

def growBox(duration=defaultdur, size=clipsize, fill=defaultfill, transparent=transparent):
    surface = gizeh.Surface(size[0],size[1],bg_color=defaultbg)
    def gb(t):
        x = size[0]/2
        y = size[1]/2
        gstart = 0
        gend = 1
        staticduration = duration - gend
        w = 0
        h = size[1]
        if(t > gstart and t < gend):
            w = t*size[0]//gend
        if(t>gend and t<duration):
            w = size[0]
        # print(w, h)
        rect = gizeh.rectangle(lx=w,ly=h,xy=(400,300),fill=fill)
        rect.draw(surface)

        return surface.get_npimage(transparent=transparent)
    return makeClip(gb).set_duration(duration)

def boxReveal(duration=5, size=(800,600), padding=(100,20), fill=(0,0,.5)):
    w = size[0]+padding[0]*2
    def br(t):
        surface = gizeh.Surface(w,size[1]+padding[1]*2,bg_color=(0,0,0,0))
        x = max(w - t * (size[0] + padding[0]) / duration * 6, padding[0])
        rect = gizeh.rectangle(lx=x,ly=size[1]+padding[1]*2,xy=(x/2,size[1]/2),fill=fill)
        rect.draw(surface)
        return surface.get_npimage(transparent=True)
    return makeClip(br).set_duration(duration)

def flyInAndGrow(duration=defaultdur, size=clipsize, fill=defaultfill, transparent=transparent):
    def fiag(t):
        surface = gizeh.Surface(size[0],size[1],bg_color=(0, 0, 0, 0))
        fend = 0.5
        gstart = fend
        gend = 1.5
        # staticduration = duration - gend
        w = size[0]*0.1
        h = size[1]
        x = size[0]/2
        y = -size[1]/2
        if t <= gend:
            if (t <= fend):
                y = -h/2 + t/fend*h
            else:
                y = size[1]/2
                w = w + size[0]*((t-fend)/(gend-gstart))
        else:
            w, h = size[0], size[1]
            x, y = size[0]/2, size[1]/2
        rect = gizeh.rectangle(lx=w,ly=h,xy=(x,y),fill=fill)
        rect.draw(surface)
        return surface.get_npimage(transparent=transparent)
    return makeClip(fiag).set_duration(duration)

def zoomFromCenter(duration=defaultdur, size=clipsize, fill=defaultfill, transparent=transparent):
    def zfc(t):
        surface = gizeh.Surface(size[0], size[1], bg_color=defaultbg)
        zstart = 0
        zend = 1
        staticduration = duration - (zend-zstart)
        w = 0
        h = 0
        x = size[0]/2
        y = size[1]/2
        if (t < zend):
            w = t*size[0]/zend
            h = t*size[1]/zend
        else:
            w, h = size[0]/zend, size[1]/zend
        rect = gizeh.rectangle(lx=w, ly=h, xy=(x,y),fill=fill)
        rect.draw(surface)

        return surface.get_npimage(transparent=transparent)
    return makeClip(zfc).set_duration(duration)

def circleShrink(duration=defaultdur, size=clipsize, fill=defaultfill, transparent=transparent):
    def cs(t):
        surface = gizeh.Surface(size[0], size[1], bg_color=defaultbg)
        send = 1
        r = 10
        x = r
        if(t <= send):
            r = (send-t)*size[0]/2 + r
            x = (send-t)*size[0]/2
        y = size[1]/2

        circle = gizeh.circle(r=r, xy=[x,y], fill=fill)
        circle.draw(surface)

        return surface.get_npimage(transparent=transparent)
    return makeClip(cs).set_duration(duration)

def boxShrink(duration=defaultdur, size=clipsize, fill=defaultfill, transparent=transparent):
    def cs(t):
        surface = gizeh.Surface(size[0], size[1], bg_color=defaultbg)
        send = 1
        r = 10
        x = r
        if(t <= send):
            r = (send-t)*size[0]/2 + r
            x = (send-t)*size[0]/2
        y = size[1]/2

        circle = gizeh.rectangle(lx=r, ly=r, xy=(x,y), fill=fill)
        circle.draw(surface)

        return surface.get_npimage(transparent=transparent)
    return makeClip(cs).set_duration(duration)

def drawBoxOutline(duration=defaultdur, size=clipsize, fill=defaultfill, transparent=transparent):
    def dbo(t):
        surface = gizeh.Surface(size[0], size[1], bg_color=defaultbg)

        dstart = 0
        dend = 1

        stroke = 20
        x = size[0]/2
        y = size[1]/2
        w = size[0]
        h = size[1]

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

        topline.draw(surface)
        bottomline.draw(surface)
        rightline.draw(surface)
        leftline.draw(surface)

        return surface.get_npimage(transparent=transparent)
    return makeClip(dbo).set_duration(duration)


if __name__ == '__main__':
    clips = [
                drawBoxOutline(),
                circleShrink(),
                growBox(),
                boxReveal(),
                flyInAndGrow(),
                zoomFromCenter()
                ]

    final_clips = e.concatenate_videoclips(clips)
    final_clips.write_videofile("output/transitiontest.mp4", fps=30)