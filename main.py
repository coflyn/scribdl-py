import os
import sys
import time
import re
import click
import img2pdf
import configparser
import json
import tempfile
import atexit
from datetime import datetime
from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeoutError

def load_config():
    config = configparser.ConfigParser()
    config.read('config.ini')
    defaults = {
        'delay': 0.5,
        'scale': 2,
        'output': None
    }
    if 'SETTINGS' in config:
        settings = config['SETTINGS']
        defaults['delay'] = settings.getfloat('delay', 0.5)
        defaults['scale'] = settings.getint('scale', 2)
        defaults['output'] = settings.get('output', None) or None
    return defaults

def get_filename(url, page_title):
    clean_title = re.sub(r'[<>:"/\\|?*]', '', page_title)
    clean_title = clean_title.strip('. ')
    if not clean_title:
        clean_title = "Document"
    return f"{clean_title}.pdf"

def parse_page_selection(selection_str, total_pages):
    selection_str = selection_str.lower().strip()
    
    if selection_str == 'all' or not selection_str:
        return list(range(total_pages))
    
    selected_indices = set()
    
    try:
        parts = [p.strip() for p in selection_str.split(',')]
        
        for part in parts:
            if '-' in part:
                start, end = map(int, part.split('-'))
                if start < 1 or end > total_pages or start > end:
                    raise ValueError(f"Range {start}-{end} is out of document bounds (1-{total_pages}).")
                for i in range(start - 1, end):
                    selected_indices.add(i)
            else:
                p_num = int(part)
                if p_num < 1 or p_num > total_pages:
                    raise ValueError(f"Page number {p_num} is out of document bounds (1-{total_pages}).")
                selected_indices.add(p_num - 1)
        
        return sorted(list(selected_indices))
        
    except ValueError as e:
        if "out of document bounds" in str(e):
            raise e
        raise ValueError("Invalid format. Use 'all', a single number (e.g. 3), or range (e.g. 1-10).")

def log_history(url, title, pages_count, output_file):
    history_file = "history.json"
    history = []
    
    if os.path.exists(history_file):
        try:
            with open(history_file, 'r') as f:
                history = json.load(f)
        except (json.JSONDecodeError, IOError):
            history = []
            
    new_entry = {
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "title": title,
        "url": url,
        "pages": pages_count,
        "output": output_file
    }
    
    history.append(new_entry)
    
    with open(history_file, 'w') as f:
        json.dump(history, f, indent=4)

@click.command()
@click.argument('url', required=False)
@click.option('--output', '-o', help='Output filename')
@click.option('--pages', '-p', help='Page range (e.g. "all", "3", or "1-10")')
@click.option('--delay', '-d', type=float, help='Extra delay between page scrolls (seconds)')
@click.option('--scale', '-s', type=int, help='Scaling factor (1 or 2)')
@click.option('--quiet', '-q', is_flag=True, help='Disable progress output')
def main(url, output, pages, delay, scale, quiet):
    config_settings = load_config()
    
    if not url:
        try:
            url = input("Enter target URL: ")
        except (KeyboardInterrupt, EOFError):
            sys.exit(0)
        
    url = url.strip().strip("'\"")
    if not url:
        print("Error: Target URL is required.")
        sys.exit(1)
    
    final_delay = delay if delay is not None else config_settings['delay']
    final_scale = scale if scale is not None else config_settings['scale']
    final_output = output if output is not None else config_settings['output']

    doc_id = None
    match = re.search(r"/(?:document|presentation|doc|book|article|listen)/(\d+)", url)
    if match:
        doc_id = match.group(1)
    elif url.isdigit():
        doc_id = url
    
    if not doc_id:
        print("Error: Invalid Scribd URL.")
        sys.exit(1)

    embed_url = f"https://www.scribd.com/embeds/{doc_id}/content?start_page=1&view_mode=scroll"
    
    temp_dir_obj = tempfile.TemporaryDirectory(prefix="scribdl_")
    temp_dir = temp_dir_obj.name
    atexit.register(temp_dir_obj.cleanup)

    with sync_playwright() as p:
        if not quiet:
            print("Connecting to Scribd...")
        
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            viewport={"width": 1400, "height": 2000},
            device_scale_factor=final_scale
        )
        
        context.route("**/*osano*/**", lambda route: route.abort())
        context.route("**/*analytics*/**", lambda route: route.abort())
        
        page = context.new_page()
        page.goto(embed_url, wait_until="domcontentloaded", timeout=60000)
        
        from urllib.parse import unquote
        
        clean_url = url.split('#')[0].split('?')[0]
        url_slug = clean_url.rstrip('/').split('/')[-1]
        url_title = unquote(url_slug).replace('-', ' ').replace('_', ' ').title()
        
        doc_title = page.evaluate("""() => {
            const ogTitle = document.querySelector('meta[property="og:title"]')?.content;
            if (ogTitle && ogTitle.toLowerCase() !== 'scribd') return ogTitle;
            const internalTitle = document.querySelector('.title_text, .doc_title')?.innerText;
            return internalTitle || "";
        }""")
        
        if not doc_title:
            doc_title = url_title or page.title().replace(' | Scribd', '').strip()

        doc_title = "".join([c for c in doc_title if c.isalnum() or c in (' ', '-', '_')]).strip()
        if not doc_title or doc_title.lower() == 'scribd':
             doc_title = "Archived_Document"

        try:
            page.wait_for_selector(".outer_page", timeout=15000)
        except PlaywrightTimeoutError:
            pass

        total_pages_detected = page.locator(".outer_page").count()
        if total_pages_detected == 0:
            print("Error: No pages detected. Target document might be private or restricted.")
            browser.close()
            sys.exit(1)

        if not quiet:
            print(f"Document : {doc_title}")
            print(f"Pages    : {total_pages_detected}")
    
        selected_pages_str = pages
        if not selected_pages_str:
            try:
                selected_pages_str = input("Pages to download [all]: ").strip()
            except (KeyboardInterrupt, EOFError):
                browser.close()
                sys.exit(0)
            if not selected_pages_str:
                selected_pages_str = "all"
        
        try:
            page_indices = parse_page_selection(selected_pages_str, total_pages_detected)
        except ValueError as e:
            print(f"Error: {str(e)}")
            browser.close()
            sys.exit(1)

        image_paths = []
        total_selected = len(page_indices)
        all_locators = page.locator(".outer_page")
        
        bar_length = 20
        spinner_chars = ['|', '/', '-', '\\']
        for idx_count, idx in enumerate(page_indices, start=1):
            page_element = all_locators.nth(idx)
            page_element.scroll_into_view_if_needed()
            
            try:
                img_loc = page_element.locator("img, canvas, .absimg").first
                if img_loc.count() > 0:
                    img_loc.wait_for(state="visible", timeout=5000)
                    page.evaluate("""(elem) => {
                        const img = elem.querySelector('img');
                        if (img && !img.complete) {
                            return new Promise(resolve => {
                                img.onload = resolve;
                                img.onerror = resolve;
                                setTimeout(resolve, 3000);
                            });
                        }
                    }""", page_element.element_handle())
            except PlaywrightTimeoutError:
                pass
            
            if final_delay > 0:
                time.sleep(final_delay)
                
            img_path = os.path.join(temp_dir, f"page_{idx+1}.png")
            page_element.screenshot(path=img_path)
            image_paths.append(img_path)

            if not quiet:
                percent = int((idx_count / total_selected) * 100)
                filled = int(bar_length * (idx_count / total_selected))
                bar = '#' * filled + '.' * (bar_length - filled)
                spinner = spinner_chars[idx_count % len(spinner_chars)]
                sys.stdout.write(f"\r[{spinner}] Downloading page {idx_count}/{total_selected} [{bar}] {percent}%")
                sys.stdout.flush()

        if not quiet:
            print("\n[+] Converting to PDF...")

        output_file = final_output if final_output else get_filename(url, doc_title)
        
        if not output_file.lower().endswith(".pdf"):
            output_file += ".pdf"
        
        if selected_pages_str.lower() != "all":
            clean_range = selected_pages_str.replace(' ', '')
            output_file = f"{os.path.splitext(output_file)[0]}_[{clean_range}].pdf"

        if not os.path.isabs(output_file) and not os.path.dirname(output_file):
            os.makedirs("output", exist_ok=True)
            output_file = os.path.join("output", output_file)

        with open(output_file, "wb") as f:
            f.write(img2pdf.convert(image_paths))
        
        browser.close()
        log_history(url, doc_title, len(page_indices), output_file)
            
    try:
        temp_dir_obj.cleanup()
        atexit.unregister(temp_dir_obj.cleanup)
    except Exception:
        pass
    
    if not quiet:
        print(f"[✓] Saved: {output_file}")

if __name__ == "__main__":
    main()