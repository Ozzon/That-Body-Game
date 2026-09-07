from playwright.sync_api import sync_playwright
from pathlib import Path
import json
out=Path(__file__).resolve().parents[1]/'Docs'/'References'
out.mkdir(parents=True,exist_ok=True)
with sync_playwright() as p:
    browser=p.chromium.launch(channel='chrome',headless=True,args=['--disable-dev-shm-usage'])
    page=browser.new_page(viewport={'width':1920,'height':1080},device_scale_factor=1)
    page.goto('https://www.figma.com/board/rFrsYIJ8wyqGDX8OIUzbYo/The-body-game?node-id=0-1',wait_until='domcontentloaded',timeout=60000)
    page.wait_for_timeout(18000)
    print(page.locator('body').inner_text()[:18000])
    page.screenshot(path=str(out/'figma-overview.png'))
    print('FIGMA_SCREENSHOT',out/'figma-overview.png')
    browser.close()
