import gizeh
from moviepy.editor import VideoClip, CompositeVideoClip, ColorClip, concatenate_videoclips

clipsize = (800,600)
defaultdur = 5
defaultfill = (0,0,0.7)
defaultbg = (0,0,0,0)
isTransparent = False

def growBox(duration=defaultdur, size=clipsize, fill=defaultfill, isTransparent=isTransparent):
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

        return surface.get_npimage(transparent=isTransparent)
    return gb

def boxReveal(duration=5, size=(800,600), padding=(100,20), color=(0,0,.5)):
    w = size[0]+padding[0]*2
    def br(t):
        surface = gizeh.Surface(w,size[1]+padding[1]*2,bg_color=(0,0,0,0))
        x = max(w - t * (size[0] + padding[0]) / duration * 6, padding[0])
        rect = gizeh.rectangle(lx=x,ly=size[1]+padding[1]*2,xy=(x/2,size[1]/2),fill=color)
        rect.draw(surface)
        return surface.get_npimage(transparent=True)
    boxVideo = VideoClip(br)
    boxMask = VideoClip(lambda t: br(t)[:,:,3]/255.0, ismask=True, duration=duration)
    boxClip = VideoClip(lambda t: br(t)[:,:,:3], duration=duration, ).set_mask(boxMask).set_position('center')
    return boxClip

def flyInAndGrow(duration=defaultdur, size=clipsize, fill=defaultfill, isTransparent=isTransparent):
    def fiag(t):
        surface = gizeh.Surface(size[0],size[1],bg_color=(0, 0, 0, 0))
        fstart = 0
        fend = 0.5
        gstart = fend
        gend = 1.5
        # staticduration = duration - gend
        w = size[0]*0.1
        h = size[1]*0.8
        x = size[0]/2
        y = -size[1]/2
        if t <= gend:
            if (t <= fend):
                y = -h/2 + t*h*2
            else:
                y = size[1]/2
                w = size[0]*(t*0.8/gend)
        else:
            w, h = size[0]*.8, size[1]*.8
            x, y = size[0]/2, size[1]/2
        rect = gizeh.rectangle(lx=w,ly=h,xy=(x,y),fill=fill)
        rect.draw(surface)
        return surface.get_npimage(transparent=isTransparent)
    return fiag

def zoomFromCenter(duration=defaultdur, size=clipsize, fill=defaultfill, isTransparent=isTransparent):
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

        return surface.get_npimage(transparent=isTransparent)
    return zfc

if __name__ == '__main__':
    # gb = VideoClip(growBox()).set_duration(defaultdur)
    # bg = ColorClip(clipsize,color=(0.1,0.1,0.1))
    clips = [VideoClip(growBox()).set_duration(5),
                VideoClip(flyInAndGrow()).set_duration(5),
                VideoClip(zoomFromCenter()).set_duration(5)]

    final_clips = concatenate_videoclips(clips)
    final_clips.write_videofile("colortransitiontest.mp4", fps=30)
