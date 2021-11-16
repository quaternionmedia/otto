from moviepy.video.compositing.concatenate import concatenate_videoclips
from moviepy.editor import VideoFileClip, AudioFileClip, ImageClip
from moviepy.video.compositing.CompositeVideoClip import CompositeVideoClip
from moviepy.audio.AudioClip import CompositeAudioClip
from otto import Otto, templates
from otto.getdata import timestr, download
from otto.kburns import kburns
from otto.models import Edl
from typing import List

def renderEdl(edl: Edl, media, audio=None, filename='render.mp4', moviesize=(1920,1080), logger='bar'):
    clips = []
    duration = 0
    media = [ download(m) for m in media ]
    for clip in edl.clips:
        print('making clip', clip, type(clip))
        duration += clip.duration
        if clip.type == 'template':
            tmp = getattr(templates, clip.name)
            print('making template', tmp )
            clips.append(
                tmp(**clip.data, duration=clip.duration, clipsize=moviesize)
            )
        elif clip.type == 'video':
            clips.append(
                VideoFileClip(clip.name)
                .subclip(clip.inpoint)
                .set_duration(clip.duration)
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

def generateEdl(edl: Edl, moviesize=(1920,1080), audio=None, duration=None, inpoint=None, **kwargs):
    """Generates a moviepy CompositeVideoClip from an Edl"""
    clips = []
    for clip in edl.clips:
        print('making clip', clip, type(clip))
        if clip.type == 'template':
            tmp = getattr(templates, clip.name)
            print('making template', tmp )
            c = tmp(**clip.data, clipsize=moviesize, duration=clip.duration)
        elif clip.type == 'video':
            clip.name = download(clip.name)
            c = VideoFileClip(clip.name, target_resolution=(moviesize[1], None))
        elif clip.type == 'audio':
            c = CompositeAudioClip([AudioFileClip(clip.name, fps=48000)])
            audio = c.audio_fadein(1).audio_fadeout(1)
        elif clip.type == 'image':
            c = CompositeVideoClip([ImageClip(clip.name)])
        if clip.resize:
            c = c.resize(clip.resize)
        
        if clip.offset:
            if clip.offset < 0:
                c = c.subclip(-clip.offset)
            else:
                c = c.set_start(clip.offset)
        if clip.inpoint:
            c = c.subclip(clip.inpoint)
        if clip.duration:
            c = c.set_duration(clip.duration)
        if clip.position:
            c = c.set_position(tuple(clip.position), relative=clip.relative)
        if clip.start:
            c = c.set_start(clip.start)            
        clips.append(c.crossfadein(1).crossfadeout(1))
    print('made clips', clips)
    video = CompositeVideoClip(clips)
    print('made video', video)
    if audio:
        video = video.set_audio(audio)
    if inpoint:
        video = video.subclip(inpoint)
    if duration or edl.duration:
        video = video.set_duration(duration or edl.duration)
    video = video.crossfadeout(1).audio_fadeout(1)
    return video

def renderMultitrack(edl: Edl, 
        audio=None,
        filename='render.mp4',
        moviesize=(1920,1080),
        logger='bar',
        fps=30.0,
        codec='libx264',
        bitrate=None,
        audio_bitrate='320k',
        ffmpeg_params=None,
        **kwargs):
    video = generateEdl(edl, moviesize, **kwargs)
    video.write_videofile(filename, 
        fps=30, 
        logger=logger, 
        threads=8,
        audio_fps=48000, audio_codec='aac', audio_bitrate=audio_bitrate,
        codec=codec, bitrate=bitrate,
        ffmpeg_params=ffmpeg_params)

def renderForm(form, filename='render.mp4', logger='bar'):
    v = Otto(form)
    v.render().write_videofile(filename=filename, fps=fps, logger=logger)
