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

clip = VideoClip(growBox, duration=5)

# clip = VideoClip(growBox())
#
# final_clip = CompositeVideoClip([clip])
# final_clip.write_videofile("growbox.mp4", fps=30)
