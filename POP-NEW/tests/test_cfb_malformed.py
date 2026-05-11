import struct
import unittest

from pop_core.cfb import CfbFile, HEADER_SIZE, SIGNATURE


def _valid_header(sector_shift: int = 9, mini_shift: int = 6, first_dir: int = 1) -> bytes:
    header = bytearray(HEADER_SIZE)
    header[:8] = SIGNATURE
    struct.pack_into("<H", header, 30, sector_shift)
    struct.pack_into("<H", header, 32, mini_shift)
    struct.pack_into("<I", header, 48, first_dir)
    return bytes(header)


class CfbMalformedTests(unittest.TestCase):
    def test_rejects_truncated_header(self):
        with self.assertRaisesRegex(ValueError, "shorter than"):
            CfbFile(b"\x00" * 100)

    def test_rejects_bad_signature(self):
        data = bytearray(_valid_header())
        data[:8] = b"NOTACFB!"
        with self.assertRaisesRegex(ValueError, "Not an OLE"):
            CfbFile(bytes(data))

    def test_rejects_unreasonable_sector_shift(self):
        with self.assertRaisesRegex(ValueError, "sector shift"):
            CfbFile(_valid_header(sector_shift=24))

    def test_rejects_unreasonable_mini_sector_shift(self):
        with self.assertRaisesRegex(ValueError, "mini sector shift"):
            CfbFile(_valid_header(mini_shift=20))

    def test_rejects_sector_pointing_past_eof(self):
        header = _valid_header(first_dir=0x1000)
        data = header + bytes(512)
        with self.assertRaisesRegex(ValueError, "extends past end of file"):
            CfbFile(data)

    def test_rejects_directory_entry_with_oversized_name(self):
        sector_size = 512
        header = bytearray(_valid_header(first_dir=0))
        struct.pack_into("<I", header, 76, 1)
        fat_sector = bytearray(sector_size)
        struct.pack_into("<I", fat_sector, 0, 0xFFFFFFFE)
        directory_sector = bytearray(sector_size)
        struct.pack_into("<H", directory_sector, 64, 200)
        directory_sector[66] = 2
        data = bytes(header) + bytes(directory_sector) + bytes(fat_sector)
        with self.assertRaisesRegex(ValueError, "exceeds maximum"):
            CfbFile(data)


if __name__ == "__main__":
    unittest.main()
