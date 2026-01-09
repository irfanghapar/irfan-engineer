#!/usr/bin/env python3
"""
Fix relative image URLs in HTML files to absolute URLs.
This script scans all HTML files and converts relative image URLs to absolute URLs
in meta tags, structured data (JSON-LD), and other places.
"""

import re
import os
import glob
import json

# Domain for absolute URLs
DOMAIN = "https://irfan.engineer"

def fix_json_ld_urls(content):
    """Fix relative URLs in JSON-LD structured data."""
    # Pattern to match JSON-LD script tags
    pattern = r'(<script[^>]*type=["\']application/ld\+json["\'][^>]*>)(.*?)(</script>)'
    
    def fix_json_content(match):
        script_start = match.group(1)
        json_content = match.group(2)
        script_end = match.group(3)
        
        try:
            # Try to parse and fix the JSON
            data = json.loads(json_content)
            
            def fix_urls_in_obj(obj):
                if isinstance(obj, dict):
                    for key, value in obj.items():
                        if key == 'url' and isinstance(value, str) and value.startswith('/'):
                            obj[key] = DOMAIN + value
                        elif key == 'image' and isinstance(value, dict) and 'url' in value:
                            if isinstance(value['url'], str) and value['url'].startswith('/'):
                                value['url'] = DOMAIN + value['url']
                        else:
                            fix_urls_in_obj(value)
                elif isinstance(obj, list):
                    for item in obj:
                        fix_urls_in_obj(item)
            
            fix_urls_in_obj(data)
            fixed_json = json.dumps(data, ensure_ascii=False)
            return script_start + fixed_json + script_end
        except:
            # If JSON parsing fails, try regex replacement
            fixed_json = re.sub(
                r'("url"\s*:\s*")(/[^"]+)(")',
                lambda m: m.group(1) + DOMAIN + m.group(2) + m.group(3),
                json_content
            )
            return script_start + fixed_json + script_end
    
    return re.sub(pattern, fix_json_content, content, flags=re.DOTALL)

def fix_meta_tag_urls(content):
    """Fix relative URLs in meta tags (og:image, twitter:image, etc.)."""
    # Pattern for meta tags with content attributes
    patterns = [
        (r'(<meta[^>]*property=["\'](og:image|twitter:image|msapplication-TileImage)["\'][^>]*content=["\'])(/[^"\']+)(["\'][^>]*>)', 'meta property'),
        (r'(<meta[^>]*name=["\'](og:image|twitter:image|msapplication-TileImage)["\'][^>]*content=["\'])(/[^"\']+)(["\'][^>]*>)', 'meta name'),
    ]
    
    changes = []
    for pattern, tag_type in patterns:
        def replace_url(match):
            prefix = match.group(1)
            relative_url = match.group(2)
            suffix = match.group(3)
            
            if relative_url.startswith('/') and not relative_url.startswith('//'):
                absolute_url = DOMAIN + relative_url
                changes.append(f"  - {tag_type}: {relative_url} -> {absolute_url}")
                return prefix + absolute_url + suffix
            return match.group(0)
        
        content = re.sub(pattern, replace_url, content)
    
    return content, changes

def fix_html_file(file_path):
    """Fix relative image URLs in an HTML file."""
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    original_content = content
    all_changes = []
    
    # Fix JSON-LD structured data
    content = fix_json_ld_urls(content)
    
    # Fix meta tags
    content, meta_changes = fix_meta_tag_urls(content)
    all_changes.extend(meta_changes)
    
    if content != original_content:
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        return True, all_changes
    return False, []

def main():
    """Main function to fix all HTML files."""
    # Find all HTML files
    html_files = glob.glob('*.html') + glob.glob('**/*.html', recursive=True)
    html_files = [f for f in html_files if os.path.isfile(f)]
    
    if not html_files:
        print("No HTML files found.")
        return
    
    print(f"Found {len(html_files)} HTML file(s)")
    print()
    
    total_fixed = 0
    for file_path in html_files:
        fixed, changes = fix_html_file(file_path)
        
        if fixed:
            total_fixed += 1
            print(f"✓ Fixed: {file_path}")
            for change in changes:
                print(change)
            print()
    
    if total_fixed > 0:
        print(f"✓ Successfully fixed {total_fixed} file(s)")
    else:
        print("✓ All HTML files already have absolute URLs")

if __name__ == '__main__':
    main()

