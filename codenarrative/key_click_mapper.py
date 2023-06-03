import struct
from typing import BinaryIO, TextIO

from codenarrative.domain.sound import WavFormat
from codenarrative.service.sound_service import check_format

INPUT_WAV_FILENAME = "sounds/typing_audio.wav"
OUTPUT_MAPPING_FILENAME = "sounds/typing_audio.csv"


def main():
    with open(INPUT_WAV_FILENAME, "rb") as input_wav:
        wav_format = check_format(input_wav)
        with open(OUTPUT_MAPPING_FILENAME, "w") as output_csv:
            output_csv.write(
                f"# channels: {wav_format.channels}, sample rate: {wav_format.sample_rate}, bits per sample: {wav_format.bit_per_sample}\n"
            )
            output_csv.write(f"# start_pos, max_volume_pos, end_pos\n")
            data_pos = input_wav.tell()
            low, high = find_local_extremes(input_wav, wav_format)
            input_wav.seek(data_pos)  # jump to beginning of data
            print_impulses(input_wav, output_csv, wav_format, low, high)


def find_local_extremes(input_wav: BinaryIO, wav_format: WavFormat) -> tuple[int, int]:
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
    input_wav: BinaryIO, output_csv: TextIO, wav_format: WavFormat, low: int, high: int
):
    shortest_key_press_ms = 100
    shortest_key_press_samples = int(
        wav_format.sample_rate * shortest_key_press_ms / 1000
    )
    shortest_key_press_bytes = (
        shortest_key_press_samples * wav_format.sample_size * wav_format.channels
    )
    state = 0  # 0 - seek for begin, 1 - seek for end
    pos0 = 0
    samples_counter = 0
    max_volume = 0
    max_volume_pos = 0
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
            max_volume = volume
            max_volume_pos = pos

        area_len = pos - pos0

        if state == 1:
            if volume > max_volume:
                max_volume = volume
                max_volume_pos = pos

            if area_len >= shortest_key_press_bytes and abs(volume - low) <= low / 2:
                state = 0
                # consider as a good click area if max_volume_pos is somewhere in the middle
                max_volume_relative_pos = max_volume_pos - pos0
                max_volume_ratio_pos = max_volume_relative_pos / area_len
                # output_csv.write(
                #     f"#{pos0},{max_volume_pos},{pos},{max_volume_ratio_pos}\n"
                # )
                if area_len > 0 and 0.3 <= max_volume_ratio_pos <= 0.8:
                    output_csv.write(f"{pos0},{max_volume_pos},{pos}\n")


if __name__ == "__main__":
    main()
