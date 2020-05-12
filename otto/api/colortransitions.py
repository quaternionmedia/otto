import gizeh
from moviepy.editor import VideoClip, CompositeVideoClip, ColorClip

def growBox(duration=5, size=(800,600)):
    surface = gizeh.Surface(size[0],size[1],bg_color=(0,0,0,0))
    def gb(t):
        x = size[0]*t*2
        rect = gizeh.rectangle(lx=x,ly=size[1],xy=(0,size[1]/2),fill=(0,0,.5,.4))
        rect.draw(surface)

        return surface.get_npimage(transparent=True)
    return gb

def flyInAndGrow(duration=5, size=(1920,1080)):
    surface = gizeh.Surface(size[0],size[1],bg_color=(0, 0, 0, 0))
    def fiag(t):
        w = size[0]*0.1
        h = size[1]*0.8
        x = size[0]/2
        y = -size[1]/2
        if (t < 0.5):
            y = -h/2 + t*h
        if (t > 0.5 and t < duration):
            y = h/2
            w = size[0]*(t*0.8/duration)
        rect = gizeh.rectangle(lx=w,ly=h,xy=(x,y),fill=(0,0,.5,.4))
        rect.draw(surface)

        return surface.get_npimage()
    return fiag

# clip = VideoClip(growBox())
#
# final_clip = CompositeVideoClip([clip])
# final_clip.write_videofile("growbox.mp4", fps=30)
