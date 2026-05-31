#!/usr/bin/env python3
"""
Gemini Paper Coding Script for Dual-LLM Validation
====================================================

Codes all 459 papers using Gemini 2.5 Pro as a second independent LLM
to assess and mitigate systematic bias from GPT-4o-only coding.

The prompt has been improved based on systematic disagreement analysis
between human coders and GPT-4o on a 50-paper validation sample.

Usage:
    cd supplementary_materials/code
    python3 code_all_papers_gemini.py           # run all
    python3 code_all_papers_gemini.py --dry-run  # preview only

Output:
    gemini_coding_results.csv
"""

import os
import sys
import csv
import time
import re
from pathlib import Path
from typing import Optional, Dict, List, Tuple
from dotenv import load_dotenv

load_dotenv()

try:
    import fitz
except ImportError:
    os.system("pip3 install pymupdf")
    import fitz

try:
    import google.generativeai as genai
except ImportError:
    os.system("pip3 install google-generativeai")
    import google.generativeai as genai


RAW_PAPERS_DIR = Path(os.environ.get("RAW_PAPERS_DIR", "../raw_papers"))
OUTPUT_DIR = Path(os.environ.get("OUTPUT_DIR", "../data"))
OUTPUT_CSV = OUTPUT_DIR / "gemini_coding_results.csv"
CHECKPOINT_CSV = OUTPUT_DIR / "gemini_checkpoint_progress.csv"

DELAY_BETWEEN_REQUESTS = 4.0
MAX_RETRIES = 3
RETRY_DELAY = 10.0

# ============================================================================
# IMPROVED CODING PROMPT
# Based on systematic disagreement analysis of GPT-4o vs human coding (N=50)
# Key improvements marked with [LESSON] comments
# ============================================================================
CODING_PROMPT = """IMPORTANT: Provide your answer immediately in the specified format below. Do not include any thinking, reasoning, or explanation - only output the coded values.

You are a research assistant coding adversarial machine learning papers for a systematic literature review. Provide consistent, reproducible codings based on the operational definitions provided. Answer ONLY with the specified option values.

Analyze this adversarial machine learning research paper and code it on 9 dimensions.

PAPER CONTENT:
{paper_text}

=== CODING DIMENSIONS ===

**G1. Primary Contribution**
What is the paper's MAIN contribution?
OPTIONS: atk | def | both
- atk: Proposes a new attack method or technique
- def: Proposes a new defense, detection, or mitigation method
- both: Proposes BOTH a novel attack AND a novel defense in the same paper
IMPORTANT: Code "both" if the paper proposes a new attack AND then builds a defense against it (or vice versa). A defense paper that merely evaluates against existing attacks is "def", not "both". A paper that introduces a new attack vector AND a corresponding mitigation is "both".

**G2. Attack Category**
What type of adversarial attack does the paper primarily address?
OPTIONS: Evasion | Poisoning | Privacy | Multiple | NA
- Evasion: Test-time attacks that perturb inputs to cause misclassification (adversarial examples, adversarial patches, jailbreaking)
- Poisoning: Training-time attacks that corrupt the model (backdoors, trojans, data poisoning)
- Privacy: Attacks that extract information (membership inference, model extraction/stealing, attribute inference)
- Multiple: Paper addresses more than one attack category substantially
- NA: Defense paper that does not focus on a specific attack type, or survey/SoK paper

**G3. Data Modality**
What is the PRIMARY data type used in experiments?
OPTIONS: Images | Text | Audio | Malware | Other
- Images: Vision tasks (image classification, object detection, face recognition, autonomous driving perception, traffic signs, medical images)
- Text: NLP tasks (text classification, language models, sentiment, machine translation)
- Audio: Speech/acoustic tasks (speaker verification, speech recognition)
- Malware: Binary analysis, network intrusion detection, malware classification, network traffic analysis
- Other: Tabular data, graphs, multimodal systems, reinforcement learning, federated learning, code, or domains not covered above
NOTE: Code based on the primary data modality the paper's core contribution operates on. Federated learning papers are typically Other even if they use image datasets for evaluation.

**G4. Economic Analysis**
Does the paper include QUANTITATIVE economic or cost-benefit analysis with explicit monetary figures?
OPTIONS: Yes | No
- Yes: Paper includes explicit dollar amounts ("$5,713 to train"), market pricing ("$5-199 subscription"), itemized monetary cost breakdowns, or quantitative ROI calculations with actual figures
- No: Paper focuses on technical evaluation only, OR mentions "cost" or "economic" only qualitatively without providing actual monetary figures
STRICT RULE: Computation time ("3 GPU-hours"), query counts ("10,000 queries"), perturbation budgets, or privacy budgets (epsilon) are NOT economic analysis. The paper must contain actual dollar amounts, pricing, or monetary ROI to qualify as Yes.

**G5. Code Availability**
Is implementation code publicly available?
OPTIONS: Yes | No
- Yes: Paper mentions code release in ANY of: GitHub/GitLab URL, "code available at...", artifact evaluation badge, "supplementary materials include code", footnotes with repository links, or acknowledgment of open-source release
- No: No mention of code availability anywhere in the paper
IMPORTANT: Look carefully in footnotes, acknowledgments, the first page header, appendices, and the paper's final section for code/artifact URLs. Authors often place GitHub links in footnotes or at the very end.

**G6. Real-World Deployment**
Was the method evaluated on a production, commercial, or deployed system?
OPTIONS: Yes | No
- Yes: Tested on deployed/commercial/production systems. This INCLUDES: commercial APIs (OpenAI, Google Cloud Vision, Anthropic, AWS Rekognition, Clarifai, Microsoft Azure), app stores, real social media platforms, commercial voice assistants, deployed malware detection systems, or any system serving real users.
- No: Evaluated ONLY on research datasets (CIFAR, ImageNet, LibriSpeech) and locally-hosted academic models (local ResNet, local BERT, self-hosted LLaMA)
IMPORTANT: If the paper attacks or tests against a commercial API (e.g., "we queried GPT-4 via the OpenAI API", "we tested against Google Cloud Speech-to-Text"), that IS real-world deployment (Yes). Downloading an open-source model and running it locally is NOT.

**T1. Threat Model**
What level of access to the target model does the attacker have (or is assumed to have)?
OPTIONS: White-box | Gray-box | Black-box | White-box/Black-box | NA
- White-box: Full access to model internals (architecture, weights, gradients)
- Gray-box: Partial access (e.g., architecture known but weights unknown; or uses a surrogate/shadow model trained on similar data)
- Black-box: Query access only (input-output pairs, prediction scores, no internal access)
- White-box/Black-box: Paper evaluates under BOTH threat models
- NA: Not applicable (pure survey/SoK papers, measurement studies with no attack/defense component)
NOTE: For defense papers, code the threat model based on what attacker capability the defense is designed to handle. A defense evaluated against white-box adversaries is White-box; one evaluated against query-only adversaries is Black-box. Most attack and defense papers have a threat model — use NA sparingly.

**Q1. Gradient Dependency**
Does the proposed method require gradient computation through the TARGET model?
OPTIONS: Yes | No | NA
- Yes: Method requires backpropagation/gradient computation through the target model (e.g., FGSM, PGD, adversarial training, gradient-based optimization of inputs)
- No: Gradient-free method (zeroth-order optimization, evolutionary algorithms, decision-based attacks, query-based attacks using only predictions, transfer attacks using a separate surrogate, input preprocessing defenses)
- NA: Gradient access is structurally irrelevant to this paper (survey/SoK papers, measurement studies, policy analysis)
NOTE: For defense papers, consider whether the defense method itself computes gradients through the model. Adversarial training and certified robustness methods require gradients (Yes); input filtering and anomaly detection typically do not (No). Use NA sparingly — most papers that involve a model have a definable gradient relationship.

**Q2. Query Complexity**
How many queries to the TARGET model does the method require?
OPTIONS: High | Low | None | NA
- High: Requires >1000 queries to the target model
- Low: Requires 1-1000 queries to the target model
- None: No queries to the target model are needed — the method has direct model access (e.g., white-box gradient attacks where the model is available locally) or uses transfer attacks (craft on a surrogate, no interaction with the target)
- NA: The concept of querying a target model does not apply to this paper (e.g., survey/SoK papers, pure measurement studies)
NOTE on None vs NA: "None" means the paper involves a model but the method doesn't need to query it (because it has direct access or uses transfer). "NA" means there is no meaningful target model interaction in this paper at all.

=== OUTPUT FORMAT ===

Provide answers in EXACTLY this format with no additional text, explanation, or reasoning:

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
    try:
        doc = fitz.open(pdf_path)
        if len(doc) == 0:
            return None
        pages_to_extract = min(len(doc), max_pages)
        text_parts = []
        for i in range(pages_to_extract):
            text_parts.append(doc[i].get_text())
        doc.close()
        text = "\n".join(text_parts)
        text = re.sub(r'\s+', ' ', text).strip()
        if len(text) > max_chars:
            text = text[:max_chars] + "..."
        return text if text else None
    except Exception as e:
        print(f"  ERROR extracting {pdf_path.name}: {e}")
        return None


def parse_response(response_text: str) -> Dict[str, str]:
    result = {k: '' for k in ['G1', 'G2', 'G3', 'G4', 'G5', 'G6', 'T1', 'Q1', 'Q2']}
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
    parts = pdf_path.parts
    conference = 'Unknown'
    for part in parts:
        if 'acm' in part.lower():
            conference = 'ACM'; break
        elif 'ieee' in part.lower():
            conference = 'IEEE'; break
        elif 'nds' in part.lower() or 'ndss' in part.lower():
            conference = 'NDSS'; break
        elif 'usenix' in part.lower():
            conference = 'USENIX'; break
    year = 'Unknown'
    for part in parts:
        if part.isdigit() and len(part) == 4:
            year = part; break
    return conference, year, pdf_path.name


def find_all_pdfs() -> List[Path]:
    pdfs = []
    for conf_dir in RAW_PAPERS_DIR.iterdir():
        if conf_dir.is_dir() and not conf_dir.name.startswith('.'):
            for year_dir in conf_dir.iterdir():
                if year_dir.is_dir() and year_dir.name.isdigit():
                    for pdf in year_dir.glob("*.pdf"):
                        pdfs.append(pdf)
    return sorted(pdfs)


def load_checkpoint() -> set:
    processed = set()
    if CHECKPOINT_CSV.exists():
        with open(CHECKPOINT_CSV, 'r') as f:
            reader = csv.DictReader(f)
            for row in reader:
                processed.add(row['Filename'])
    return processed


def code_papers(dry_run: bool = False):
    api_key = os.environ.get('GOOGLE_API_KEY')
    if not api_key and not dry_run:
        print("ERROR: GOOGLE_API_KEY not found!")
        print("Set it in .env file or: export GOOGLE_API_KEY='your-key'")
        sys.exit(1)

    if not dry_run:
        genai.configure(api_key=api_key)
        
        # Configure safety settings to be more permissive for academic content
        safety_settings = [
            {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_NONE"},
            {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_NONE"},
            {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_NONE"},
            {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_NONE"},
        ]
        
        # Note: Gemini 2.5 Pro uses thinking mode internally which consumes output tokens.
        # Setting max_output_tokens=8192 to accommodate thinking + response.
        model = genai.GenerativeModel(
            'gemini-2.5-pro',
            generation_config=genai.GenerationConfig(
                temperature=0, 
                max_output_tokens=8192,
            ),
            safety_settings=safety_settings
        )

    all_pdfs = find_all_pdfs()
    print(f"Found {len(all_pdfs)} PDF papers")

    processed = load_checkpoint()
    print(f"Already processed: {len(processed)}")

    pdfs_to_process = [p for p in all_pdfs if p.name not in processed]
    print(f"Remaining: {len(pdfs_to_process)}")

    if dry_run:
        print("\n=== DRY RUN ===")
        for i, pdf in enumerate(pdfs_to_process[:10]):
            conf, year, fname = get_paper_metadata(pdf)
            print(f"  {i+1}. [{conf} {year}] {fname}")
        if len(pdfs_to_process) > 10:
            print(f"  ... and {len(pdfs_to_process) - 10} more")
        return

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    headers = ['Paper_ID', 'Year', 'Conference', 'Filename',
               'G1', 'G2', 'G3', 'G4', 'G5', 'G6', 'T1', 'Q1', 'Q2',
               'Raw_Response', 'Error']

    write_header = not CHECKPOINT_CSV.exists()

    success_count = 0
    error_count = 0

    with open(CHECKPOINT_CSV, 'a', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=headers)
        if write_header:
            writer.writeheader()

        for i, pdf_path in enumerate(pdfs_to_process):
            paper_id = len(processed) + i + 1
            conf, year, filename = get_paper_metadata(pdf_path)
            print(f"\n[{paper_id}/{len(all_pdfs)}] {filename} [{conf} {year}]")

            text = extract_pages(pdf_path, max_pages=15)
            if not text:
                print(f"  SKIPPED: No text extracted")
                row = {'Paper_ID': paper_id, 'Year': year, 'Conference': conf,
                       'Filename': filename,
                       **{k: '' for k in ['G1','G2','G3','G4','G5','G6','T1','Q1','Q2']},
                       'Raw_Response': '', 'Error': 'No text extracted'}
                writer.writerow(row)
                f.flush()
                error_count += 1
                continue

            print(f"  Extracted {len(text)} chars")

            raw = None
            last_error = None
            for attempt in range(MAX_RETRIES):
                try:
                    response = model.generate_content(CODING_PROMPT.format(paper_text=text))
                    
                    # Check if response was blocked
                    if response.prompt_feedback.block_reason:
                        raise ValueError(f"Response blocked: {response.prompt_feedback.block_reason}")
                    
                    # Gemini 2.5 Pro returns multi-part responses (thinking + text).
                    # Extract the actual text content from all parts.
                    try:
                        raw = response.text
                    except (ValueError, AttributeError):
                        # Multi-part response - extract text from all parts
                        if response.candidates and len(response.candidates) > 0:
                            candidate = response.candidates[0]
                            
                            # Check finish reason
                            if hasattr(candidate, 'finish_reason') and candidate.finish_reason not in [1, 'STOP']:
                                raise ValueError(f"Response finished with reason: {candidate.finish_reason}")
                            
                            parts = candidate.content.parts
                            text_parts = []
                            for p in parts:
                                if hasattr(p, 'text') and p.text:
                                    text_parts.append(p.text)
                            raw = "\n".join(text_parts)
                        else:
                            raw = ""
                    
                    if raw and len(raw.strip()) > 10:  # Need at least some content
                        break
                    else:
                        raise ValueError(f"Empty or too short response (len={len(raw) if raw else 0})")
                        
                except Exception as e:
                    last_error = e
                    print(f"  Attempt {attempt+1}/{MAX_RETRIES} failed: {e}")
                    if attempt < MAX_RETRIES - 1:
                        wait = RETRY_DELAY * (attempt + 1)
                        print(f"  Retrying in {wait}s...")
                        time.sleep(wait)

            if raw is not None:
                # Debug: print first 200 chars of raw response
                print(f"  Raw response preview: {raw[:200]}...")
                
                parsed = parse_response(raw)
                print(f"  G1={parsed['G1']}, G2={parsed['G2']}, G3={parsed['G3']}, "
                      f"G4={parsed['G4']}, G5={parsed['G5']}, G6={parsed['G6']}")

                row = {'Paper_ID': paper_id, 'Year': year, 'Conference': conf,
                       'Filename': filename, **parsed,
                       'Raw_Response': raw.replace('\n', ' | '), 'Error': ''}
                success_count += 1
            else:
                print(f"  FAILED after {MAX_RETRIES} attempts: {last_error}")
                row = {'Paper_ID': paper_id, 'Year': year, 'Conference': conf,
                       'Filename': filename,
                       **{k: '' for k in ['G1','G2','G3','G4','G5','G6','T1','Q1','Q2']},
                       'Raw_Response': '', 'Error': str(last_error)}
                error_count += 1

            writer.writerow(row)
            f.flush()
            time.sleep(DELAY_BETWEEN_REQUESTS)

            if (paper_id) % 50 == 0:
                print(f"\n  === Progress: {paper_id}/{len(all_pdfs)} | "
                      f"Success: {success_count} | Errors: {error_count} ===\n")

    # Create final clean output
    print(f"\n{'='*60}")
    print(f"Creating final output: {OUTPUT_CSV}")
    clean_headers = ['Paper_ID', 'Year', 'Conference', 'Filename',
                     'G1', 'G2', 'G3', 'G4', 'G5', 'G6', 'T1', 'Q1', 'Q2']
    with open(CHECKPOINT_CSV, 'r') as f_in, open(OUTPUT_CSV, 'w', newline='') as f_out:
        reader = csv.DictReader(f_in)
        writer = csv.DictWriter(f_out, fieldnames=clean_headers)
        writer.writeheader()
        for row in reader:
            writer.writerow({k: row[k] for k in clean_headers})

    print(f"Success: {success_count} | Errors: {error_count}")
    print(f"Results saved to: {OUTPUT_CSV}")
    print(f"{'='*60}")


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Code papers using Gemini 2.5 Pro")
    parser.add_argument('--dry-run', action='store_true',
                       help="Preview papers without calling API")
    args = parser.parse_args()
    code_papers(dry_run=args.dry_run)
