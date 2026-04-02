# Elite Athlete Sponsorship Applications 2025

**Bermuda Department of Youth, Sport & Recreation**

A standalone HTML dashboard for reviewing and managing the 2025 Elite Athlete Sponsorship applications.

## Features

- **46 applicants** across 20+ sports, with all data embedded in the page
- **Document matching** — each applicant's uploaded files are linked directly from their folder
- **Full-text search** across name, sport, NSGB, and email
- **Filter** by sport, document status, and application status
- **Application status tracking** (Pending / Under Review / Approved / Declined) — synced via Supabase
- **Shortlist management** — star applicants and export shortlists
- **Analytics charts** — sports breakdown, amounts by sport, NSGB distribution, BOA categories, amount distribution
- **Export** to CSV, JSON, or printable PDF
- **Sortable table** with pagination
- **Detailed modal** showing full application, accomplishments, goals, budget details, and all uploaded documents
- **Access code login** with session persistence

## Access Codes

```
EAS001  EAS002  EAS003  EAS004  EAS005
ELITE1  ELITE2  ELITE3  ADMIN1  REVIEW1
```

## Running Locally

1. Clone the repository
2. Open `index.html` in your browser — no server required
3. Documents are linked via relative paths in the `docs/` folder

## Deployment

Host on GitHub Pages or any static file server. The `docs/` folder must be present alongside `index.html` for document links to work.

## Architecture

- Single-file HTML with all CSS, JS, and applicant data embedded
- Supabase backend for shortlist and status persistence across sessions
- Document files stored in `docs/2025 Elite Athlete Sponsorship Application  /{submissionId}/`
