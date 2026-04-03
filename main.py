import os
import sys
import time
import random
import re
import click
import img2pdf
import configparser
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TaskProgressColumn
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

@click.command()
@click.argument('url')
@click.option('--output', '-o', help='Output filename')
@click.option('--delay', '-d', type=float, help='Delay between page scrolls (seconds)')
@click.option('--scale', '-s', type=int, help='Scaling factor (1 or 2)')
def main(url, output, delay, scale):
    config_settings = load_config()
    
    final_delay = delay if delay is not None else config_settings['delay']
    final_scale = scale if scale is not None else config_settings['scale']
    final_output = output if output is not None else config_settings['output']

    console.print(f"\n[bold purple]scribdl-py[/bold purple] | [dim]Archive Engine[/dim]\n", justify="center")
    
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
            BarColumn(),
            TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
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
            progress.update(launch_task, description="[cyan]Connecting to Scribd Data Matrix...")
            
            page.goto(embed_url, wait_until="domcontentloaded", timeout=60000)
            
            from urllib.parse import unquote
            
            clean_url = url.split('#')[0].split('?')[0]
            url_slug = clean_url.rstrip('/').split('/')[-1]
            url_title = unquote(url_slug).replace('-', ' ').replace('_', ' ').title()
            
            doc_title = page.evaluate("""() => {
                const ogTitle = document.querySelector('meta[property="og:title"]')?.content;
                if (ogTitle && ogTitle.toLowerCase() !== 'scribd') return ogTitle;
                
                const internalTitle = document.querySelector('.title_text, .doc_title')?.innerText;
                if (internalTitle) return internalTitle;
                
                return "";
            }""")
            
            if not doc_title:
                doc_title = url_title or page.title().replace(' | Scribd', '').strip()

            doc_title = "".join([c for c in doc_title if c.isalnum() or c in (' ', '-', '_')]).strip()
            
            if not doc_title or doc_title.lower() == 'scribd':
                 doc_title = "Archived_Document"

            console.print(f"[dim]Pub Title:[/dim]      [bold white]{doc_title}[/bold white]")

            try:
                page.wait_for_selector(".outer_page", timeout=15000)
            except:
                pass

            pages = page.locator(".outer_page")
            page_count = pages.count()
            
            if page_count == 0:
                console.print("[red]Error:[/red] No pages detected. Target might be private or restricted.")
                browser.close()
                sys.exit(1)

            console.print(f"[dim]Total Pages:[/dim]     [bold cyan]{page_count}[/bold cyan]")
            progress.remove_task(launch_task)
            capture_task = progress.add_task(f"[green]Capturing high-res renders...", total=page_count)
            
            image_paths = []
            for i in range(page_count):
                page_element = pages.nth(i)
                page_element.scroll_into_view_if_needed()
                
                time.sleep(final_delay)
                
                try:
                    page.wait_for_function(
                        """(idx) => {
                            const p = document.querySelectorAll('.outer_page')[idx];
                            if (!p) return false;
                            const img = p.querySelector('img');
                            return img && img.complete && img.naturalWidth > 0;
                        }""", 
                        arg=i, 
                        timeout=4000
                    )
                except:
                    pass
                
                img_path = os.path.join(temp_dir, f"page_{i+1}.png")
                page_element.screenshot(path=img_path)
                image_paths.append(img_path)
                progress.advance(capture_task)

            pdf_task = progress.add_task("[yellow]Synthesizing High-Fidelity PDF...", total=100)
            output_file = final_output or get_filename(url, doc_title)
            
            if not output_file.lower().endswith(".pdf"):
                output_file += ".pdf"
            
            with open(output_file, "wb") as f:
                f.write(img2pdf.convert(image_paths))
            
            progress.update(pdf_task, completed=100)
            time.sleep(0.5)
            
            browser.close()
            
    for img in image_paths:
        os.remove(img)
    os.rmdir(temp_dir)
    
    console.print(f"\n[bold green]Success![/bold green] File archived: [white]{output_file}[/white]")

if __name__ == "__main__":
    main()