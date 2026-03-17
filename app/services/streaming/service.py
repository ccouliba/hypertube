"""
StreamingService - Handles HTTP video streaming with Range support and FFmpeg remuxing.

Responsibilities:
- Serve MP4/WebM files with HTTP 206 Range responses (seek support, zero CPU)
- Remux MKV/AVI/etc. to fragmented MP4 via FFmpeg -c copy (no re-encode)

This service is Flask-agnostic regarding request parsing:
the caller (API layer) is responsible for extracting the Range header
and passing it as a plain string.
"""
import os
import subprocess
import logging
from pathlib import Path
from typing import (Optional, Generator)
from flask import Response
from app.core.errors.handlers import APIError
from app.core.errors.messages import ERROR_MESSAGES

LOGGER: logging.Logger = logging.getLogger(__name__)
BROWSER_NATIVE_EXTENSIONS: dict[str, str] = {
    ".mp4":  "video/mp4",
    ".webm": "video/webm",
    ".ogg":  "video/ogg",
}
# Minimum bytes downloaded before we attempt to stream
MIN_STREAMABLE_BYTES: int = 10 * 1024 * 1024  # 10 MB
CHUNK_SIZE: int = 65_536  # 64 KB read chunks


class StreamingService:
    """
    Provides video streaming responses.
    Stateless — can be instantiated once and reused across requests.
    """

    def stream(
        self,
        file_path: str,
        range_header: Optional[str] = None
    ) -> Response:
        """
        Build the appropriate streaming Response for a given file.
        Args:
            file_path:    Absolute path to the (possibly partial) video file.
            range_header: Value of the HTTP Range header, e.g. "bytes=0-1023".
                          Provided by the API layer from flask.request.
        Returns:
            A Flask Response (206 partial or 200 full).
        Raises:
            APIError 404: file does not exist.
            APIError 503: not enough data downloaded yet.
        """
        if not os.path.exists(file_path):
            LOGGER.warning(f"StreamingService: file not found on disk: {file_path}")
            raise APIError(404, ERROR_MESSAGES["VIDEO_FILE_NOT_ON_DISK"])
        file_size_bytes: int = os.path.getsize(file_path)
        if file_size_bytes < MIN_STREAMABLE_BYTES:
            LOGGER.warning(
                f"StreamingService: not enough data yet ({file_size_bytes // (1024*1024)} MB "
                f"< {MIN_STREAMABLE_BYTES // (1024*1024)} MB): {file_path}"
            )
            raise APIError(503, ERROR_MESSAGES["VIDEO_STILL_DOWNLOADING"])
        ext: str = Path(file_path).suffix.lower()
        LOGGER.info(
            f"StreamingService: {'Range' if range_header else 'full'} request for {Path(file_path).name} "
            f"({file_size_bytes // (1024*1024)} MB)"
        )
        if mimetype := BROWSER_NATIVE_EXTENSIONS.get(ext):
            LOGGER.debug(f"StreamingService: {ext} natively with Range support: {file_path}")
            return self._range_response(file_path, mimetype, range_header)
        LOGGER.debug(f"StreamingService: Remuxing {ext} → MP4 via FFmpeg: {file_path}")
        return self._ffmpeg_remux_response(file_path)

    def _range_response(
        self,
        file_path: str,
        mimetype: str,
        range_header: Optional[str],
    ) -> Response:
        """
        Serve a file with HTTP 206 Partial Content support.
        Enables seek / time-scrubbing in the browser <video> element.
        """
        file_size: int = os.path.getsize(file_path)
        if not range_header:
            return Response(
                self._read_chunks(file_path, 0, file_size),
                mimetype=mimetype,
                headers={
                    "Accept-Ranges":  "bytes",
                    "Content-Length": str(file_size),
                },
            )
        start, end = self._parse_range(range_header, file_size)
        length: int = end - start + 1
        return Response(
            self._read_chunks(file_path, start, length),
            status=206,
            mimetype=mimetype,
            headers={
                "Content-Range":  f"bytes {start}-{end}/{file_size}",
                "Accept-Ranges":  "bytes",
                "Content-Length": str(length),
            },
        )

    def _ffmpeg_remux_response(self, file_path: str) -> Response:
        """
        Remux any container (MKV, AVI…) to fragmented MP4 using FFmpeg -c copy.
        No re-encoding: fast and lossless, works on partial files.
        """
        def generate(path: str):
            cmd: list[str] = [
                "ffmpeg", "-i", path,
                "-c", "copy",
                "-movflags", "frag_keyframe+empty_moov",
                "-f", "mp4", "pipe:1",
            ]
            try:
                proc: subprocess.Popen = subprocess.Popen(
                    cmd,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.DEVNULL
                )
            except FileNotFoundError:
                LOGGER.error("StreamingService: ffmpeg not found — ensure it is installed")
                return
            try:
                while chunk := proc.stdout.read(CHUNK_SIZE):
                    yield chunk
            finally:
                proc.kill()
                proc.wait()
        return Response(generate(file_path), mimetype="video/mp4")

    @staticmethod
    def _parse_range(range_header: str, file_size: int) -> tuple[int, int]:
        """Parse 'bytes=start-end' into (start, end) clamped to file_size."""
        try:
            parts: list[str] = range_header.replace("bytes=", "").split("-")
            start: int = int(parts[0])
            end: int = int(parts[1]) if parts[1] else file_size - 1
            end = min(end, file_size - 1)
            return start, end
        except (ValueError, IndexError):
            raise APIError(400, f"Invalid Range header: {range_header!r}")

    @staticmethod
    def _read_chunks(
        file_path: str,
        start: int,
        length: int
    ) -> Generator[bytes, None, None]:
        """Generator that reads a file from `start` for `length` bytes."""
        try:
            with open(file_path, "rb") as f:
                f.seek(start)
                remaining: int = length
                while remaining > 0:
                    chunk: bytes = f.read(min(CHUNK_SIZE, remaining))
                    if not chunk:
                        break
                    remaining -= len(chunk)
                    yield chunk
        except OSError as e:
            LOGGER.exception("StreamingService: read error for %s", file_path)
