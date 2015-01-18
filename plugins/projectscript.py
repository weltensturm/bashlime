
from bashlime import *
import re


def path(p):
	return var_text(os.path.join(PLUGIN_DATA, 'projectscript', p))


def matching_errors(text):
	config = Config.get(path('%(project)s.json'))
	res = []
	for name, entry in config.data.items():
		if not 'regex' in entry:
			continue
		a = re.compile(entry['regex'])
		for line in text.splitlines():
			if a.match(line):
				res.append(line)
	return res


def run(name):
	config = Config.get(path('%(project)s.json'))
	config = config.data[name]
	for dependency in config.get('require', []):
		run(dependency)
	p = Popen(config['command'], cwd=config['dir'] or '', stdout=PIPE, stderr=PIPE)
	result = p.wait()
	data = 'STDERR\n' + p.stderr.read().decode('utf-8')
	data += 'STDOUT\n' + p.stdout.read().decode('utf-8')
	with open(path('build.log'), 'w') as f:
		f.write(data)
	if result:
		show_errors()
		raise ActionAbort('"%s" exited with code %i. Show details with "Open Log"' % (name, result))
	notification('"%s" finished.' % name)


def show_errors():
	config = Config.get(path('%(project)s.json'))
	with open(path('build.log')) as f:
		data = f.read()
	res = matching_errors(data)
	if not res:
		raise ActionAbort('No errors.')
	res = dmenu(res, ['-p', 'Errors'])
	for name, cfg in config.data.items():
		a = re.compile(cfg.get('regex', '\\\\'))
		match = a.match(res)
		if match:
			call(['subl3', '%s:%s' % (os.path.join(cfg['dir'], match.group(1)), match.group(2))])
			return


def open_log():
	call(['xdg-open', path('build.log')])


def create_default_config(p):
	config = Config(path(p))
	project = Project.current()
	config.data = {
		'Build': {
			'command': ['dub', 'build'],
			'dir': project.dirs[0],
			'regex': '([^@\n]+)\\(([0-9]+)\\):'
			},
		'Run': {
			'command': ['./output'],
			'dir': project.dirs[0]
			}
		}
	config.save()
	return config


def edit():
	config = Config.get(path('%(project)s.json'))
	if not config:
		config = create_default_config('%(project)s.json')
	os.system('xdg-open "%s"' % config.path)


@on_menu('Script')
def menu(entries):
	if not Project.current():
		return

	entries['Edit Config'] = edit
	entries['Show Errors'] = show_errors
	entries['Open Log'] = open_log

	config = Config.get(path('%(project)s.json'))
	if config:
		for name in config.data.keys():
			entries['"%s"' % name] = lambda n=name: run(n)


