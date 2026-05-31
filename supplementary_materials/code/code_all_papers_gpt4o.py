#!/usr/bin/env python3
"""
GPT-4o Paper Coding Script for Adversarial ML Literature Review
================================================================

This script:
1. Finds all PDFs in the raw_papers folder
2. Extracts up to 15 pages per paper for sufficient context
3. Sends to GPT-4o with standardized coding prompt
4. Parses responses and saves to CSV

Usage:
    export OPENAI_API_KEY="your-api-key"
    python3 code_all_papers_gpt4o.py

Output:
    gpt4o_coding_results_v2.csv
"""

import os
import sys
import csv
import time
import re
from pathlib import Path
from typing import Optional, Dict, List, Tuple

# PDF extraction
try:
    import fitz  # PyMuPDF for PDF text extraction
except ImportError:
    print("Installing PyMuPDF...")
    os.system("pip install pymupdf")
    import fitz

# OpenAI API
try:
    from openai import OpenAI
except ImportError:
    print("Installing openai...")
    os.system("pip install openai")
    from openai import OpenAI


# Configuration
RAW_PAPERS_DIR = Path(os.environ.get("RAW_PAPERS_DIR", "../raw_papers"))
OUTPUT_DIR = Path(os.environ.get("OUTPUT_DIR", "../data"))
OUTPUT_CSV = OUTPUT_DIR / "gpt4o_coding_results_v2.csv"
CHECKPOINT_CSV = OUTPUT_DIR / "checkpoint_progress.csv"

# Rate limiting
REQUESTS_PER_MINUTE = 50  # Conservative limit
DELAY_BETWEEN_REQUESTS = 60 / REQUESTS_PER_MINUTE  # 1.2 seconds

# Standardized coding prompt
SYSTEM_PROMPT = """You are a research assistant coding adversarial machine learning papers for a systematic literature review. Provide consistent, reproducible codings based on the operational definitions provided. Answer only with the specified options."""

USER_PROMPT_TEMPLATE = """Analyze this adversarial machine learning research paper and code it according to the dimensions below.

PAPER CONTENT:
{paper_text}

=== CODING DIMENSIONS ===

**G1. Primary Contribution**
What is the paper's main contribution?
OPTIONS: atk | def | both
- atk: Proposes a new attack method or technique
- def: Proposes a new defense, detection, or mitigation method
- both: Proposes both a novel attack AND a novel defense in the same paper

**G2. Attack Category**
What type of adversarial attack does the paper address?
OPTIONS: Evasion | Poisoning | Privacy | Multiple | NA
- Evasion: Test-time attacks that perturb inputs to cause misclassification (adversarial examples)
- Poisoning: Training-time attacks that corrupt the model (backdoors, trojans, data poisoning)
- Privacy: Attacks that extract information (membership inference, model extraction, attribute inference)
- Multiple: Paper addresses more than one attack category
- NA: Defense paper that does not focus on a specific attack type

**G3. Data Modality**
What is the primary data type used in experiments?
OPTIONS: Images | Text | Audio | Malware | Other
- Images: Vision tasks (classification, object detection, face recognition)
- Text: NLP tasks (classification, language models, sentiment)
- Audio: Speech/acoustic tasks
- Malware: Binary analysis, network intrusion detection
- Other: Tabular, graphs, multimodal, reinforcement learning, federated learning

**G4. Economic Analysis**
Does the paper include explicit economic or cost-benefit analysis?
OPTIONS: Yes | No
- Yes: Paper explicitly analyzes monetary costs, economic incentives, market implications, or formal cost-benefit tradeoffs of attacks/defenses
- No: Paper focuses on technical evaluation (accuracy, robustness metrics) without economic framing
Note: Standard technical metrics (computation time, query counts, perturbation budgets) are NOT economic analysis unless explicitly framed in monetary or market terms.

**G5. Code Availability**
Is implementation code publicly available?
OPTIONS: Yes | No
- Yes: Paper states code is released (GitHub, artifact, supplementary materials)
- No: No code availability mentioned

**G6. Real-World Deployment**
Was the method evaluated on production/commercial systems?
OPTIONS: Yes | No
- Yes: Tested on deployed systems (commercial APIs, real-world applications with actual users)
- No: Evaluated only on research datasets and academic models

**T1. Threat Model**
What level of model access does the attacker have?
OPTIONS: White-box | Gray-box | Black-box | White-box/Black-box | NA
- White-box: Full access to model internals (architecture, weights, gradients)
- Gray-box: Partial access (e.g., architecture known, weights unknown; or surrogate model)
- Black-box: Query access only (input-output pairs, no internal access)
- White-box/Black-box: Paper evaluates under both threat models
- NA: Not applicable (e.g., defense paper where attacker model access is not the focus)

**Q1. Gradient Dependency**
Does the proposed method require gradient computation?
OPTIONS: Yes | No | NA
- Yes: Method requires backpropagation through the target model
- No: Gradient-free method (zeroth-order optimization, evolutionary, decision-based)
- NA: Not applicable (defense-only paper, or method where gradient access is irrelevant)

**Q2. Query Complexity**
How many queries to the target model does the method require?
OPTIONS: High | Low | None | NA
- High: Requires >1000 model queries
- Low: Requires 1-1000 model queries
- None: No queries required (e.g., white-box with direct gradient access, transfer attacks)
- NA: Not applicable (defense paper, or query count not relevant to the method)

=== OUTPUT FORMAT ===

Provide answers in exactly this format with no additional text:

G1: [answer]
G2: [answer]
G3: [answer]
G4: [answer]
G5: [answer]
G6: [answer]
T1: [answer]
Q1: [answer]
Q2: [answer]"""


def extract_pages(pdf_path: Path, max_pages: int = 15, max_chars: int = 50000) -> Optional[str]:
    """Extract text from up to max_pages pages of PDF."""
    try:
        doc = fitz.open(pdf_path)
        if len(doc) == 0:
            return None

        # Extract up to max_pages
        pages_to_extract = min(len(doc), max_pages)
        text_parts = []

        for i in range(pages_to_extract):
            page = doc[i]
            text_parts.append(page.get_text())

        doc.close()

        text = "\n".join(text_parts)

        # Clean up text
        text = re.sub(r'\s+', ' ', text)  # Normalize whitespace
        text = text.strip()

        # Truncate if too long (safety limit)
        if len(text) > max_chars:
            text = text[:max_chars] + "..."

        return text if text else None

    except Exception as e:
        print(f"  ERROR extracting {pdf_path.name}: {e}")
        return None


def parse_gpt_response(response_text: str) -> Dict[str, str]:
    """Parse GPT-4o response into coding dimensions."""
    result = {
        'G1': '', 'G2': '', 'G3': '', 'G4': '',
        'G5': '', 'G6': '', 'T1': '', 'Q1': '', 'Q2': ''
    }

    # Parse each line
    for line in response_text.strip().split('\n'):
        line = line.strip()
        if ':' in line:
            key, value = line.split(':', 1)
            key = key.strip().upper()
            value = value.strip()
            if key in result:
                result[key] = value

    return result


def get_paper_metadata(pdf_path: Path) -> Tuple[str, str, str]:
    """Extract conference and year from folder structure."""
    parts = pdf_path.parts

    # Find conference from folder name
    for part in parts:
        if 'acm' in part.lower():
            conference = 'ACM'
            break
        elif 'ieee' in part.lower():
            conference = 'IEEE'
            break
        elif 'nds' in part.lower() or 'ndss' in part.lower():
            conference = 'NDSS'
            break
        elif 'usenix' in part.lower():
            conference = 'USENIX'
            break
    else:
        conference = 'Unknown'

    # Find year from folder name (look for 4-digit year)
    year = 'Unknown'
    for part in parts:
        if part.isdigit() and len(part) == 4:
            year = part
            break

    filename = pdf_path.name

    return conference, year, filename


def find_all_pdfs() -> List[Path]:
    """Find all PDF files in the raw_papers directory."""
    pdfs = []

    for conf_dir in RAW_PAPERS_DIR.iterdir():
        if conf_dir.is_dir() and not conf_dir.name.startswith('.'):
            for year_dir in conf_dir.iterdir():
                if year_dir.is_dir() and year_dir.name.isdigit():
                    for pdf in year_dir.glob("*.pdf"):
                        pdfs.append(pdf)

    return sorted(pdfs)


def load_checkpoint() -> set:
    """Load already processed paper filenames from checkpoint."""
    processed = set()
    if CHECKPOINT_CSV.exists():
        with open(CHECKPOINT_CSV, 'r') as f:
            reader = csv.DictReader(f)
            for row in reader:
                processed.add(row['Filename'])
    return processed


def code_papers(dry_run: bool = False):
    """Main function to code all papers."""

    # Check for API key
    api_key = os.environ.get('OPENAI_API_KEY')
    if not api_key and not dry_run:
        print("ERROR: OPENAI_API_KEY environment variable not set!")
        print("Usage: export OPENAI_API_KEY='your-key' && python code_all_papers_gpt4o.py")
        sys.exit(1)

    # Initialize OpenAI client
    client = OpenAI() if not dry_run else None

    # Find all PDFs
    all_pdfs = find_all_pdfs()
    print(f"Found {len(all_pdfs)} PDF papers to process")

    # Load checkpoint (already processed papers)
    processed = load_checkpoint()
    print(f"Already processed: {len(processed)} papers")

    # Filter out already processed
    pdfs_to_process = [p for p in all_pdfs if p.name not in processed]
    print(f"Remaining to process: {len(pdfs_to_process)} papers")

    if dry_run:
        print("\n=== DRY RUN MODE ===")
        print("Would process these papers:")
        for i, pdf in enumerate(pdfs_to_process[:10]):
            conf, year, fname = get_paper_metadata(pdf)
            print(f"  {i+1}. [{conf} {year}] {fname}")
        if len(pdfs_to_process) > 10:
            print(f"  ... and {len(pdfs_to_process) - 10} more")
        return

    # Create output directory
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    # Prepare CSV headers
    headers = ['Paper_ID', 'Year', 'Conference', 'Filename',
               'G1', 'G2', 'G3', 'G4', 'G5', 'G6', 'T1', 'Q1', 'Q2',
               'Raw_Response', 'Error']

    # Open output file (append mode if exists)
    write_header = not CHECKPOINT_CSV.exists()

    with open(CHECKPOINT_CSV, 'a', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=headers)
        if write_header:
            writer.writeheader()

        # Process each paper
        for i, pdf_path in enumerate(pdfs_to_process):
            paper_id = len(processed) + i + 1
            conf, year, filename = get_paper_metadata(pdf_path)

            print(f"\n[{paper_id}/{len(all_pdfs)}] Processing: {filename}")
            print(f"  Conference: {conf}, Year: {year}")

            # Extract up to 15 pages
            text = extract_pages(pdf_path, max_pages=15)

            if not text:
                print(f"  SKIPPED: Could not extract text")
                row = {
                    'Paper_ID': paper_id, 'Year': year, 'Conference': conf,
                    'Filename': filename, 'G1': '', 'G2': '', 'G3': '',
                    'G4': '', 'G5': '', 'G6': '', 'T1': '', 'Q1': '', 'Q2': '',
                    'Raw_Response': '', 'Error': 'Failed to extract text'
                }
                writer.writerow(row)
                f.flush()
                continue

            print(f"  Extracted {len(text)} chars")

            # Call GPT-4o
            try:
                response = client.chat.completions.create(
                    model="gpt-4o",
                    temperature=0,
                    max_tokens=400,
                    messages=[
                        {"role": "system", "content": SYSTEM_PROMPT},
                        {"role": "user", "content": USER_PROMPT_TEMPLATE.format(paper_text=text)}
                    ]
                )

                raw_response = response.choices[0].message.content
                parsed = parse_gpt_response(raw_response)

                print(f"  G1={parsed['G1']}, G2={parsed['G2']}, G3={parsed['G3']}, G4={parsed['G4']}")

                row = {
                    'Paper_ID': paper_id, 'Year': year, 'Conference': conf,
                    'Filename': filename,
                    'G1': parsed['G1'], 'G2': parsed['G2'], 'G3': parsed['G3'],
                    'G4': parsed['G4'], 'G5': parsed['G5'], 'G6': parsed['G6'],
                    'T1': parsed['T1'], 'Q1': parsed['Q1'], 'Q2': parsed['Q2'],
                    'Raw_Response': raw_response.replace('\n', ' | '),
                    'Error': ''
                }

            except Exception as e:
                print(f"  ERROR: {e}")
                row = {
                    'Paper_ID': paper_id, 'Year': year, 'Conference': conf,
                    'Filename': filename, 'G1': '', 'G2': '', 'G3': '',
                    'G4': '', 'G5': '', 'G6': '', 'T1': '', 'Q1': '', 'Q2': '',
                    'Raw_Response': '', 'Error': str(e)
                }

            writer.writerow(row)
            f.flush()

            # Rate limiting
            time.sleep(DELAY_BETWEEN_REQUESTS)

    # Create final output file (clean version without raw response/errors)
    print(f"\n\nCreating final output: {OUTPUT_CSV}")

    with open(CHECKPOINT_CSV, 'r') as f_in, open(OUTPUT_CSV, 'w', newline='') as f_out:
        reader = csv.DictReader(f_in)
        clean_headers = ['Paper_ID', 'Year', 'Conference', 'Filename',
                        'G1', 'G2', 'G3', 'G4', 'G5', 'G6', 'T1', 'Q1', 'Q2']
        writer = csv.DictWriter(f_out, fieldnames=clean_headers)
        writer.writeheader()

        for row in reader:
            clean_row = {k: row[k] for k in clean_headers}
            writer.writerow(clean_row)

    print(f"\nDone! Results saved to: {OUTPUT_CSV}")


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Code adversarial ML papers using GPT-4o")
    parser.add_argument('--dry-run', action='store_true',
                       help="Show what would be processed without calling API")

    args = parser.parse_args()
    code_papers(dry_run=args.dry_run)
