"""A video is probed once for each version of its file, not on every build.

A preview builds the whole Edl again for every frame it shows. Each build ran
ffmpeg on every video before opening it -- twice for a video that is not
turned, since moviepy reports no rotation for it and ffmpeg was asked again
for a display matrix.
"""

import shutil
import subprocess

import pytest

from ffmpeg_samples import ROTATED_7, ROTATED_9
from helpers import rotated_copy
from otto import render
from otto.models import Clip, Edl
from otto.render import generateEdl

FRAME = (64, 36)


def build(*paths):
    clips = [Clip(type='video', name=p, duration=1, fadeIn=0, fadeOut=0) for p in paths]
    return generateEdl(Edl(clips=clips), moviesize=FRAME)


@pytest.fixture
def probes(monkeypatch):
    """What otto asked ffmpeg about, in order: ('infos' or 'rotation', path)."""
    asked = []
    parse_infos = render.ffmpeg_parse_infos
    display_matrix_rotation = render._display_matrix_rotation

    def infos(path, *args, **kwargs):
        asked.append(('infos', path))
        return parse_infos(path, *args, **kwargs)

    def rotation(path):
        asked.append(('rotation', path))
        return display_matrix_rotation(path)

    monkeypatch.setattr(render, 'ffmpeg_parse_infos', infos)
    monkeypatch.setattr(render, '_display_matrix_rotation', rotation)
    render._probe.cache_clear()
    yield asked
    render._probe.cache_clear()


def test_a_second_build_does_not_probe_again(media, probes):
    build(media['wide'])
    assert probes == [('infos', media['wide']), ('rotation', media['wide'])]

    build(media['wide'])
    assert len(probes) == 2, 'the second build asked ffmpeg again'


def test_each_file_is_probed_once_however_often_it_is_used(media, probes):
    build(media['wide'], media['tall'], media['wide'])
    build(media['tall'], media['wide'])

    assert sorted(set(path for _, path in probes)) == sorted(
        [media['wide'], media['tall']]
    )
    assert len(probes) == 4


def test_a_file_that_changes_is_probed_again(media, probes, tmp_path):
    path = str(tmp_path / 'clip.mp4')
    shutil.copy(media['wide'], path)
    assert tuple(build(path).clips[0].size) == (64, 36)

    shutil.copy(media['tall'], path)  # another size, so another version

    assert tuple(build(path).clips[0].size) == (20, 36), 'fitted from a stale probe'
    assert [kind for kind, _ in probes].count('infos') == 2


def test_a_turned_video_is_upright_from_the_cache_too(media, probes, tmp_path):
    rotated = str(tmp_path / 'rotated.mp4')
    rotated_copy(media['wide'], rotated)

    first = build(rotated).clips[0]
    asked = len(probes)
    second = build(rotated).clips[0]

    assert tuple(first.size) == tuple(second.size) == (20, 36)
    assert len(probes) == asked


@pytest.mark.parametrize(
    'description', [ROTATED_7, ROTATED_9], ids=['ffmpeg-7.0', 'ffmpeg-9']
)
def test_a_display_matrix_is_read_in_either_spelling(monkeypatch, description):
    """The installed ffmpeg prints one spelling, so the suite's own files test
    only that one; this reads each, whichever ffmpeg is installed."""

    def described(args, **kwargs):
        return subprocess.CompletedProcess(args, 1, stdout='', stderr=description)

    monkeypatch.setattr(render.subprocess, 'run', described)

    assert abs(render._display_matrix_rotation('turned.mp4')) == 90


def test_how_many_probes_are_kept_is_bounded():
    assert render._probe.cache_info().maxsize == render.PROBE_CACHE_SIZE > 0
