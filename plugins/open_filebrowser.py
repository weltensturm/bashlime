
from bashlime import *


def browse_dirs():
	project = Project.current()
	folders = []
	for directory in project.dirs:
		for d, subdirs, entries in os.walk(directory):
			folders.append(d)
	result = dmenu(folders, ['-p', project.name])
	notification(result)
	if result:
		checked_run(['thunar', result])


@on_menu('Browse')
def menu(entries):
	project = Project.current()
	if project:
		for d in project.dirs:
			entries[d] = lambda d_c=d: checked_run(['thunar', d_c]);
	entries['Directories'] = browse_dirs
