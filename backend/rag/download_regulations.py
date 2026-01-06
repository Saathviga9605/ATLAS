"""
Utility script to download all regulatory PDFs
Run this once to download all sources, then use them in the main agent
"""

import os
from regulation_intelligence_agent import (
    RegulationIntelligenceAgent, 
    REGULATORY_SOURCES,
    DocumentProcessor,
    Config
)

def download_all_regulations():
    """Download all regulatory PDFs from sources"""
    print("\n" + "="*70)
    print("REGULATORY PDF DOWNLOADER")
    print("="*70)
    print(f"\nWill download {len(REGULATORY_SOURCES)} regulatory documents")
    print(f"Save location: {Config.DATA_DIR}\n")
    
    processor = DocumentProcessor()
    
    # Track success/failure
    success = []
    failed = []
    
    # Download each source
    for i, (key, source) in enumerate(REGULATORY_SOURCES.items(), 1):
        print(f"\n[{i}/{len(REGULATORY_SOURCES)}] {key}")
        print(f"  Name: {source['name']}")
        print(f"  URL: {source['url'][:80]}...")
        
        filepath = processor.download_pdf(source['url'], source['local_path'])
        
        if filepath:
            success.append(key)
        else:
            failed.append(key)
    
    # Summary
    print("\n" + "="*70)
    print("DOWNLOAD SUMMARY")
    print("="*70)
    print(f"\n✓ Successfully downloaded: {len(success)}/{len(REGULATORY_SOURCES)}")
    for key in success:
        print(f"  ✓ {key}")
    
    if failed:
        print(f"\n✗ Failed downloads: {len(failed)}")
        for key in failed:
            print(f"  ✗ {key}")
        print("\nNote: Some sources require manual download or web scraping")
    
    print(f"\nFiles saved to: {Config.DATA_DIR}")
    print("\nNext steps:")
    print("  1. Run: agent.setup(download_pdfs=True) to process PDFs")
    print("  2. Or manually move PDFs to regulatory_data/ folder")


def download_priority_only():
    """Download only Visa + PCI-DSS + GDPR (for hackathon speed)"""
    print("\n" + "="*70)
    print("PRIORITY REGULATORY PDF DOWNLOADER")
    print("="*70)
    print("\nDownloading: Visa Rules + PCI-DSS + GDPR only\n")
    
    processor = DocumentProcessor()
    
    priority = ["VISA_CORE_RULES", "PCI_DSS", "GDPR", 
                "VISA_MERCHANT_DATA_STANDARDS", "VISA_GLOBAL_ACQUIRER_RISK_STANDARDS"]
    
    for key in priority:
        if key in REGULATORY_SOURCES:
            source = REGULATORY_SOURCES[key]
            print(f"\n[{key}]")
            print(f"  {source['name']}")
            processor.download_pdf(source['url'], source['local_path'])
    
    print("\n✓ Priority downloads complete!")


def list_all_sources():
    """List all available regulatory sources"""
    print("\n" + "="*70)
    print("AVAILABLE REGULATORY SOURCES")
    print("="*70)
    
    categories = {
        "VISA": [],
        "PCI": [],
        "GDPR": [],
        "INDIA": [],
        "UK": [],
        "USA": []
    }
    
    for key, source in REGULATORY_SOURCES.items():
        if "VISA" in key or "INTERLINK" in key:
            categories["VISA"].append((key, source['name']))
        elif "PCI" in key:
            categories["PCI"].append((key, source['name']))
        elif "GDPR" in key:
            categories["GDPR"].append((key, source['name']))
        elif "INDIA" in key or "RBI" in key or "SEBI" in key:
            categories["INDIA"].append((key, source['name']))
        elif "FCA" in key:
            categories["UK"].append((key, source['name']))
        elif "SEC" in key or "CFR" in key:
            categories["USA"].append((key, source['name']))
    
    for category, items in categories.items():
        if items:
            print(f"\n{category} REGULATIONS ({len(items)}):")
            for key, name in items:
                print(f"  • {key}: {name}")


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        command = sys.argv[1]
        
        if command == "all":
            download_all_regulations()
        elif command == "priority":
            download_priority_only()
        elif command == "list":
            list_all_sources()
        else:
            print(f"Unknown command: {command}")
            print("\nUsage:")
            print("  python download_regulations.py all       # Download all regulations")
            print("  python download_regulations.py priority  # Download Visa + PCI + GDPR only")
            print("  python download_regulations.py list      # List all sources")
    else:
        print("="*70)
        print("REGULATORY PDF DOWNLOADER")
        print("="*70)
        print("\nUsage:")
        print("  python download_regulations.py all       # Download all regulations")
        print("  python download_regulations.py priority  # Download Visa + PCI + GDPR only")
        print("  python download_regulations.py list      # List all sources")
        print("\nRecommended for hackathon: priority (faster, focused)")