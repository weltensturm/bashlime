
from bashlime import *

import stat, urllib.request, random

CONFIG = '/home/void/.fehbg'
WALLPAPER_DIR = '/home/void/Pictures/wallpapers/'


def set_wallpaper(res):
	if os.path.isfile(res):
		with open(CONFIG, 'w') as f:
			f.write('feh --bg-fill "%s"' % res)	
		st = os.stat(CONFIG)
		os.chmod(CONFIG, st.st_mode | stat.S_IEXEC)
	os.system(CONFIG)


def pick():
	files = []
	for d, subdirs, entries in os.walk(WALLPAPER_DIR):
		for f in entries:
			files.append(os.path.join(d, f)[len(WALLPAPER_DIR):])
	res = WALLPAPER_DIR + dmenu(files, ['-p', 'Select Wallpaper'])
	set_wallpaper(res)


def random_wallhaven():
	url = 'http://wallpapers.wallhaven.cc/wallpapers/full/wallhaven-%i.jpg'
	randpath = os.path.join(WALLPAPER_DIR, 'random_wallhaven.jpg')
	rand = random.randrange(1, 100000)
	try:
		urllib.request.urlretrieve(url % rand, randpath)
		set_wallpaper(randpath)
	except urllib.error.HTTPError:
		notification('Failed to download %i, trying another' % rand)
		random_wallhaven()


@on_menu('Set Wallpaper')
def menu(entries):
	entries['pick file'] = pick
	entries['random wallhaven'] = random_wallhaven


