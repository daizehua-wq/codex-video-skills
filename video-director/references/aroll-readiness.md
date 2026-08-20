# A-roll Readiness Gate

Read this reference before producing a final director timeline or executable B-roll requests.

## Human-owned work

The director does not record A-roll or decide which take, mistake, pause, expression or delivery should survive. A human owns:

- recording;
- take selection;
- mistake and false-start removal;
- pacing and pause adjustment;
- pickup recording;
- final performance approval.

The readiness gate verifies the resulting handoff. It does not redo or judge that human work.

## Required final inputs

1. A human-finalized A-roll media file.
2. Explicit human confirmation that the cut is locked.
3. A timecoded transcript or subtitle file generated from that exact cut.
4. A runtime probed from the media container.
5. Delivery aspect ratio or intended crop.

The transcript may be SRT or another format that exposes ordered start and end times. If the transcript came from an earlier take or edit, the gate fails until it is regenerated or realigned.

## Mechanical checks

- the A-roll file exists and can be probed;
- video duration is greater than zero and comes from the media file;
- a video stream and an audio stream are present unless the user explicitly approves a silent source;
- the transcript exists and contains at least one valid timed cue;
- cue times are ordered and each cue ends after it starts;
- the last cue does not extend beyond the media runtime, allowing only a small container rounding tolerance;
- human finalization is explicitly confirmed.

These checks do not prove that the words are transcribed correctly. The director must still compare material script anchors with the supplied transcript.

## Outcomes

### execution_ready

All required inputs and checks pass. The director may output:

    director_plan.json
    broll_requests.json

Both files must record measured timing and the readiness result. `broll_requests.json` is now safe to hand to the B-roll executor.

Passing this gate authorizes measured planning; it does not imply that any beat requires B-roll or that a visual coverage target must be reached.

### draft_only

Any required input or check is missing, the A-roll is still changing, or the user only wants pre-recording planning. The director may output:

    director_plan.draft.json
    aroll_readiness_report.json

Do not create or refresh executable `broll_requests.json`. If an older request file exists, identify it as stale and do not imply that it matches the current A-roll.

## Final handoff fields

The `project` object in both final files must include:

    "handoff_status": "execution_ready",
    "timing_basis": "measured",
    "aroll_readiness": {
      "human_finalized": true,
      "media_file": "aroll_master.mov",
      "transcript_file": "transcript.srt",
      "duration_source": "probed_media",
      "checks": {
        "media_readable": true,
        "video_stream_present": true,
        "audio_stream_present": true,
        "duration_measured": true,
        "transcript_timecoded": true,
        "transcript_within_runtime": true,
        "human_lock_confirmed": true
      },
      "notes": []
    }

Use project-relative paths when the files belong to the project workspace. Do not claim a check passed without observing the relevant file or receiving the required human confirmation.
