import struct

from codenarrative.domain.keypress import Keypress, Key
from codenarrative.domain.scene import Profile
from codenarrative.domain.sound import SoundContext, WavFormat, KeySoundPointer
from typing import BinaryIO

from codenarrative.domain.storage import Location

INPUT_WAV_FILENAME = "sounds/typing_audio.wav"
MAPPING_FILENAME = "sounds/typing_audio.csv"

OUTPUT_WAV_FILENAME_NO_EXTENSION = "audio"


def create_context(location: Location, profile: Profile) -> SoundContext:
    input_wav_file = open(INPUT_WAV_FILENAME, "rb")
    wav_format = check_format(input_wav_file)
    output_wav_filename = location.file(OUTPUT_WAV_FILENAME_NO_EXTENSION, "wav")
    output_wav_file = create_output_file(output_wav_filename, wav_format)
    key_sound_pointers = read_keys_mapping(wav_format, profile.fps)
    context = SoundContext(
        profile.fps, input_wav_file, wav_format, output_wav_file, key_sound_pointers
    )
    return context


def create_output_file(filename: str, wav_format: WavFormat) -> BinaryIO:
    file = open(filename, "wb")
    file.write(b"RIFF")
    file.write(b"\x00\x00\x00\x00")  # size
    file.write(b"WAVEfmt ")

    # 4 bytes fmt chunk size 16 bytes
    file.write(struct.pack("<I", 16))

    # 2 bytes pcm 1
    file.write(struct.pack("<H", 1))

    # 2 bytes
    file.write(struct.pack("<H", wav_format.channels))

    # 4 bytes
    file.write(struct.pack("<I", wav_format.sample_rate))

    # 4 bytes
    file.write(
        struct.pack(
            "<I",
            int(
                wav_format.sample_rate
                * wav_format.bit_per_sample
                * wav_format.channels
                / 8
            ),
        )
    )

    # 2 bytes
    file.write(
        struct.pack("<H", int(wav_format.channels * wav_format.bit_per_sample / 8))
    )

    # 2 bytes
    file.write(struct.pack("<H", wav_format.bit_per_sample))
    file.write(b"data")
    # 4 bytes data chunk size
    file.write(b"\x00\x00\x00\x00")
    return file


def release_files(context: SoundContext):
    # jump to size placeholder
    context.output_wav_file.seek(4)
    context.output_wav_file.write(struct.pack("<I", context.data_size + 16))
    # jump to data chunk size placeholder
    context.output_wav_file.seek(40)
    context.output_wav_file.write(struct.pack("<I", context.data_size))
    context.input_wav_file.close()
    context.output_wav_file.close()


def check_format(input_wav: BinaryIO) -> WavFormat:
    format_expect(input_wav.read(4), b"RIFF")
    # skip 8 bytes (size) from the current position (__whence=1)
    input_wav.seek(4, 1)
    format_expect(input_wav.read(7), b"WAVEfmt ")

    # skip 4 bytes (fmt chunk size) from the current position (__whence=1)
    input_wav.seek(4, 1)
    format_expect(input_wav.read(2), b"\x01\x00")  # 1 PCM (non compressed)

    channels = struct.unpack("<H", input_wav.read(2))[0]
    sample_rate = struct.unpack("<I", input_wav.read(4))[0]

    # skip 4 bytes (size) from the current position (__whence=1)
    input_wav.seek(4 + 2, 1)
    bit_per_sample = struct.unpack("<H", input_wav.read(2))[0]
    format_expect(input_wav.read(4), b"data")
    data_chunk_len = struct.unpack("<I", input_wav.read(4))[0]

    sample_size = int(bit_per_sample / 8)
    unpack_format = ""
    if sample_size == 1:
        unpack_format = "B"  # unsigned
    elif sample_size == 2:
        unpack_format = "h"  # signed
    else:
        raise AssertionError(f"unsupported sample size {sample_size}, supported: 1, 2")
    return WavFormat(
        channels,
        sample_rate,
        bit_per_sample,
        data_chunk_len,
        sample_size,
        unpack_format,
    )


def format_expect(actual, expected):
    if actual != expected:
        raise AssertionError(
            f"unsupported file format: piece: expected '{expected}', actual '{actual}'"
        )


def read_keys_mapping(wav_format: WavFormat, fps: int) -> list[KeySoundPointer]:
    with open(MAPPING_FILENAME, "r") as file:
        return list(
            map(
                lambda l: mapping_line_to_pointer(wav_format, fps, l),
                filter(lambda l: not l.startswith("#"), file.readlines()),
            )
        )


def mapping_line_to_pointer(
    wav_format: WavFormat, fps: int, line: str
) -> KeySoundPointer:
    pointer_data = line.split(",", 3)
    begin = int(pointer_data[0].strip())
    peak_at = int(pointer_data[1].strip())
    end = int(pointer_data[2].strip())
    all_samples = int((end - begin) / wav_format.channels / wav_format.sample_size)
    peak_sample = int((peak_at - begin) / wav_format.channels / wav_format.sample_size)
    frames = max(int(fps * all_samples / wav_format.sample_rate), 1)
    peak_frame = max(int(fps * peak_sample / wav_format.sample_rate), 1)
    return KeySoundPointer(begin, peak_at, end, frames, peak_frame)


def get_sound_pointer(context: SoundContext, keypress: Keypress) -> KeySoundPointer:
    pointers_len = len(context.key_sound_pointers)
    key_number = (
        keypress.key.value if keypress.key != Key.OTHER else ord(keypress.char.lower())
    )
    pos = key_number % pointers_len
    return context.key_sound_pointers[pos]


def append_sound_sample(
    context: SoundContext, pointer: KeySoundPointer, current_frame: int
):
    silence_samples_number = frames_to_samples(
        context, current_frame - context.current_frame
    )
    if silence_samples_number > 0:
        silence_sample_buf = silence_sample(context)
        for i in range(silence_samples_number):
            context.output_wav_file.write(silence_sample_buf)
            context.data_size = context.data_size + len(silence_sample_buf)
    bytes_left = pointer.end_pos - pointer.begin_pos
    context.input_wav_file.seek(pointer.begin_pos)
    while bytes_left > 0:
        buf_size = min(bytes_left, 1024)
        context.output_wav_file.write(context.input_wav_file.read(buf_size))
        context.data_size = context.data_size + buf_size
        bytes_left = bytes_left - buf_size
    context.current_frame = context.current_frame + pointer.frames


def silence_sample(context: SoundContext) -> bytes:
    wav_format = context.wav_format
    if wav_format.sample_size == 1:
        return struct.pack(wav_format.unpack_format, 127) * wav_format.channels
    else:
        return struct.pack(wav_format.unpack_format, 0) * wav_format.channels


def frames_to_samples(context: SoundContext, frames: int) -> int:
    return int(context.wav_format.sample_rate * frames / context.fps)


# https://en.wikipedia.org/wiki/WAV
# https://de.wikipedia.org/wiki/RIFF_WAVE
# https://docs.fileformat.com/audio/wav/
# https://www.joenord.com/audio-wav-file-format/
# https://stackoverflow.com/questions/11779490/how-to-add-a-new-audio-not-mixing-into-a-video-using-ffmpeg
# https://superuser.com/questions/1436830/how-to-convert-raw-pcm-data-to-a-valid-wav-file-with-ffmpeg
# ffmpeg -f f32le -channels 2 -i pipe:0 -f wav file-out.wav
