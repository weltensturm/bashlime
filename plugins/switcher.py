
from bashlime import *

def window_list():
	command = r'echo -ne "i3-ipc\x0\x0\x0\x0\x4\x0\x0\x0" | socat STDIO UNIX-CLIENT:`i3 --get-socketpath`'
	raw = os.system(command)
	#data = json.loads(raw.decode('utf-8'))
	notification(raw)


@on_menu('Switch')
def menu(entries):
	entries['test'] = window_list
