#!/usr/bin/env python3
import unittest
from slcan_parser import parse_data

class TestSlcanParser(unittest.TestCase):
    def test_01_part_of_frame(self):
        stored_bytes = "T"
        new_coming_bytes = "9"

        expected_parsed_frames = ""
        expected_updated_stored_bytes = "T9"

        parsed_farmes, updated_stored_bytes = parse_data(stored_bytes, new_coming_bytes)
        self.assertEqual(parsed_farmes, expected_parsed_frames)
        self.assertEqual(updated_stored_bytes, expected_updated_stored_bytes)

    def test_02_single_full_frame_by_once(self):
        stored_bytes = ""
        new_coming_bytes = "T9004034B8233AB442BC5CBC2D\r"

        expected_parsed_frames = "T9004034B8233AB442BC5CBC2D\r"
        expected_updated_stored_bytes = ""

        parsed_farmes, updated_stored_bytes = parse_data(stored_bytes, new_coming_bytes)
        self.assertEqual(parsed_farmes, expected_parsed_frames)
        self.assertEqual(updated_stored_bytes, expected_updated_stored_bytes)

    def test_03_single_full_frame_by_two_parts(self):
        stored_bytes = "T9004034B823"
        new_coming_bytes = "3AB442BC5CBC2D\r"

        expected_parsed_frames = "T9004034B8233AB442BC5CBC2D\r"
        expected_updated_stored_bytes = ""

        parsed_farmes, updated_stored_bytes = parse_data(stored_bytes, new_coming_bytes)
        self.assertEqual(parsed_farmes, expected_parsed_frames)
        self.assertEqual(updated_stored_bytes, expected_updated_stored_bytes)

    def test_04_real_case_part_1(self):
        stored_bytes = ""
        new_coming_bytes = "9A700000000008E\rT9004034A8F37DB142C95CC92E\rT9004034A8ED2DAB42C95CC932\rT9004034A8"

        expected_parsed_frames = "T9004034A8F37DB142C95CC92E\rT9004034A8ED2DAB42C95CC932\r"
        expected_updated_stored_bytes = "T9004034A8"

        parsed_farmes, updated_stored_bytes = parse_data(stored_bytes, new_coming_bytes)
        self.assertEqual(parsed_farmes, expected_parsed_frames)
        self.assertEqual(updated_stored_bytes, expected_updated_stored_bytes)

    def test_05_real_case_part_2_one_frame_is_short(self):
        stored_bytes = "T9004034A8"
        new_coming_bytes = "477900000000008F\rT9004034A80B96A442C95CC92F\rT9004034A65CC95CC95C4F\rT9004034A"

        expected_parsed_frames = "T9004034A8477900000000008F\rT9004034A80B96A442C95CC92F\rT9004034A65CC95CC95C4F\r"
        expected_updated_stored_bytes = "T9004034A"

        parsed_farmes, updated_stored_bytes = parse_data(stored_bytes, new_coming_bytes)
        self.assertEqual(parsed_farmes, expected_parsed_frames)
        self.assertEqual(updated_stored_bytes, expected_updated_stored_bytes)

    def test_06_check_string_index_out_of_range(self):
        stored_bytes = "T980155"
        new_coming_bytes = "32812000000000100C3\rT9004034A839CC000000000095\rT9004034A84A64A742CC5CCC35"

        expected_parsed_frames = "T98015532812000000000100C3\rT9004034A839CC000000000095\r"
        expected_updated_stored_bytes = "T9004034A84A64A742CC5CCC35"

        parsed_farmes, updated_stored_bytes = parse_data(stored_bytes, new_coming_bytes)
        self.assertEqual(parsed_farmes, expected_parsed_frames)
        self.assertEqual(updated_stored_bytes, expected_updated_stored_bytes)

if __name__ == "__main__":
    unittest.main()