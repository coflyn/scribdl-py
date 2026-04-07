import os
import sys
import time
import random
import re
import click
import img2pdf
import configparser
import json
from datetime import datetime
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TaskProgressColumn
from rich.prompt import Prompt
from playwright.sync_api import sync_playwright

console = Console()

def load_config():
    config = configparser.ConfigParser()
    config.read('config.ini')
    defaults = {
        'delay': 3.0,
        'scale': 2,
        'output': None
    }
    if 'SETTINGS' in config:
        settings = config['SETTINGS']
        defaults['delay'] = settings.getfloat('delay', 3.0)
        defaults['scale'] = settings.getint('scale', 2)
        defaults['output'] = settings.get('output', None) or None
    return defaults

def get_filename(url, page_title):
    clean_title = "".join([c for c in page_title if c.isalnum() or c in (' ', '-', '_')]).strip()
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
@click.option('--delay', '-d', type=float, help='Delay between page scrolls (seconds)')
@click.option('--scale', '-s', type=int, help='Scaling factor (1 or 2)')
def main(url, output, pages, delay, scale):
    config_settings = load_config()
    
    if not url:
        url = Prompt.ask("[bold cyan]Input Target URL[/bold cyan]")
        
    final_delay = delay if delay is not None else config_settings['delay']
    final_scale = scale if scale is not None else config_settings['scale']
    final_output = output if output is not None else config_settings['output']

    console.print(f"\n[bold purple]scribdl-py[/bold purple] | [dim]Simple Scribd Downloader[/dim]\n", justify="center")
    
    doc_id = None
    match = re.search(r"/(?:document|presentation|doc|book|article|listen)/(\d+)", url)
    if match:
        doc_id = match.group(1)
    elif url.isdigit():
        doc_id = url
    
    if not doc_id:
        console.print("[red]Error:[/red] Invalid Scribd URL. Target document mapping failed.")
        sys.exit(1)

    embed_url = f"https://www.scribd.com/embeds/{doc_id}/content?start_page=1&view_mode=scroll"
    
    temp_dir = "temp_capture"
    if not os.path.exists(temp_dir):
        os.makedirs(temp_dir)

    with sync_playwright() as p:
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console
        ) as progress:
            launch_task = progress.add_task("[cyan]Initializing Browser Engine...", total=None)
            browser = p.chromium.launch(headless=True)
            context = browser.new_context(
                viewport={"width": 1400, "height": 2000},
                device_scale_factor=final_scale
            )
            
            context.route("**/*osano*/**", lambda route: route.abort())
            context.route("**/*analytics*/**", lambda route: route.abort())
            
            page = context.new_page()
            progress.update(launch_task, description="[cyan]Loading information from Scribd...")
            
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

            console.print(f"[dim]Title:[/dim]          [bold white]{doc_title}[/bold white]")

            try:
                page.wait_for_selector(".outer_page", timeout=15000)
            except:
                pass

            total_pages_detected = page.locator(".outer_page").count()
            if total_pages_detected == 0:
                console.print("[red]Error:[/red] No pages detected. Target might be private or restricted.")
                browser.close()
                sys.exit(1)

            console.print(f"[dim]Total Pages:[/dim]     [bold cyan]{total_pages_detected}[/bold cyan]")
        
        selected_pages_str = pages
        if not selected_pages_str:
            selected_pages_str = Prompt.ask(
                "\n[bold yellow]Select Pages[/bold yellow] [dim](example: all, 5, or 1-10)[/dim]", 
                default="all"
            )
        
        try:
            page_indices = parse_page_selection(selected_pages_str, total_pages_detected)
        except ValueError as e:
            console.print(f"[red]Error:[/red] {str(e)}")
            browser.close()
            sys.exit(1)

        image_paths = []
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
            console=console
        ) as progress:
            capture_task = progress.add_task(f"[green]Downloading pages...", total=len(page_indices))
            
            all_locators = page.locator(".outer_page")
            for idx in page_indices:
                page_element = all_locators.nth(idx)
                page_element.scroll_into_view_if_needed()
                
                time.sleep(final_delay)
                progress.update(capture_task, description=f"[green]Capturing page {idx+1}...")
                
                img_path = os.path.join(temp_dir, f"page_{idx+1}.png")
                page_element.screenshot(path=img_path)
                image_paths.append(img_path)
                progress.advance(capture_task)

            pdf_task = progress.add_task("[yellow]Saving to PDF file...", total=100)
            output_file = final_output if final_output else get_filename(url, doc_title)
            
            if not output_file.lower().endswith(".pdf"):
                output_file += ".pdf"
            
            if selected_pages_str.lower() != "all":
                clean_range = selected_pages_str.replace(' ', '')
                output_file = f"{os.path.splitext(output_file)[0]}_[{clean_range}].pdf"

            with open(output_file, "wb") as f:
                f.write(img2pdf.convert(image_paths))
            
            progress.update(pdf_task, completed=100)
            time.sleep(0.5)
            browser.close()
            
            log_history(url, doc_title, len(page_indices), output_file)
            
    for img in image_paths:
        if os.path.exists(img):
            os.remove(img)
    try:
        if not os.listdir(temp_dir):
            os.rmdir(temp_dir)
    except:
        pass
    
    console.print(f"\n[bold green]Success![/bold green] Saved as: [white]{output_file}[/white]")

if __name__ == "__main__":
    main()