
from bashlime import *


def os_call(command, *args):
	'''Run OS command
		args: [display text, selection list callbac], repeating'''
	userargs = []
	for userarg in args:
		choice = dmenu(userarg[1], ['-p', userarg[0]])
		if not choice:
			return
		userargs.append(choice)

	text = checked_run([command] + userargs)
	return userargs


def touch():
	res = os_call('touch', ['New File', Project.current().subdirs()])
	if res:
		call(['xdg-open', res[0]])


@menu_project('Util')
def menu(entries, project):
	entries['mv'] = lambda: os_call('mv', ['Source', project.files_full()], ['Target', project.subdirs()+project.files_full()])
	entries['rm'] = lambda: os_call('rm', ['Remove File', project.files_full()])
	entries['cp'] = lambda: os_call('cp', ['Source', project.files_full()], ['Target', project.subdirs()])
	entries['touch'] = touch
	entries['mkdir'] = lambda: os_call('mkdir', ['New Directory', project.subdirs()])
	entries['rmdir'] = lambda: os_call('rmdir', ['Remove Directory', project.subdirs()])

