
from bashlime import *

@on_menu('Select')
def menu(entries):
	for project in Project.all():
		entries[project] = lambda p=project: workspace_set_project(p)
