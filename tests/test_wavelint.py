"""wavelint hook tests."""

import contextlib
import io
import os
import tempfile

from waves import Sound, mono_ttf_gen, stereo_ttf_gen

import pytest

from hooks.wavelint import wavelint


TMP_DIR = tempfile.gettempdir()


@pytest.mark.parametrize(
    "nchannels",
    (1, 2),
    ids=("nchannels=1", "nchannels=2"),
)
@pytest.mark.parametrize(
    "sample_width",
    (2,),
    ids=("sample_width=2",),
)
@pytest.mark.parametrize(
    "frame_rate",
    (22050, 41100),
    ids=("frame_rate=22050", "frame_rate=41100")
)
@pytest.mark.parametrize(
    "max_duration",
    (1, 1.5),
    ids=("max_duration=1", "max_duration=1.5"),
)
@pytest.mark.parametrize(
    "min_duration",
    (0.5,),
    ids=("min_duration=0.5",),
)
@pytest.mark.parametrize(
    "duration",
    (0.5, 1, 1.2),
    ids=("duration=0.5", "duration=1", "duration=1.2"),
)
def test_wavelint(
    nchannels,
    sample_width,
    frame_rate,
    max_duration,
    min_duration,
    duration,
):
    filenames, expected_messages, expected_exitcode = ([], [], 0)
    expected_messages = [
        "Found lower duration (0.5) than allowed (1.2) at file /tmp/wavelint__test_0.wav"
    ]
    for i in range(5):
        filename = os.path.join(TMP_DIR, f"wavelint__test_{i}.wav")
        if os.path.isfile(filename):
            os.remove(filename)
            
        if duration > max_duration:
            expected_messages.append(
                (f"Found greater duration ({float(duration)}) than allowed"
                 f" ({float(max_duration)}) at file {filename}")
            )
        
        if duration < min_duration:
            expected_messages.append(
                (f"Found lower duration ({float(duration)}) than allowed"
                 f" ({float(min_duration)}) at file {filename}")
            )
    
        kwargs = dict(volume=0.5, sample_width=sample_width)
        if frame_rate is not None:
            kwargs["fps"] = frame_rate
        time_to_frame = (
            mono_ttf_gen(frequency=440, **kwargs)
            if nchannels == 1 else
            stereo_ttf_gen(frequencies=(220, 440), **kwargs)
        )
        
        Sound.from_datatimes(
            time_to_frame,
            fps=frame_rate,
        ).with_duration(duration).save(filename)
        filenames.append(filename)
    
    stderr = io.StringIO()
    with contextlib.redirect_stderr(stderr):
        exitcode = wavelint(
            filenames,
            nchannels=nchannels,
            sample_width=sample_width,
            frame_rate=frame_rate,
            max_duration=max_duration,
            min_duration=min_duration,
        )
    
    stderr_content = stderr.getvalue()
    
    for message in stderr_content.splitlines():
        assert message in expected_messages
    
    for filename in filenames:
        os.remove(filename)
    
    