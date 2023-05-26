import struct
from typing import BinaryIO

INPUT_WAV_FILENAME = "sounds/typing_audio.wav"
OUTPUT_MAPPING_FILENAME = "sounds/typing_audio.csv"


class Format:
    def __init__(
        self, channels: int, sample_rate: int, bit_per_sample: int, data_chunk_len: int
    ):
        self.channels = channels
        self.sample_rate = sample_rate
        self.bit_per_sample = bit_per_sample
        self.data_chunk_len = data_chunk_len


def main():
    with open(INPUT_WAV_FILENAME, "rb") as input_wav:
        wav_format = check_format(input_wav)
        with open(OUTPUT_MAPPING_FILENAME, "w") as output_csv:
            output_csv.write(
                f"# channels: {wav_format.channels}, sample rate: {wav_format.sample_rate}, bits per sample: {wav_format.bit_per_sample}"
            )
            sample_size = int(wav_format.bit_per_sample / 8)
            if sample_size == 1:
                unpack_format = "B"  # unsigned
            elif sample_size == 2:
                unpack_format = "h"  # signed
            else:
                raise AssertionError(
                    f"unsupported sample size {sample_size}, supported: 1, 2"
                )

            sample_number = 0
            while all_channels_samples := input_wav.read(
                wav_format.channels * sample_size
            ):
                volume = 0
                for channel_number in range(wav_format.channels):
                    begin_index = channel_number * sample_size
                    sample = all_channels_samples[
                        begin_index : begin_index + sample_size
                    ]
                    volume = volume + struct.unpack(unpack_format, sample)[0]
                sample_number = sample_number + 1
                # print(volume)
                if sample_number % 10 == 0:  # example output
                    print(volume)


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
    return Format(
        channels=struct.unpack("<H", input_wav.read(2))[0],
        sample_rate=struct.unpack("<I", input_wav.read(4))[0],
        bit_per_sample=struct.unpack(
            "<H", skip_and_read(input_wav, skip=4 + 2, read=2)
        )[0],
        data_chunk_len=struct.unpack("<I", input_wav.read(4))[0],
    )


def skip_and_read(input_wav: BinaryIO, skip: int, read: int):
    input_wav.seek(skip, 1)  # skip from the current position
    return input_wav.read(read)


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
