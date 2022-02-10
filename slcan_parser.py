#!/usr/bin/env python3
FRAME_MAX_LENGTH = 27   # size = 8
FRAME_MIN_LENGTH = 11   # size = 0 (theoretical case)
FRAME_SIZE_IDX = 9
FRAME_FIRST_BYTE = 'T'
FRAME_LAST_BYTE = '\r'


def parse_data(storage, new_coming_bytes):
    """
    Brief. This function is manipulate with 3 types of buffer:
    - the storage buffer
    - buffer with with new coming data
    - parsed frame
    By giving the previous storage and the coming bytes,
    it updates the storage and return the parsed frames.
    """
    parsed_frames = ""
    updated_storage = ""

    data = storage + new_coming_bytes
    combined_buffer_size = len(data)

    if combined_buffer_size < FRAME_MIN_LENGTH:
        updated_storage = data
    else:
        # Find all appropriate frames, skip bad frames.
        # Use while instead of for + range() because we need to increment by the different values
        head_idx = 0
        last_parsed_tail_idx = 0
        while head_idx <= combined_buffer_size - FRAME_MIN_LENGTH:
            if data[head_idx] == FRAME_FIRST_BYTE:
                try:
                    payload_size = int(data[head_idx + FRAME_SIZE_IDX])
                except ValueError:
                    head_idx += 1
                    continue
                frame_size = FRAME_MIN_LENGTH + 2 * int(data[head_idx + FRAME_SIZE_IDX])
                if frame_size < combined_buffer_size - head_idx + 1 and data[head_idx + frame_size - 1] == FRAME_LAST_BYTE:
                    parsed_frames += data[head_idx : head_idx + frame_size]
                    head_idx += frame_size
                    last_parsed_tail_idx = head_idx
                    continue
            head_idx += 1

        # put everything else into the storage buffer
        updated_storage = data[last_parsed_tail_idx : combined_buffer_size]

    return parsed_frames, updated_storage
