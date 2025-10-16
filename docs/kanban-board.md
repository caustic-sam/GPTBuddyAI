# GPTBuddyAI Kanban Board Guide

The GPTBuddyAI project uses a GitHub Project (beta) board configured as a Kanban workflow. This document captures the canonical column definitions, WIP limits, swimlanes, and automation rules so the board stays useful as the project scales.

## Columns & Policies
| Column | Purpose | Exit Criteria | Suggested WIP |
| --- | --- | --- | --- |
| Backlog | Intake for new ideas and unsorted requests. | Item reviewed during backlog grooming. | ∞ |
| Ready | Groomed work with acceptance criteria, estimate, and owner. | Owner signs off on scope and dependencies resolved. | 7 |
| In Progress | Active development or investigation. | Code complete, tests passing, PR raised. | 4 |
| Review | Awaiting review, QA, or stakeholder validation. | Approved PR merged, validation checklist complete. | 6 |
| Done | Completed, deployed, and documented work. | Release notes updated, documentation merged. | ∞ |

## Swimlanes
- **MVP Delivery** – Critical scope for the two-week MVP.
- **Tech Debt & Tooling** – Infrastructure, refactoring, automation.
- **Icebox** – Low priority or paused initiatives.

Assign items to swimlanes via the `Milestone` or `Custom Field` filters in GitHub Projects.

## Field Schema
Add the following custom fields to each project item:
- `Priority`: Enum (`P0`, `P1`, `P2`, `P3`). Default `P2`.
- `Milestone`: Free-text or GitHub milestone reference (e.g., `MVP-2025-02`).
- `Target Release`: Date for planned delivery.
- `Blocked`: Boolean with reason captured in comments.

## Board Hygiene Rituals
- **Daily**: Move items right-to-left during standup. Update blockers and due dates.
- **Weekly**: Run backlog grooming (triage new items, adjust estimates, archive stale cards).
- **Per Release**: Verify all items in `Done` have documentation/pr links before closing the milestone.

## Automation Suggestions
1. **Status Sync** – Use GitHub Actions to move cards when PRs close:
   ```yaml
   # .github/workflows/project-auto-update.yml (future)
   on:
     pull_request:
       types: [closed]
   jobs:
     sync-project:
       runs-on: ubuntu-latest
       steps:
         - uses: actions/github-script@v7
           with:
             github-token: ${{ secrets.PROJECT_TOKEN }}
             script: |
               // Move linked project item to "Done" when PR merged
   ```
2. **WIP Alerts** – Nightly workflow to comment on items if `In Progress` exceeds limit.
3. **Template Cards** – Save `Ready` column default fields (labels, priority) to reduce triage time.

## Meeting Cadence
- **Standup**: 15 min daily. Focus on board updates and blockers.
- **Backlog Grooming**: 45 min weekly. Review `Backlog` and `Ready` columns.
- **MVP Demo**: End of Week 2. Showcase Streamlit UI + analytics.

## Tips for Effective Use
- Reference issues directly in PR descriptions to auto-link card status.
- Keep descriptions short; move detailed implementation plans to the issue body or `docs/`.
- Use labels for quick board filtering (`area:*`, `priority:*`, `type:*`).
- Archive cards older than 90 days in `Done` to maintain board performance.
