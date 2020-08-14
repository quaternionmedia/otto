from moviepy.video.compositing.concatenate import concatenate_videoclips
from moviepy.editor import VideoFileClip, AudioFileClip
from moviepy.video.compositing.CompositeVideoClip import CompositeVideoClip
from otto import Otto, templates
from otto.getdata import timestr, download
from otto.kburns import kburns

def renderEdl(edl, media, audio=None, filename='render.mp4', moviesize=(1920,1080), logger='bar'):
    clips = []
    duration = 0
    media = [ download(m) for m in media ]
    for clip in edl:
        print('making clip', clip, type(clip))
        duration += clip['duration']
        if clip['type'] == 'template':
            tmp = getattr(templates, clip['name'])
            print('making template', tmp )
            clips.append(
                tmp(**clip['data'], duration=clip['duration'], clipsize=moviesize)
            )
        elif clip['type'] == 'video':
            clips.append(
                VideoFileClip(clip['name'])
                .subclip(clip['inpoint'])
                .set_duration(clip['duration'])
            )
    print('made clips', clips)
    video = concatenate_videoclips(clips).resize(moviesize)
    print('made video', video, duration)
    kburns(media[:int(1 + duration//5)], moviesize=moviesize, filename=f'{filename}_kbout.mp4')
    slides = (VideoFileClip(f'{filename}_kbout.mp4')
            .set_duration(duration)
            .crossfadein(1)
            .crossfadeout(1)
    )
    video = CompositeVideoClip([slides, video])
    if audio:
        video = video.set_audio(AudioFileClip(audio))
    video = video.set_duration(duration).crossfadeout(1).audio_fadeout(1)
    video.write_videofile(filename, fps=30, logger=logger, threads=8)

def renderMultitrack(edl, audio=None, filename='render.mp4', moviesize=(1920,1080), logger='bar'):
    clips = []
    for clip in edl:
        print('making clip', clip, type(clip))
        if clip['type'] == 'template':
            tmp = getattr(templates, clip['name'])
            print('making template', tmp )
            clips.append(
                tmp(**clip['data'], duration=clip['duration'], clipsize=moviesize).set_start(clip['start'])
            )
        elif clip['type'] == 'video':
            c = (
                VideoFileClip(clip['name'], target_resolution=(moviesize[1], moviesize[0]))
                .subclip(clip.get('inpoint', 0))
                .crossfadein(1)
            )
            if clip.get('duration'):
                c = c.set_duration(clip['duration'])
            clips.append(c.crossfadeout(1))
    print('made clips', clips)
    video = CompositeVideoClip(clips)
    print('made video', video)
    if audio:
        video = video.set_audio(AudioFileClip(audio))
    video = video.crossfadeout(1).audio_fadeout(1)
    video.write_videofile(filename, fps=30, logger=logger, threads=8)

def renderForm(form, filename='render.mp4', logger='bar'):
    v = Otto(form)
    v.render().write_videofile(filename=filename, fps=30, logger=logger)
