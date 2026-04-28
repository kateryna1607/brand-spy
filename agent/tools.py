"""Universal Web Fetcher with Fallback mechanism."""
import requests
import cloudscraper
from rich.console import Console
from bs4 import BeautifulSoup

console = Console()

def fetch_universal_content(url: str) -> str:
    """
    Tries Jina AI first (better for JS), then falls back to direct request.
    Automatically handles missing https:// or www.
    """
    url = url.strip()
    # Remove any trailing slash
    url = url.rstrip("/")
    
    if not url.startswith("http"):
        urls_to_try = [f"https://{url}", f"https://www.{url}"]
    else:
        # If they provided http/https, try that, and if it fails and doesn't have www, try adding www
        base_domain = url.split("://", 1)[-1]
        if not base_domain.startswith("www."):
            urls_to_try = [url, f"https://www.{base_domain}"]
        else:
            urls_to_try = [url]
            
    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.9",
    }
            
    for try_url in urls_to_try:
        jina_url = f"https://r.jina.ai/{try_url}"
        console.log(f"[cyan]🌐 Attempting Jina AI reader for[/cyan] {try_url}...")
        try:
            response = requests.get(jina_url, headers=headers, timeout=20)
            if response.status_code == 200 and len(response.text) > 200:
                return response.text
        except Exception as e:
            console.log(f"[yellow]Jina AI failed for {try_url}, falling back to direct request...[/yellow]")
    
        # 2. Direct Fallback if Jina fails
        console.log(f"[cyan]🌐 Direct scraping attempt for {try_url}...[/cyan]")
        try:
            try:
                import cloudscraper
                scraper = cloudscraper.create_scraper(delay=10, browser={'browser': 'chrome', 'platform': 'windows', 'mobile': False})
                response = scraper.get(try_url, timeout=20)
            except ImportError:
                response = requests.get(try_url, headers=headers, timeout=20)
    
            response.raise_for_status()
            
            # Extract text from HTML
            soup = BeautifulSoup(response.text, 'html.parser')
            for script_or_style in soup(["script", "style"]):
                script_or_style.decompose()
    
            text = soup.get_text(separator=' ')
            lines = (line.strip() for line in text.splitlines())
            chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
            text = '\n'.join(chunk for chunk in chunks if chunk)
            
            if len(text) > 100:
                return text
        except Exception as e:
            console.log(f"[red]Scraping failed for {try_url}: {e}[/red]")
            continue # Try next URL (like www. fallback)
        
    return ""
