import urllib.request
import xml.etree.ElementTree as ET
import os
import duckdb
from datetime import datetime, timezone
import hashlib
import re

class NewsRSSIngestor:
    def __init__(self, db_path: str = "data/duckdb/intelligence.duckdb", raw_dir: str = "data/raw/news"):
        self.db_path = db_path
        self.raw_dir = raw_dir
        self.feed_url = "https://www.cnbcindonesia.com/market/rss"
        self.source_id = "INFO_RSS_CNBC_ID"
        self.source_name = "CNBC Indonesia RSS"
        
        # Static list of pilot tickers for simple heuristic linkage
        self.pilot_tickers = ["BBCA", "BBRI", "BMRI", "BBNI", "TLKM", "ASII", "PTBA", "ADRO", "ITMG", "UNTR", "ANTM", "INCO"]
        
        os.makedirs(self.raw_dir, exist_ok=True)
        
    def _parse_pubdate(self, pubdate_str: str) -> str:
        # e.g., "Mon, 14 Sep 2026 09:21:53 +0700"
        try:
            # We will use simple datetime parsing and convert to UTC ISO string
            dt = datetime.strptime(pubdate_str, "%a, %d %b %Y %H:%M:%S %z")
            return dt.astimezone(timezone.utc).isoformat()
        except Exception:
            return datetime.now(timezone.utc).isoformat() # Fallback if parsing fails

    def _extract_entity(self, title: str, description: str) -> str:
        text = f"{title} {description}".upper()
        # Find all matching tickers
        matches = [t for t in self.pilot_tickers if re.search(r'\b' + t + r'\b', text)]
        if len(matches) == 1:
            return f"ENT_{matches[0]}"
        elif len(matches) > 1:
            return "MULTIPLE_POSSIBLE"
        return "UNRESOLVED"

    def ingest_rss(self):
        req = urllib.request.Request(self.feed_url, headers={'User-Agent': 'Mozilla/5.0'})
        retrieved_at = datetime.now(timezone.utc)
        retrieved_at_iso = retrieved_at.isoformat()
        
        try:
            response = urllib.request.urlopen(req)
            xml_data = response.read()
        except Exception as e:
            print(f"Failed to fetch RSS: {e}")
            return
            
        # Save raw evidence
        date_str = retrieved_at.strftime("%Y%m%d_%H%M%S")
        raw_file = os.path.join(self.raw_dir, f"cnbc_{date_str}.xml")
        with open(raw_file, "wb") as f:
            f.write(xml_data)
            
        try:
            root = ET.fromstring(xml_data)
        except Exception as e:
            print(f"Failed to parse XML: {e}")
            return
            
        con = duckdb.connect(self.db_path)
        total_ingested = 0
        
        for item in root.findall('.//item'):
            title = item.find('title').text or ""
            link = item.find('link').text or ""
            description = item.find('description').text or ""
            pubDate = item.find('pubDate').text or ""
            
            published_at = self._parse_pubdate(pubDate)
            information_available_at = published_at
            
            # Generate stable ID based on link
            content_hash = hashlib.md5(link.encode('utf-8')).hexdigest()
            event_id = f"EVT_NEWS_{content_hash}"
            
            entity_id = self._extract_entity(title, description)
            
            # Upsert
            con.execute("""
                INSERT INTO fact_event (
                    event_id, event_type, event_subtype, 
                    entity_id, entity_type, 
                    event_timestamp, published_at, information_available_at, observed_at, retrieved_at,
                    valid_from, valid_to,
                    source_id, source_name, source_url, source_quality, source_type,
                    raw_reference, provenance,
                    information_state, information_delta,
                    materiality, relevance, confidence,
                    is_pit_valid, status
                ) VALUES (
                    ?, ?, ?,
                    ?, ?,
                    ?, ?, ?, ?, ?,
                    ?, NULL,
                    ?, ?, ?, ?, ?,
                    ?, ?,
                    ?, ?,
                    ?, ?, ?,
                    ?, ?
                ) ON CONFLICT (event_id) DO NOTHING;
            """, (
                event_id, 'NEWS_INFORMATION', 'ARTICLE',
                entity_id if entity_id.startswith('ENT_') else None, 'COMPANY' if entity_id.startswith('ENT_') else None,
                published_at, published_at, information_available_at, retrieved_at_iso, retrieved_at_iso,
                published_at, # valid_from
                self.source_id, self.source_name, link, 'MEDIUM', 'reputable news',
                title, 'REAL',
                'DETECTED', 'NEW',
                'UNKNOWN', 'UNKNOWN', 0.8,
                True, 'ACTIVE'
            ))
            total_ingested += 1
            
        con.close()
        print(f"Ingested {total_ingested} news events from RSS.")
        return total_ingested

if __name__ == "__main__":
    ingestor = NewsRSSIngestor()
    ingestor.ingest_rss()
