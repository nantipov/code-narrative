import struct
from typing import BinaryIO, TextIO

INPUT_WAV_FILENAME = "sounds/typing_audio.wav"
OUTPUT_MAPPING_FILENAME = "sounds/typing_audio.csv"


class Format:
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


def main():
    with open(INPUT_WAV_FILENAME, "rb") as input_wav:
        wav_format = check_format(input_wav)
        with open(OUTPUT_MAPPING_FILENAME, "w") as output_csv:
            output_csv.write(
                f"# channels: {wav_format.channels}, sample rate: {wav_format.sample_rate}, bits per sample: {wav_format.bit_per_sample}\n"
            )
            data_pos = input_wav.tell()
            low, high = find_local_extremes(input_wav, wav_format)
            input_wav.seek(data_pos)  # jump to beginning of data
            print_impulses(input_wav, output_csv, wav_format, low, high)


def find_local_extremes(input_wav: BinaryIO, wav_format: Format) -> tuple[int, int]:
    local_area_ms = 100
    local_area_samples = int(wav_format.sample_rate * local_area_ms / 1000)
    least_extreme = -1
    most_extreme = 0
    local_max_volume = 0
    samples_counter = 0
    while all_channels_sample := input_wav.read(
        wav_format.channels * wav_format.sample_size
    ):
        volume = 0
        for channel_number in range(wav_format.channels):
            begin_index = channel_number * wav_format.sample_size
            sample = all_channels_sample[
                begin_index : begin_index + wav_format.sample_size
            ]
            volume = volume + struct.unpack(wav_format.unpack_format, sample)[0]
        volume = abs(volume)
        samples_counter = samples_counter + 1
        if volume > local_max_volume:
            local_max_volume = volume
        if samples_counter > local_area_samples:
            if least_extreme < 0 or local_max_volume < least_extreme:
                least_extreme = local_max_volume
            if local_max_volume > most_extreme:
                most_extreme = local_max_volume
            local_max_volume = 0
            samples_counter = 0
    return least_extreme, most_extreme


def print_impulses(
    input_wav: BinaryIO, output_csv: TextIO, wav_format: Format, low: int, high: int
):
    shortest_key_press_ms = 100
    shortest_key_press_ms = int(wav_format.sample_rate * shortest_key_press_ms / 1000)
    state = 0  # 0 - seek for begin, 1 - see for end
    pos0 = 0
    samples_counter = 0
    while all_channels_sample := input_wav.read(
        wav_format.channels * wav_format.sample_size
    ):
        volume = 0
        for channel_number in range(wav_format.channels):
            begin_index = channel_number * wav_format.sample_size
            sample = all_channels_sample[
                begin_index : begin_index + wav_format.sample_size
            ]
            volume = volume + struct.unpack(wav_format.unpack_format, sample)[0]
        volume = abs(volume)
        pos = input_wav.tell()
        samples_counter = samples_counter + 1
        if state == 0 and volume > low:
            state = 1
            pos0 = pos
        if state == 1 and volume <= low and pos - pos0 >= shortest_key_press_ms:
            state = 0
            output_csv.write(f"{pos0},{pos}\n")


def check_format(input_wav: BinaryIO) -> Format:
    format_expect(input_wav.read(4), b"RIFF")
    # skip 8 bytes (size) from the current position (__whence=1)
    input_wav.seek(4, 1)
    format_expect(input_wav.read(7), b"WAVEfmt")
    # skip 1 byte (fmt trailing null) from the current position (__whence=1)
    input_wav.seek(1, 1)
    # skip 4 bytes (size) from the current position (__whence=1)
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
    return Format(
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


if __name__ == "__main__":
    main()

# https://en.wikipedia.org/wiki/WAV
# https://de.wikipedia.org/wiki/RIFF_WAVE
# https://docs.fileformat.com/audio/wav/
# https://www.joenord.com/audio-wav-file-format/
