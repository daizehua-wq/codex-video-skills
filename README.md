# codex-video-skills

Four separate Codex Skills for evidence-led talking-head video production:

1. video-fact-checker — verifies claims and produces fact_card.json, fact_card.md and sources.md.
2. video-script-writer — turns an approved fact card into narration.md and script_claims.json.
3. video-director — turns final narration into director_plan.json and broll_requests.json.
4. broll-asset-executor — fulfills explicit B-roll requests and produces assets plus manifests.

Pipeline:

    topic / source materials
            ↓
    video-fact-checker
            ↓
    fact_card.json + fact_card.md + sources.md
            ↓
    video-script-writer
            ↓
    narration.md + script_claims.json
            ↓
    video-director
            ↓
    director_plan.json + broll_requests.json
            ↓
    broll-asset-executor
            ↓
    assets/ + manifest.csv + manifest.json + sources.md

Responsibility boundaries are deliberate: fact checking does not write the story, script writing does not invent facts, directing does not acquire assets, and B-roll execution does not add shot requirements.
