import os
import fitz  # PyMuPDF
import re
import json
from typing import List, Dict

class PDFLoader:
    def __init__(self, raw_dir: str = "data/raw_pdfs", entity_file: str = "banned_entities.json"):
        self.raw_dir = raw_dir
        
        # 1. LOAD PRIVATE ENTITY LIST (Hidden from GitHub)
        self.BANNED_ENTITIES = self._load_banned_entities(entity_file)

        # 2. STOP MARKERS (Generic, safe to share)
        self.LEGAL_STOP_MARKERS = [
            "Disclosure Appendix", "Important Disclosures", "Analyst Certification",
            "Appendix A: Disclosure", "Legal Disclaimer", "Investment Banking Services",
            "General Disclosures", "Regulatory Disclosures", "Investment Risks", 
            "Risk Factors", "You received this message because", 
            "Unsubscribe |", "Manage your newsletter subscriptions", 
            "Want to sponsor this newsletter?", "Ads powered by"
        ]
        
        # 3. NOISE PATTERNS (Generic, safe to share)
        self.NOISE_PATTERNS = [
            r"Page \d+ of \d+", r"Copyright \d{4}", r"All rights reserved",
            r"Strictly Private & Confidential", r"From: .*@.*", r"To: .*@.*",
            r"Subject: .*", r"View in browser", r"Like getting this newsletter\?",
            r"Subscribe to .*", r"Before it’s here, it’s on the .*", r"Sent from my iPhone",
            r"For the exclusive use of", r"Source: \w+ Research", r"Download the \w+ app"
        ]

    def _load_banned_entities(self, filepath: str) -> List[str]:
        """Loads sensitive names from a private JSON file ignored by Git."""
        if os.path.exists(filepath):
            try:
                with open(filepath, 'r') as f:
                    return json.load(f)
            except Exception as e:
                print(f"⚠️ Warning: Could not parse {filepath}: {e}")
                return []
        else:
            print(f"ℹ️ Note: {filepath} not found. Running without entity redaction.")
            return []

    def load_documents(self) -> List[Dict]:
        """Scans folder, cleans text, redacts entities, and returns content."""
        documents = []
        if not os.path.exists(self.raw_dir):
            os.makedirs(self.raw_dir)
            print(f"📁 Created {self.raw_dir}. Drop research PDFs here.")
            return []

        files = [f for f in os.listdir(self.raw_dir) if f.lower().endswith(".pdf")]
        
        if not files:
            print(f"⚠️ No PDFs found in {self.raw_dir}")
            return []

        print(f"📄 Found {len(files)} PDFs. Processing with Redaction...")

        for filename in files:
            path = os.path.join(self.raw_dir, filename)
            try:
                # 1. Extract Raw Text
                raw_text = self._extract_text(path)
                
                # 2. Structural Cleaning (Cut disclaimers, headers)
                clean_text = self._remove_legal_bloat(raw_text)
                
                # 3. Entity Redaction (The "Clean Room" scrub)
                final_text = self._redact_entities(clean_text)
                
                # Metrics
                reduction = 1 - (len(final_text) / len(raw_text)) if len(raw_text) > 0 else 0
                doc_type = "newsletter" if "newsletter" in filename.lower() else "sellside_research"

                documents.append({
                    "source": filename,
                    "content": final_text,
                    "type": doc_type,
                    # This is the key your main.py was looking for:
                    "boilerplate_removed_pct": f"{reduction:.1%}" 
                })
                print(f"   ✅ Loaded & Anonymized: {filename}")
                
            except Exception as e:
                print(f"   ❌ Failed to load {filename}: {e}")
                
        return documents

    def _extract_text(self, filepath: str) -> str:
        doc = fitz.open(filepath)
        text_blocks = []
        for page in doc:
            text_blocks.append(page.get_text())
        return "\n".join(text_blocks)

    def _remove_legal_bloat(self, text: str) -> str:
        lines = text.split('\n')
        cleaned_lines = []
        stop_triggered = False
        
        for line in lines:
            line_strip = line.strip()
            
            # Check Stop Markers
            for marker in self.LEGAL_STOP_MARKERS:
                if marker.lower() in line_strip.lower() and len(line_strip) < 100:
                    stop_triggered = True
                    break
            if stop_triggered: break 
            
            # Check Noise Patterns
            is_noise = False
            for pattern in self.NOISE_PATTERNS:
                if re.search(pattern, line_strip, re.IGNORECASE):
                    is_noise = True
                    break
            
            if not is_noise and line_strip:
                cleaned_lines.append(line_strip)
                
        return "\n".join(cleaned_lines)

    def _redact_entities(self, text: str) -> str:
        """Replaces sensitive bank names and authors with generic placeholders."""
        if not self.BANNED_ENTITIES:
            return text
            
        redacted_text = text
        for entity in self.BANNED_ENTITIES:
            pattern = re.compile(re.escape(entity), re.IGNORECASE)
            redacted_text = pattern.sub("[REDACTED_ENTITY]", redacted_text)
        return redacted_text

if __name__ == "__main__":
    loader = PDFLoader()
    docs = loader.load_documents()