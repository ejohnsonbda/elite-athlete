#!/usr/bin/env python3
"""
Parse Elite Athlete Sponsorship CSV and match documents to applicants.
Outputs structured JSON data for embedding in the HTML app.
"""
import csv
import json
import os
import re

CSV_FILE = '/home/ubuntu/elite-athlete-work/Elite_Athlete_Sponsorship_Appli2026-04-01_23_10_47.csv'
DOCS_BASE = '/home/ubuntu/elite-athlete-work/docs/2025 Elite Athlete Sponsorship Application  '

def extract_submission_id(url):
    """Extract the 19-digit submission ID from a JotForm URL."""
    if not url:
        return None
    m = re.search(r'/(\d{19})/', url)
    return m.group(1) if m else None

def get_files_for_submission(submission_id):
    """Get all files in a submission folder."""
    if not submission_id:
        return [], []
    folder = os.path.join(DOCS_BASE, submission_id)
    if not os.path.isdir(folder):
        return [], []
    files = []
    paths = []
    for f in sorted(os.listdir(folder)):
        fpath = os.path.join(folder, f)
        if os.path.isfile(fpath):
            files.append(f)
            # Relative path from the app root (docs/ folder)
            rel = f'docs/2025 Elite Athlete Sponsorship Application  /{submission_id}/{f}'
            paths.append(rel)
    return files, paths

def clean_amount(val):
    """Clean and normalize dollar amount."""
    if not val:
        return ''
    val = str(val).strip().replace(',', '').replace('$', '')
    try:
        f = float(val)
        return f'${f:,.2f}'
    except:
        return val

def parse_csv():
    applicants = []
    with open(CSV_FILE, encoding='utf-8-sig') as f:
        reader = csv.DictReader(f)
        for idx, row in enumerate(reader, 1):
            name = row.get('Name of Athlete:', '').strip()
            if not name:
                continue

            # Extract submission ID from docs URL
            docs_url = row.get('Please Upload  the  supporting documents', '')
            passport_url = row.get('Please upload a certified copy of a Bermudian passport.', '')
            submission_id = extract_submission_id(docs_url) or extract_submission_id(passport_url)

            # Get matched files
            files, file_paths = get_files_for_submission(submission_id)

            # Parse name
            parts = name.split()
            first_name = parts[0] if parts else name
            last_name = ' '.join(parts[1:]) if len(parts) > 1 else ''

            # Clean amount
            amount_raw = row.get('Total amount requested:', '').strip()
            amount_display = clean_amount(amount_raw)
            try:
                amount_num = float(amount_raw.replace(',', '').replace('$', '')) if amount_raw else 0
            except:
                amount_num = 0

            # BOA category
            boa_cat = row.get('BOA Elite Athlete Category:\xa0\xa0 (If applicable)', '').strip()

            # Submission date
            sub_date = row.get('Submission Date', '').strip()

            # Period
            start_period = row.get('Starting Period for which sponsorship is being requested:', '').strip()
            end_period = row.get('Ending Period for which sponsorship is being requested:', '').strip()

            # Accomplishments
            accomplishments = row.get('Please provide details of your accomplishments in the last (5) five years within your respective sport', '').strip()

            # Goals
            goals = row.get('Please provide a projected indication of the applicant\u2019s goals for the next two (2) years within your respective sport: ', '').strip()

            # Purpose
            purpose = row.get('Outline the intended purpose of Elite Athlete Sponsorship ', '').strip()

            # Budget details
            budget_details = row.get('Please include itemized budget & assisted quotes', '').strip()

            # Requested amount (second field)
            req_amount = row.get('Requested Sponsorship Amount ', '').strip()

            applicant = {
                'id': idx,
                'submissionId': submission_id or '',
                'submissionDate': sub_date,
                'firstName': first_name,
                'lastName': last_name,
                'fullName': name,
                'nsgb': row.get('NSGB Affiliation:', '').strip(),
                'boaCategory': boa_cat,
                'phone': row.get('Phone Number', '').strip(),
                'email': row.get('Email', '').strip(),
                'age': row.get('Age', '').strip(),
                'sport': row.get('Sport', '').strip(),
                'performanceLevel': row.get('Current level of performance', '').strip(),
                'accomplishments': accomplishments,
                'additionalAccomplishments': row.get('Please upload additional accomplishment information if necessary', '').strip(),
                'goals': goals,
                'purpose': purpose,
                'budgetDetails': budget_details,
                'startPeriod': start_period,
                'endPeriod': end_period,
                'totalAmountRaw': amount_raw,
                'totalAmount': amount_display,
                'totalAmountNum': amount_num,
                'requestedAmount': req_amount,
                'signature': row.get('Signature', '').strip(),
                'submitterName': row.get('Name of the Person Submitting', '').strip(),
                'submitterPosition': row.get('Position ', '').strip(),
                'passportUrl': passport_url,
                'docsUrl': docs_url,
                'uploadedFiles': files,
                'uploadedFilePaths': file_paths,
                'docFolder': f'docs/2025 Elite Athlete Sponsorship Application  /{submission_id}' if submission_id else '',
            }
            applicants.append(applicant)

    return applicants

if __name__ == '__main__':
    data = parse_csv()
    print(f'Parsed {len(data)} applicants')
    for a in data:
        print(f"  [{a['id']:2d}] {a['fullName']:35s} | {a['sport']:30s} | {a['totalAmount']:12s} | {len(a['uploadedFiles'])} docs | ID:{a['submissionId']}")

    # Save JSON
    out_path = '/home/ubuntu/elite-athlete-work/applicants.json'
    with open(out_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print(f'\nSaved to {out_path}')
