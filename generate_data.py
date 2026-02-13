import re
import json
import os

def slugify(text):
    # Remove non-ascii
    text = re.sub(r'[^\x00-\x7f]', '', text)
    # Lowercase
    text = text.lower()
    # Replace non-alphanumeric with hyphen
    text = re.sub(r'[^a-z0-9]+', '-', text)
    # Strip leading/trailing hyphens
    text = text.strip('-')
    return text

def parse_markdown(markdown_text, item_links):
    data = {"version": 1, "items": []}
    lines = markdown_text.split('\n')
    
    current_section = None
    current_subsection = None
    item_index = 0 # To map to item_links
    
    # ID tracking to avoid duplicates
    seen_ids = set()

    def get_unique_id(text, context_prefix=""):
        base_id = slugify(text)
        if not base_id:
            base_id = "item"
        
        # Add context if provided (e.g. 'language-')
        if context_prefix:
             base_id = f"{context_prefix}-{base_id}"
             
        candidate = base_id
        counter = 1
        while candidate in seen_ids:
            candidate = f"{base_id}-{counter}"
            counter += 1
        seen_ids.add(candidate)
        return candidate

    section_prefix = ""

    for line in lines:
        line = line.strip()
        if not line or line == '-----':
            continue
            
        # Section
        match = re.match(r'^## \d+\.\s+(.*)', line)
        if match:
            title = match.group(0).replace('## ', '') # Keep the numbering for display
            # Generate a prefix for IDs in this section
            raw_title = match.group(1) # "语言 Language..."
            section_prefix = slugify(raw_title.split(' ')[1] if ' ' in raw_title else raw_title)
            # Shorten common prefixes
            if 'language' in section_prefix: section_prefix = 'lang'
            if 'digital' in section_prefix: section_prefix = 'digital'
            if 'culture' in section_prefix: section_prefix = 'culture'
            
            current_section = {
                "title": title,
                "items": []
            }
            data["items"].append(current_section)
            current_subsection = None
            continue
            
        # Subsection
        match = re.match(r'^###\s+(.*)', line)
        if match:
            title = match.group(1)
            current_subsection = {
                "title": title,
                "items": []
            }
            if current_section:
                current_section["items"].append(current_subsection)
            continue
            
        # Item
        match = re.match(r'^-\s+\[\s*\]\s+(.*)', line)
        if match:
            text_content = match.group(1)
            # Handle recursive items (indented) - The regex above catches top level
            # But wait, logic in original js handled indent.
            # For simplicity in this flat markdown structure:
            
            # Let's handle indent by checking original line
            indent = len(line) - len(line.lstrip())
            # In the original, indent-1 was 22px (roughly 2 spaces in code? No, ` - ` is 3)
            # Let's just assume flat for now or use the indent to nest?
            # The simplified data structure supports nesting.
            
            item_id = get_unique_id(text_content, section_prefix)
            
            item = {
                "id": item_id,
                "text": text_content
            }
            
            # Check for link
            if item_index in item_links:
                item["link"] = item_links[item_index]
            
            # Handle blockquotes inside items? No, blockquotes were separate.
            
            # Logic for nesting:
            # If I am indented more than the previous item, I am a child of it.
            # Simplified approach: If it's a sub-item (indent > 0), add to previous item's 'items' array.
            # But the original JS flattened visual indent.
            # Let's keep it simple: Add to current container.
            
            container_list = current_subsection["items"] if current_subsection else (current_section["items"] if current_section else data["items"])
            
            # Check if this is a nested item (sub-task)
            # Original: indent-1 or indent-2
            # Markdown: `  - [ ]`
            
            is_nested = line.startswith('- [ ]') == False # If it has leading spaces logic
            # Actually line is stripped above.
            # We need the original line.
            
            # Let's re-read line with indent
            # But I stripped it. Reworking loop slightly.
            pass

    # RE-DO Loop with correct indent handling
    data = {"version": 1, "items": []}
    lines = markdown_text.split('\n')
    current_section = None
    current_subsection = None
    last_item = None # For nesting
    current_indent_level = 0
    item_index = 0
    seen_ids = set()
    section_prefix = "item"

    for line_raw in lines:
        line = line_raw.strip()
        if not line or line == '-----': continue
        
        # Section
        if line.startswith('## '):
            title = line.replace('## ', '')
            section_prefix = slugify(title.split(' ')[1]) if ' ' in title else slugify(title)
            # Aliases for shorter IDs
            if 'language' in section_prefix: section_prefix = 'lang'
            elif 'digital' in section_prefix: section_prefix = 'digi'
            elif 'culture' in section_prefix: section_prefix = 'cult'
            elif 'political' in section_prefix: section_prefix = 'pol'
            elif 'film' in section_prefix: section_prefix = 'film'
            elif 'music' in section_prefix: section_prefix = 'music'
            elif 'literature' in section_prefix: section_prefix = 'lit'
            elif 'online' in section_prefix: section_prefix = 'web'
            elif 'food' in section_prefix: section_prefix = 'food'
            elif 'style' in section_prefix: section_prefix = 'style'
            elif 'travel' in section_prefix: section_prefix = 'travel'
            elif 'social' in section_prefix: section_prefix = 'social'
            elif 'fitness' in section_prefix: section_prefix = 'fit'
            elif 'investment' in section_prefix: section_prefix = 'invest'
            elif 'career' in section_prefix: section_prefix = 'biz'
            elif 'electronics' in section_prefix: section_prefix = 'tech'
            elif 'ai' in section_prefix: section_prefix = 'ai'
            elif 'challenge' in section_prefix: section_prefix = 'bucket'

            current_section = {"title": title, "items": []}
            data["items"].append(current_section)
            current_subsection = None
            last_item = None
            continue
            
        # Subsection
        if line.startswith('### '):
            title = line.replace('### ', '')
            current_subsection = {"title": title, "items": []}
            current_section["items"].append(current_subsection)
            last_item = None
            continue
            
        # Checklist Item
        if '- [ ]' in line:
            # Calculate indent
            indent = len(line_raw) - len(line_raw.lstrip())
            text_content = line.split('- [ ]', 1)[1].strip()
            
            # Clean text (remove bolding markdown for ID generation)
            clean_text = text_content.replace('**', '')
            
            item_id = get_unique_id(clean_text, section_prefix)
            
            new_item = {
                "id": item_id,
                "text": text_content
            }
            if item_index in item_links:
                new_item["link"] = item_links[item_index]
            
            # Determine placement based on indent
            # Base indent for top-level item in markdown list is 0
            # Indented item is usually 2 or 4 spaces
            
            if indent > 0 and last_item:
                # Add as child of last item
                if "items" not in last_item:
                    last_item["items"] = []
                last_item["items"].append(new_item)
            else:
                # Add to current container
                target = current_subsection["items"] if current_subsection else current_section["items"]
                target.append(new_item)
                last_item = new_item
            
            item_index += 1
            continue
            
        # Blockquote
        if line.startswith('> '):
            text = line.replace('> ', '').strip()
            # Add as a special item type
            target = current_section["items"] if current_section else data["items"]
            target.append({"type": "blockquote", "text": text})
            
    return data

def main():
    with open('index.html', 'r', encoding='utf-8') as f:
        content = f.read()
        
    # Extract Markdown
    md_start = content.find('const markdownContent = `') + len('const markdownContent = `')
    md_end = content.find('`;', md_start)
    markdown_text = content[md_start:md_end]
    
    # Extract Item Links
    links_start = content.find('const itemLinks = {')
    links_end = content.find('};', links_start) + 1
    links_block = content[links_start:links_end]
    
    # Parse links securely-ish (it's valid JS object syntax, nearly JSON but keys aren't quoted sometimes)
    # Actually keys are numbers.
    # We can parse it by stripping comments and wrapping in {}
    item_links = {}
    
    # Manual parsing of the links object body
    # Remove 'const itemLinks = {' and '};'
    links_body = links_block[links_block.find('{')+1 : links_block.rfind('}')]
    
    for line in links_body.split('\n'):
        line = line.strip()
        if not line or line.startswith('//'): continue
        
        # Match: 0: 'url',
        match = re.match(r"(\d+):\s*'([^']+)'", line)
        if match:
            idx = int(match.group(1))
            url = match.group(2)
            item_links[idx] = url
            
    # Generate Data
    data = parse_markdown(markdown_text, item_links)
    
    # Ensure assets/js exists
    os.makedirs('assets/js', exist_ok=True)
    
    # Write to file
    with open('assets/js/data.js', 'w', encoding='utf-8') as f:
        f.write('export const checklistData = ')
        json.dump(data, f, indent=2, ensure_ascii=False)
        f.write(';')
        
    print("Successfully generated assets/js/data.js")

if __name__ == '__main__':
    main()
