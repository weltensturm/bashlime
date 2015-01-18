
from bashlime import *

import stat

def select():
	project = Project.current()
	files = []
	for f in project.files_full():
		if os.stat(f).st_mode & stat.S_IEXEC:
			files.append(f)
	res = dmenu(files)
	checked_run(res)

@menu_project('Run')
def menu(entries, project):
	entries['executable'] = select


