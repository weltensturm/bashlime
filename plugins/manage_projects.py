
from bashlime import *


def create():
	name = dmenu(Project.all(), ['-p', 'Name'])
	workspace_set_project(name)
	project = Project(name)
	project.save()
	call(['xdg-open', project.path])


def delete():
	target = project_prompt()
	if target:
		Project(target).delete()
		workspace_set_project(None)


@menu_global('Manage Projects')
def menu(entries):
	entries['Create'] = create
	entries['Remove'] = delete


@menu_project('Manage Project')
def menu(entries, project):
	entries['Edit'] = lambda: call(['xdg-open', project.path])


