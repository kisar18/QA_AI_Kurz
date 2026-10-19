import struct
import zlib
from pathlib import Path


def create_png_image(filepath: str | Path, width: int = 160, height: int = 90) -> Path:
    """Vytvoří validní PNG obrázek o zadaných rozměrech (šířka x výška) bez externích závislostí."""
    target_path = Path(filepath)
    target_path.parent.mkdir(parents=True, exist_ok=True)

    # PNG hlavička (magic bytes)
    png_header = b"\x89PNG\r\n\x1a\n"

    # IHDR chunk
    # Bit depth 8, Color type 2 (RGB), Compression 0, Filter 0, Interlace 0
    ihdr_data = struct.pack(">IIBBBBB", width, height, 8, 2, 0, 0, 0)
    ihdr_crc = zlib.crc32(b"IHDR" + ihdr_data)
    ihdr_chunk = struct.pack(">I", len(ihdr_data)) + b"IHDR" + ihdr_data + struct.pack(">I", ihdr_crc)

    # Raw image data (RGB): pro každý řádek filter byte (0) + 3 bajty na pixel (R, G, B)
    raw_lines = []
    line_bytes = b"\x00" + (b"\x64\x95\xed" * width)  # modrá barva
    for _ in range(height):
        raw_lines.append(line_bytes)
    raw_data = b"".join(raw_lines)
    compressed_data = zlib.compress(raw_data)

    # IDAT chunk
    idat_crc = zlib.crc32(b"IDAT" + compressed_data)
    idat_chunk = struct.pack(">I", len(compressed_data)) + b"IDAT" + compressed_data + struct.pack(">I", idat_crc)

    # IEND chunk
    iend_crc = zlib.crc32(b"IEND")
    iend_chunk = struct.pack(">I", 0) + b"IEND" + struct.pack(">I", iend_crc)

    png_bytes = png_header + ihdr_chunk + idat_chunk + iend_chunk
    target_path.write_bytes(png_bytes)
    return target_path
