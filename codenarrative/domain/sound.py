from typing import BinaryIO


class WavFormat:
    def __init__(
        self,
        channels: int,
        sample_rate: int,
        bit_per_sample: int,
        data_chunk_len: int,
        sample_size: int,
        unpack_format: str,
    ):
        self.channels = channels
        self.sample_rate = sample_rate
        self.bit_per_sample = bit_per_sample
        self.data_chunk_len = data_chunk_len
        self.sample_size = sample_size
        self.unpack_format = unpack_format


class KeySoundPointer:
    def __init__(
        self,
        begin_pos: int,
        peak_pos: int,
        end_pos: int,
        frames: int,
        peak_frame: int,
        samples: int,
    ):
        self.begin_pos = begin_pos
        self.peak_pos = peak_pos
        self.end_pos = end_pos
        self.frames = frames
        self.peak_frame = peak_frame
        self.samples = samples


class SoundContext:
    def __init__(
        self,
        fps: int,
        input_wav_file: BinaryIO,
        wav_format: WavFormat,
        output_wav_file: BinaryIO,
        key_sound_pointers: list[KeySoundPointer],
    ):
        self.current_frame = 0
        self.current_sample = 0
        self.data_size = 0
        self.fps = fps
        self.input_wav_file = input_wav_file
        self.wav_format = wav_format
        self.output_wav_file = output_wav_file
        self.key_sound_pointers = key_sound_pointers
