#!/usr/bin/bash

import json, os, sys, traceback, importlib
from subprocess import Popen, PIPE, call

BASHLIME_DIR = os.path.dirname(os.path.realpath(__file__))
PROJECT_DIR = os.path.join(BASHLIME_DIR, 'projects')
PLUGIN_DIR = os.path.join(BASHLIME_DIR, 'plugins')
PLUGIN_DATA = os.path.join(PLUGIN_DIR, 'data')
#PROJECT_LIST = os.path.join(BASHLIME_DIR, 'projects.json')

CONFIG_WORKSPACE = os.path.join(BASHLIME_DIR, 'workspaces.json')


DMENU = [
	"dmenu",
	"-fn", "Consolas-10",
	"-f",
	"-i",
	"-l", "20"
]


def checked_run(cmd, inp=''):
	cmd = ' '.join([('"%s"' % x) for x in cmd])
	p = Popen(cmd, stdout=PIPE, stderr=PIPE, shell=True)
	result = p.wait()
	data = p.stderr.read().decode('utf-8')
	data += p.stdout.read().decode('utf-8')
	if result:
		raise ActionAbort(data)
	elif data:
		notification(data)
	return data


def dmenu(lines, moreargs=[]):
	proc = Popen(DMENU + moreargs, stdout=PIPE, stdin=PIPE)
	return proc.communicate(input='\n'.join(lines).encode())[0].decode('utf-8').strip()


def notification(msg, critical=False):
	if critical:
		call(['notify-send', str(msg), '-u', 'critical'])
	else:
		call(['notify-send', str(msg)])


def error(msg):
	raise Exception(msg)


def nagbar(msg, f):
	os.system('i3-nagbar -m "%s" -b Details "vim \\"%s\\"" &' % (msg, f))


def open_file(target):
	if target:
		path, filename = os.path.split(target)
		Popen(['xdg-open', filename], cwd=path)


class ActionAbort(Exception):
	pass


class Config(object):

	@classmethod
	def get(cls, path):
		if os.path.isfile(path):
			return cls(path)

	def __init__(self, path):
		self.data = {}
		self.path = path
		if os.path.isfile(path):
			with open(self.path) as f:
				self.data = json.load(f)

	def save(self):
		ensure_dir(self.path)
		with open(self.path, 'w') as f:
			json.dump(self.data, f, sort_keys=True, indent=4, separators=(',', ': '))


class Project(object):

	@classmethod
	def current(cls):
		name = Config.get(CONFIG_WORKSPACE).data.get(workspace_number())
		if not name:
			return
		project = Project(name)
		if os.path.isfile(project.path):
			return project

	@classmethod
	def all(cls):
		for (dirpath, dirnames, filenames) in os.walk(PROJECT_DIR):
			return [os.path.splitext(x)[0] for x in filenames]
		return []

	def __init__(self, name):
		self.name = name
		self.path = os.path.join(PROJECT_DIR, name + '.json')
		self.dirs = Config(self.path).data.get("dirs", [])

	def dir_add(self, dir):
		if not dir.endswith('/'):
			dir = dir+'/'
		if dir in self.dirs:
			error('Path already in project')
		self.dirs.append(dir)
		self.save()

	def dir_remove(self, dir):
		if not dir.endswith('/'):
			dir = dir+'/'
		self.dirs.remove(dir)
		self.save()
		workspace_set_project(name)

	def save(self):
		cfg = Config(self.path)
		cfg.data["dirs"] = self.dirs
		cfg.save()

	def delete(self):
		os.remove(self.path)


	def files(self):
		files = []
		exclude = Config(self.path).data.get('exclude', [])
		for directory in self.dirs:
			for d, subdirs, entries in os.walk(directory):
				for f in entries:
					path = os.path.join(d, f)[len(directory):]
					if any(x in path for x in exclude):
						continue
					files.append(path)
		return files

	def files_full(self):
		files = []
		for directory in self.dirs:
			for d, subdirs, entries in os.walk(directory):
				for f in entries:
					files.append(os.path.join(d, f))
		return files

	def subdirs(self):
		dirs = []
		for directory in self.dirs:
			for d, subdirs, entries in os.walk(directory):
				dirs.append(os.path.join(d, ''))
		return dirs



def ensure_dir(path):
	(d, f) = os.path.split(path)
	if not os.path.isdir(d):
		os.makedirs(d)


current_plugin = 'No Plugin'
def var_text(text):
	project = Project.current()
	return text.replace('%(project)s', project.name).replace('%(plugin)s', current_plugin)


def workspace_set_project(project):
	ws = workspace_number()
	cfg = Config(CONFIG_WORKSPACE)
	cfg.data[ws] = project
	cfg.save()
	workspace_update()


def workspace_number():
	p = Popen(['i3-msg', '-t', 'get_workspaces'], stdout=PIPE)
	data = json.loads(p.stdout.read().decode('utf-8'))
	for workspace in data:
		if workspace['focused']:
			return str(workspace['num'])
	return '-1'


def workspace_rename(name):
	call(['i3-msg', 'rename workspace to "%s"' % name])


def workspace_update():
	project = Project.current()
	if project:
		workspace_rename('%s: %s' % (workspace_number(), project.name))
	else:
		workspace_rename(workspace_number())


def project_prompt():
	d = dmenu(Project.all())
	return d and d or ''


def getdate(paths, f):
	for path in paths:
		if os.path.isfile(os.path.join(path, f)):
			return os.stat(os.path.join(path, f)).st_mtime
	return 0


def file_prompt():
	project = Project.current()
	if not project:
		return ""
	files = project.files()
	files.sort(key=lambda x: getdate(project.dirs, x), reverse=True)
	f = dmenu(files, ['-p', project.name])
	for directory in project.dirs:
		if os.path.isfile(os.path.join(directory, f)):
			return os.path.join(directory, f)
	return ""


def with_project(fn):
	def inner(*args, **kwargs):
		project = Project.current()
		if project:
			fn(project, *args, **kwargs)
	return inner


def plugin_data(path):
	p = var_text(os.path.join(PLUGIN_DATA, '%(plugin)s', path))
	ensure_dir(p)
	return p


menu_project_hooks = {}

def menu_project(name):
	def decorator(fn):
		if name in menu_project_hooks:
			error('%s already registered' % name)
		menu_project_hooks[name] = fn
		return fn
	return decorator


menu_global_hooks = {}

def menu_global(name):
	def decorator(fn):
		if name in menu_project_hooks:
			error('%s already registered' % name)
		menu_global_hooks[name] = fn
		return fn
	return decorator


on_menu_hooks = {}

def on_menu(name):
	def decorator(fn):
		if name in on_menu_hooks:
			error('Name %s already used' % name)
		on_menu_hooks[name] = fn
		return fn
	return decorator


def plugin_menu():
	global current_plugin

	for path in os.listdir(PLUGIN_DIR):
		if path.endswith('.py'):
			module = importlib.import_module("plugins.%s" % path[:-3])

	entries = {}

	project = Project.current()

	for name, fn in menu_global_hooks.items():
		current_plugin = name
		e = {}
		fn(e)
		for text, fn in e.items():
			entries['%s: %s' % (name, text)] = fn

	if project:
		for name, fn in menu_project_hooks.items():
			current_plugin = name
			e = {}
			fn(e, project)
			for text, fn in e.items():
				entries['%s: %s' % (name, text)] = fn


	for name, fn in on_menu_hooks.items():
		current_plugin = name
		e = {}
		fn(e)
		for text, fn in e.items():
			entries['%s: %s' % (name, text)] = fn

	result = dmenu(sorted(entries.keys()), ['-p', 'Menu'])

	if result in entries:
		try:
			entries[result]()
		except ActionAbort as e:
			notification(e)
		except Exception as e:
			notification(traceback.format_exc(), True)

