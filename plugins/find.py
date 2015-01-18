
from bashlime import *


def find_content(project):
	what = dmenu([]);
	res = checked_run(["grep", "-nr", "%s" % what] + project.dirs);
	dmenu(res.splitlines());


@menu_project('Find')
def menu(entries, project):
	entries['file content'] = lambda x=project: find_content(x)

