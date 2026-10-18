"""The output is the size asked for, and media fits inside it.

The composite used to take its size from whatever clip came first, images
were drawn at their own pixel size, and every clip without a position sat in
the top left corner.
"""

import subprocess

import pytest

from helpers import BLACK_MP4, close_to, color_clip, ffmpeg, pixel
from otto.exceptions import EdlException
from otto.models import Clip, Edl
from otto.render import generateEdl

FRAME = (64, 36)
T = 1.5  # sampled away from any fade
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)


def render(*clips, moviesize=FRAME):
    return generateEdl(Edl(clips=list(clips)), moviesize=moviesize)


def video(path, **attrs):
    return Clip(type='video', name=path, duration=2, fadeIn=0, fadeOut=0, **attrs)


def image(path, **attrs):
    return Clip(type='image', name=path, duration=3, fadeIn=0, fadeOut=0, **attrs)


def background(color='#00ff00'):
    return color_clip(color, duration=3, fadeIn=0, fadeOut=0)


# --- the frame --------------------------------------------------------------


@pytest.mark.parametrize('first', ['small template', 'large video', 'image'])
def test_the_output_is_the_requested_size_whatever_comes_first(first, media):
    clips = {
        'small template': color_clip(clipsize=(10, 10)),
        'large video': video(BLACK_MP4),
        'image': image(media['wide_png']),
    }
    made = render(clips[first], color_clip(), moviesize=(48, 30))
    assert tuple(made.size) == (48, 30)


@pytest.mark.parametrize('moviesize', [(0, 36), (64, -1), (64,), 'big', None])
def test_a_frame_with_no_area_is_refused(moviesize):
    with pytest.raises(EdlException, match='moviesize'):
        render(color_clip(), moviesize=moviesize)


# --- video ------------------------------------------------------------------


def test_a_video_of_the_frames_proportions_fills_it(media):
    layer = render(video(media['wide'])).clips[0]
    assert tuple(layer.size) == FRAME


def test_a_tall_video_is_fitted_and_centred(media):
    made = render(video(media['tall']))

    assert tuple(made.clips[0].size) == (20, 36)  # 90x160 scaled by 36/160
    assert close_to(pixel(made, T, 32, 18), BLUE, 12)
    assert pixel(made, T, 5, 18) == BLACK, 'pillarbox expected left of centre'
    assert pixel(made, T, 58, 18) == BLACK, 'pillarbox expected right of centre'


def test_a_wide_video_is_letterboxed_rather_than_cropped(media):
    made = render(video(media['wide']), moviesize=(40, 40))

    assert tuple(made.clips[0].size) == (40, 22)
    assert pixel(made, T, 20, 2) == BLACK
    assert close_to(pixel(made, T, 20, 20), RED, 12)
    assert pixel(made, T, 20, 37) == BLACK


def test_a_video_fits_its_clipsize_when_it_has_one(media):
    made = render(video(media['wide'], clipsize=(32, 18)))
    assert tuple(made.clips[0].size) == (32, 18)


def rotated_copy(source, target):
    """`source`, marked as turned a quarter, the way this ffmpeg marks it.

    ffmpeg 6 and later write a display matrix (`-display_rotation`); earlier
    ones write a `rotate` tag, and know no `-display_rotation`.
    """
    try:
        ffmpeg('-display_rotation', '90', '-i', source, '-c', 'copy', target)
    except subprocess.CalledProcessError:
        ffmpeg('-i', source, '-c', 'copy', '-metadata:s:v:0', 'rotate=90', target)


def test_a_rotated_video_is_fitted_upright(media, tmp_path):
    rotated = str(tmp_path / 'rotated.mp4')
    rotated_copy(media['wide'], rotated)

    made = render(video(rotated))

    # Stored 160x90, displayed 90x160: fitted as the latter.
    assert tuple(made.clips[0].size) == (20, 36)
    assert close_to(pixel(made, T, 32, 18), RED, 12)
    assert pixel(made, T, 5, 18) == BLACK


def test_a_file_with_no_picture_is_refused(media):
    with pytest.raises(EdlException, match=r"clip 1 .*no video stream"):
        render(video(media['tone']))


# --- images -----------------------------------------------------------------


def test_an_image_is_scaled_down_to_fit(media):
    made = render(image(media['wide_png']))

    assert tuple(made.clips[0].size) == (64, 32)  # 200x100 scaled by 64/200
    assert pixel(made, T, 32, 0) == BLACK
    assert pixel(made, T, 32, 18) == BLUE


def test_a_small_image_is_scaled_up_to_fit(media):
    made = render(image(media['grey_png']))

    assert tuple(made.clips[0].size) == (36, 36)
    assert pixel(made, T, 32, 18) == (200, 200, 200), 'greyscale drawn as grey'
    assert pixel(made, T, 5, 18) == BLACK


def test_an_images_transparency_shows_the_layer_beneath(media):
    made = render(background(), image(media['tall_png']))

    # 50x100 scaled to 18x36 and centred: the top half is opaque red, the
    # bottom half transparent.
    assert pixel(made, T, 32, 9) == RED
    assert pixel(made, T, 32, 27) == GREEN
    assert pixel(made, T, 5, 18) == GREEN


def test_a_position_overrides_the_centring(media):
    made = render(image(media['grey_png'], position=(0, 0)))

    assert pixel(made, T, 2, 18) == (200, 200, 200)
    assert pixel(made, T, 60, 18) == BLACK


def test_resize_scales_the_fitted_image(media):
    made = render(image(media['grey_png'], resize=0.5))

    assert tuple(made.clips[0].size) == (18, 18)
    assert pixel(made, T, 32, 18) == (200, 200, 200)
    assert pixel(made, T, 32, 5) == BLACK


def test_a_file_that_is_not_an_image_is_refused(media):
    with pytest.raises(EdlException, match=r"clip 1 .*could not be opened"):
        render(image(media['tone']))


def test_ffmpeg_is_available_for_these_tests():
    """The synthetic media above depends on it; make a failure obvious."""
    import imageio_ffmpeg

    subprocess.run(
        [imageio_ffmpeg.get_ffmpeg_exe(), '-version'], check=True, capture_output=True
    )
