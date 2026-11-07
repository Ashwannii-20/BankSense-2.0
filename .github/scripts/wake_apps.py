"""Visit the Streamlit apps and wake any that have gone to sleep."""
import sys
from playwright.sync_api import sync_playwright

APPS = [
    "https://banksense-2-0.streamlit.app/",
    "https://ashwannii-20-banksense-ai-app-gpfktk.streamlit.app/",
]

failed = []
with sync_playwright() as p:
    browser = p.chromium.launch()
    for url in APPS:
        page = browser.new_page()
        try:
            page.goto(url, timeout=90_000)
            page.wait_for_timeout(8_000)
            button = page.get_by_role("button", name="Yes, get this app back up!")
            if button.count() > 0:
                button.first.click()
                page.wait_for_timeout(60_000)
                print(f"woken up: {url}")
            else:
                print(f"awake: {url}")
        except Exception as exc:
            print(f"failed: {url} ({exc})")
            failed.append(url)
        finally:
            page.close()
    browser.close()

sys.exit(1 if failed else 0)
