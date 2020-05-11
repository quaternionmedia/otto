import gizeh
from moviepy.editor import VideoClip, CompositeVideoClip, ColorClip

duration = 5
w,h = 800, 600

def growBox(t):
    surface = gizeh.Surface(w,h,bg_color=(0, 1, 0, 0.2))
    x = w*t*2
    rect = gizeh.rectangle(lx=x,ly=600,xy=(0,h/2),fill=(0,0,1))
    rect.draw(surface)
    return surface.get_npimage()

clip = VideoClip(growBox, duration=5)

final_clip = CompositeVideoClip([clip])
final_clip.write_videofile("growbox.mp4", fps=30)
