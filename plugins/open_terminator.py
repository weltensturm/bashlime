
from bashlime import *


@on_menu('Terminator')
def plugin(entries):
	project = Project.current()
	if project:
		for dir in project.dirs:
			entries[dir] = lambda d=dir: os.system('terminator --working-directory "%s"' % d);

