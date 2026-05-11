from dataclasses import dataclass
import struct


END_OF_CHAIN = 0xFFFFFFFE
FREE_SECTOR = 0xFFFFFFFF
MAXREGSECT = 0xFFFFFFFA
SIGNATURE = b"\xd0\xcf\x11\xe0\xa1\xb1\x1a\xe1"
HEADER_SIZE = 512
MIN_SECTOR_SHIFT = 7
MAX_SECTOR_SHIFT = 16
MIN_MINI_SECTOR_SHIFT = 6
MAX_MINI_SECTOR_SHIFT = 12
MAX_NAME_BYTES = 64
MAX_STREAM_BYTES = 64 * 1024 * 1024


@dataclass(frozen=True)
class CfbDirectoryEntry:
    name: str
    object_type: int
    start_sector: int
    stream_size: int


class CfbFile:
    def __init__(self, data: bytes):
        if len(data) < HEADER_SIZE:
            raise ValueError("OLE Compound Document is shorter than its 512-byte header")
        if data[:8] != SIGNATURE:
            raise ValueError("Not an OLE Compound Document")
        sector_shift = struct.unpack_from("<H", data, 30)[0]
        mini_shift = struct.unpack_from("<H", data, 32)[0]
        if not MIN_SECTOR_SHIFT <= sector_shift <= MAX_SECTOR_SHIFT:
            raise ValueError(f"sector shift {sector_shift} is outside the allowed range")
        if not MIN_MINI_SECTOR_SHIFT <= mini_shift <= MAX_MINI_SECTOR_SHIFT:
            raise ValueError(f"mini sector shift {mini_shift} is outside the allowed range")
        self.data = data
        self.sector_size = 1 << sector_shift
        self.mini_sector_size = 1 << mini_shift
        self.first_directory_sector = struct.unpack_from("<I", data, 48)[0]
        self.mini_stream_cutoff = struct.unpack_from("<I", data, 56)[0]
        self.first_mini_fat_sector = struct.unpack_from("<I", data, 60)[0]
        self.mini_fat_sector_count = struct.unpack_from("<I", data, 64)[0]
        self.difat_sector_start = struct.unpack_from("<I", data, 68)[0]
        self.difat_sector_count = struct.unpack_from("<I", data, 72)[0]
        self.fat_sector_ids = self._read_fat_sector_ids()
        self.fat = self._read_fat()
        self.directory_entries = self._read_directory_entries()
        self.root = next((entry for entry in self.directory_entries if entry.object_type == 5), None)
        self.mini_fat = self._read_mini_fat()
        self.mini_stream = self._read_regular_stream(self.root.start_sector, self.root.stream_size) if self.root else b""

    @classmethod
    def from_path(cls, path):
        return cls(path.read_bytes())

    def stream_names(self) -> list[str]:
        return [entry.name for entry in self.directory_entries if entry.object_type == 2]

    def read_stream(self, name: str) -> bytes:
        entry = self._find_stream(name)
        if entry.stream_size < self.mini_stream_cutoff:
            return self._read_mini_stream(entry.start_sector, entry.stream_size)
        return self._read_regular_stream(entry.start_sector, entry.stream_size)

    def _find_stream(self, name: str) -> CfbDirectoryEntry:
        for entry in self.directory_entries:
            if entry.object_type == 2 and entry.name.lower() == name.lower():
                return entry
        raise KeyError(name)

    def _sector_offset(self, sector_id: int) -> int:
        return (sector_id + 1) * self.sector_size

    def _sector(self, sector_id: int) -> bytes:
        offset = self._sector_offset(sector_id)
        if offset < 0 or offset + self.sector_size > len(self.data):
            raise ValueError(f"sector {sector_id} extends past end of file")
        return self.data[offset:offset + self.sector_size]

    def _read_fat_sector_ids(self) -> list[int]:
        sector_ids = [
            value for value in struct.unpack_from("<109I", self.data, 76)
            if value not in (FREE_SECTOR, END_OF_CHAIN)
        ]
        next_difat = self.difat_sector_start
        for _ in range(self.difat_sector_count):
            if next_difat in (FREE_SECTOR, END_OF_CHAIN):
                break
            sector = self._sector(next_difat)
            values = struct.unpack_from(f"<{self.sector_size // 4}I", sector, 0)
            sector_ids.extend(value for value in values[:-1] if value not in (FREE_SECTOR, END_OF_CHAIN))
            next_difat = values[-1]
        return sector_ids

    def _read_fat(self) -> list[int]:
        entries = []
        for sector_id in self.fat_sector_ids:
            sector = self._sector(sector_id)
            entries.extend(struct.unpack_from(f"<{self.sector_size // 4}I", sector, 0))
        return entries

    def _sector_chain(self, start_sector: int) -> list[int]:
        chain = []
        sector_id = start_sector
        seen = set()
        while sector_id not in (FREE_SECTOR, END_OF_CHAIN) and sector_id < MAXREGSECT and sector_id not in seen:
            seen.add(sector_id)
            chain.append(sector_id)
            if sector_id >= len(self.fat):
                break
            sector_id = self.fat[sector_id]
        return chain

    def _read_regular_stream(self, start_sector: int, size: int) -> bytes:
        if start_sector in (FREE_SECTOR, END_OF_CHAIN):
            return b""
        if size > MAX_STREAM_BYTES:
            raise ValueError(f"stream size {size} exceeds {MAX_STREAM_BYTES} byte cap")
        data = b"".join(self._sector(sector_id) for sector_id in self._sector_chain(start_sector))
        return data[:size]

    def _read_directory_entries(self) -> list[CfbDirectoryEntry]:
        directory = self._read_regular_stream(self.first_directory_sector, len(self.data))
        entries = []
        for offset in range(0, len(directory), 128):
            chunk = directory[offset:offset + 128]
            if len(chunk) < 128:
                break
            name_size = struct.unpack_from("<H", chunk, 64)[0]
            object_type = chunk[66]
            if object_type == 0 or name_size < 2:
                continue
            if name_size > MAX_NAME_BYTES:
                raise ValueError(f"directory entry name field of {name_size} bytes exceeds maximum {MAX_NAME_BYTES}")
            name = chunk[:name_size - 2].decode("utf-16le", errors="ignore")
            start_sector = struct.unpack_from("<I", chunk, 116)[0]
            stream_size = struct.unpack_from("<Q", chunk, 120)[0]
            entries.append(CfbDirectoryEntry(name, object_type, start_sector, stream_size))
        return entries

    def _read_mini_fat(self) -> list[int]:
        if self.first_mini_fat_sector in (FREE_SECTOR, END_OF_CHAIN) or self.mini_fat_sector_count == 0:
            return []
        data = b"".join(self._sector(sector_id) for sector_id in self._sector_chain(self.first_mini_fat_sector))
        count = len(data) // 4
        return list(struct.unpack_from(f"<{count}I", data, 0))

    def _mini_sector_chain(self, start_sector: int) -> list[int]:
        chain = []
        sector_id = start_sector
        seen = set()
        while sector_id not in (FREE_SECTOR, END_OF_CHAIN) and sector_id < MAXREGSECT and sector_id not in seen:
            seen.add(sector_id)
            chain.append(sector_id)
            if sector_id >= len(self.mini_fat):
                break
            sector_id = self.mini_fat[sector_id]
        return chain

    def _read_mini_stream(self, start_sector: int, size: int) -> bytes:
        if size > MAX_STREAM_BYTES:
            raise ValueError(f"mini stream size {size} exceeds {MAX_STREAM_BYTES} byte cap")
        chunks = []
        for sector_id in self._mini_sector_chain(start_sector):
            offset = sector_id * self.mini_sector_size
            if offset < 0 or offset + self.mini_sector_size > len(self.mini_stream):
                raise ValueError(f"mini sector {sector_id} extends past mini stream")
            chunks.append(self.mini_stream[offset:offset + self.mini_sector_size])
        return b"".join(chunks)[:size]
