#!/usr/bin/env python3
"""
Fix relative image URLs in sitemap files to absolute URLs.
This script scans all sitemap XML files and converts relative URLs to absolute URLs.
"""

import re
import os
import glob
from pathlib import Path

# Domain for absolute URLs
DOMAIN = "https://irfan.engineer"

def fix_image_urls_in_file(file_path):
    """Fix relative image URLs in a sitemap file."""
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    original_content = content
    changes_made = []
    
    # Pattern to match relative URLs in image:loc tags
    # Matches: <image:loc><![CDATA[/path/to/image.jpg]]></image:loc>
    pattern = r'(<image:loc>\s*<!\[CDATA\[)(/[^/][^\]]+)(\]\]></image:loc>)'
    
    def replace_url(match):
        prefix = match.group(1)
        relative_url = match.group(2)
        suffix = match.group(3)
        
        # Only fix if it's a relative URL (starts with /)
        if relative_url.startswith('/'):
            absolute_url = DOMAIN + relative_url
            changes_made.append(f"  - {relative_url} -> {absolute_url}")
            return prefix + absolute_url + suffix
        return match.group(0)
    
    content = re.sub(pattern, replace_url, content)
    
    if content != original_content:
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        return True, changes_made
    return False, []

def main():
    """Main function to fix all sitemap files."""
    # Find all sitemap XML files
    sitemap_files = glob.glob('*.xml') + glob.glob('**/*-sitemap.xml', recursive=True)
    
    # Filter to only actual sitemap files
    sitemap_files = [f for f in sitemap_files if 'sitemap' in f.lower() and os.path.isfile(f)]
    
    if not sitemap_files:
        print("No sitemap files found.")
        return
    
    print(f"Found {len(sitemap_files)} sitemap file(s):")
    for f in sitemap_files:
        print(f"  - {f}")
    print()
    
    total_fixed = 0
    for file_path in sitemap_files:
        print(f"Processing: {file_path}")
        fixed, changes = fix_image_urls_in_file(file_path)
        
        if fixed:
            total_fixed += 1
            print(f"  ✓ Fixed {len(changes)} URL(s):")
            for change in changes:
                print(change)
        else:
            print("  ✓ No relative URLs found (all URLs are already absolute)")
        print()
    
    if total_fixed > 0:
        print(f"✓ Successfully fixed {total_fixed} file(s)")
    else:
        print("✓ All sitemap files already have absolute URLs")

if __name__ == '__main__':
    main()

