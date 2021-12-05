from moviepy.video.compositing.concatenate import concatenate_videoclips
from moviepy.editor import VideoFileClip, AudioFileClip, ImageClip
from moviepy.video.compositing.CompositeVideoClip import CompositeVideoClip
from moviepy.audio.AudioClip import CompositeAudioClip
from otto import Otto, templates
from otto.getdata import timestr, download
from otto.kburns import kburns
from otto.models import Edl
from typing import List

def generateEdl(edl: Edl, moviesize=(1920,1080), audio=None, **kwargs):
    """Generates a moviepy CompositeVideoClip from an Edl"""
    clips = []
    for clip in edl.clips:
        print('making clip', clip, type(clip))
        if clip.type == 'template':
            tmp = getattr(templates, clip.name)
            print('making template', tmp )
            c = tmp(**clip.data.dict(), clipsize=getattr(clip, 'clipsize', moviesize), duration=clip.duration)
            # c = tmp(**clip.data.dict(), clipsize=moviesize, duration=clip.duration)
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
        # if clip.outpoint:
        #     c = c.set_duration(clip.outpoint - getattr(clip, 'inpoint', 0))
        if clip.duration:
            c = c.set_duration(clip.duration)
        if clip.position:
            c = c.set_position(clip.position, relative=clip.relative)
        if clip.start:
            c = c.set_start(clip.start)
        if clip.fadeIn:
            c = c.crossfadein(clip.fadeIn)
        if clip.fadeOut:
            c = c.crossfadeout(clip.fadeOut)
        # if clip.fxs:
        #     render fx
        clips.append(c)
    print('made clips', clips)
    video = CompositeVideoClip(clips)
    print('made video', video)
    if audio:
        video = video.set_audio(audio)
    if edl.duration:
        video = video.set_duration(edl.duration)
    # video = video.crossfadeout(1).audio_fadeout(1)
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
    """Render v2: renders a multitrack Edl as seperate layers"""
    video = generateEdl(edl, moviesize, **kwargs)
    video.write_videofile(filename, 
        fps=30.0,
        logger=logger,
        threads=8,
        audio_fps=48000, audio_codec='aac', audio_bitrate=audio_bitrate,
        codec=codec, bitrate=bitrate,
        ffmpeg_params=ffmpeg_params)
