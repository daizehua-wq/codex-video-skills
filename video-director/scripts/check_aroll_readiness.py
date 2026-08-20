#!/usr/bin/env python3
"""Check whether a human-finalized A-roll and SRT are ready for directing."""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from pathlib import Path


TIMECODE_RE = re.compile(
    r"(?P<sh>\d{2}):(?P<sm>\d{2}):(?P<ss>\d{2})[,.](?P<sms>\d{3})"
    r"\s+-->\s+"
    r"(?P<eh>\d{2}):(?P<em>\d{2}):(?P<es>\d{2})[,.](?P<ems>\d{3})"
)


def seconds(hours: str, minutes: str, secs: str, millis: str) -> float:
    return int(hours) * 3600 + int(minutes) * 60 + int(secs) + int(millis) / 1000


def probe_media(path: Path) -> dict:
    command = [
        "ffprobe",
        "-v",
        "error",
        "-show_entries",
        "format=duration:stream=codec_type,codec_name,width,height,avg_frame_rate",
        "-of",
        "json",
        str(path),
    ]
    result = subprocess.run(command, capture_output=True, text=True, check=False)
    if result.returncode != 0:
        raise ValueError(result.stderr.strip() or "ffprobe could not read the media")
    return json.loads(result.stdout)


def parse_srt(path: Path) -> list[tuple[float, float]]:
    cues: list[tuple[float, float]] = []
    for match in TIMECODE_RE.finditer(path.read_text(encoding="utf-8-sig")):
        values = match.groupdict()
        start = seconds(values["sh"], values["sm"], values["ss"], values["sms"])
        end = seconds(values["eh"], values["em"], values["es"], values["ems"])
        cues.append((start, end))
    return cues


def main() -> int:
    parser = argparse.ArgumentParser(description="Check A-roll readiness for video-director")
    parser.add_argument("--aroll", required=True, type=Path)
    parser.add_argument("--transcript", required=True, type=Path)
    parser.add_argument("--human-finalized", action="store_true")
    parser.add_argument("--allow-silent", action="store_true")
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()

    checks = {
        "media_readable": False,
        "video_stream_present": False,
        "audio_stream_present": False,
        "duration_measured": False,
        "transcript_timecoded": False,
        "transcript_within_runtime": False,
        "human_lock_confirmed": bool(args.human_finalized),
    }
    notes: list[str] = []
    duration = None
    media_details: dict = {}
    cue_count = 0

    if not args.aroll.is_file():
        notes.append(f"A-roll file not found: {args.aroll}")
    else:
        try:
            probe = probe_media(args.aroll)
            checks["media_readable"] = True
            duration = float(probe.get("format", {}).get("duration", 0))
            checks["duration_measured"] = duration > 0
            streams = probe.get("streams", [])
            videos = [stream for stream in streams if stream.get("codec_type") == "video"]
            audios = [stream for stream in streams if stream.get("codec_type") == "audio"]
            checks["video_stream_present"] = bool(videos)
            checks["audio_stream_present"] = bool(audios) or args.allow_silent
            if videos:
                media_details = {
                    "width": videos[0].get("width"),
                    "height": videos[0].get("height"),
                    "video_codec": videos[0].get("codec_name"),
                    "frame_rate": videos[0].get("avg_frame_rate"),
                    "audio_codec": audios[0].get("codec_name") if audios else None,
                }
        except (OSError, ValueError, json.JSONDecodeError) as exc:
            notes.append(str(exc))

    if not args.transcript.is_file():
        notes.append(f"Transcript file not found: {args.transcript}")
    else:
        cues = parse_srt(args.transcript)
        cue_count = len(cues)
        valid_order = bool(cues)
        previous_start = -1.0
        for start, end in cues:
            if start < previous_start or end <= start:
                valid_order = False
                break
            previous_start = start
        checks["transcript_timecoded"] = valid_order
        if valid_order and duration is not None:
            checks["transcript_within_runtime"] = cues[-1][1] <= duration + 0.75

    if not args.human_finalized:
        notes.append("Human finalization was not confirmed")

    ready = all(checks.values())
    report = {
        "status": "execution_ready" if ready else "draft_only",
        "human_finalized": bool(args.human_finalized),
        "media_file": str(args.aroll),
        "transcript_file": str(args.transcript),
        "duration_source": "probed_media" if checks["duration_measured"] else None,
        "runtime_sec": round(duration, 3) if duration is not None else None,
        "transcript_cue_count": cue_count,
        "media_details": media_details,
        "checks": checks,
        "notes": notes,
    }
    rendered = json.dumps(report, ensure_ascii=False, indent=2)
    if args.output:
        args.output.write_text(rendered + "\n", encoding="utf-8")
    print(rendered)
    return 0 if ready else 1


if __name__ == "__main__":
    raise SystemExit(main())
