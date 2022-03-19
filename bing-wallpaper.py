from datetime import date
import json
import os
import subprocess
from urllib.request import urlopen, Request

FEED_URL = 'https://peapix.com/bing/feed?country='
DEFAULT_HEADERS = {
    'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64; rv:99.0) Gecko/20100101 Firefox/99.0',
}


def main() -> None:
    if not os.environ.get('DISPLAY', None):
        print('$DISPLAY not set')
        return

    # Load configuration from environment variable
    country = os.environ.get('BING_WALLPAPER_COUNTRY', '')
    wallpapers_dir = os.environ.get('BING_WALLPAPER_PATH', os.path.expanduser('~/.wallpapers'))

    # check store directory
    os.makedirs(wallpapers_dir, exist_ok=True)

    # download feed json
    with urlopen(Request(f'{FEED_URL}{country}', headers=DEFAULT_HEADERS)) as resp:
        feed = json.load(resp)

    # download new wallpapers
    for item in feed:
        path = os.path.join(wallpapers_dir, f'{item["date"]}.jpg')
        if os.path.exists(path):
            continue
        with urlopen(Request(item['imageUrl'], headers=DEFAULT_HEADERS)) as resp:
            data = resp.read()
        with open(path, 'wb') as f:
            f.write(data)

    # update xfce4-desktop wallpaper configuration
    today_wallpaper = os.path.join(wallpapers_dir, f'{date.today().isoformat()}.jpg')
    if not os.path.exists(today_wallpaper):
        return
    proc = subprocess.run(['xrandr | grep " connected"'], capture_output=True, shell=True, text=True)
    monitors = [line.split()[0] for line in proc.stdout.split('\n') if line]
    for monitor in monitors:
        prop_name = f'/backdrop/screen0/monitor{monitor}/workspace0/last-image'
        subprocess.run(['xfconf-query', '-c', 'xfce4-desktop', '-p', prop_name, '-s', today_wallpaper])


if __name__ == '__main__':
    main()
