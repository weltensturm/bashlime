
from bashlime import *
import traceback

if __name__ == '__main__':
	try:
		os.environ['DE'] = 'gnome'
		os.environ['PYTHONPATH'] = '/home/void/.i3/ide/'

		if sys.argv[1] == "file":
			open_file(file_prompt())
		elif sys.argv[1] == 'menu':
			plugin_menu()
		elif sys.argv[1] == 'update':
			workspace_update()
		else:
			raise Exception("Invalid command: %s" % sys.argv[1])
	except Exception as e:
		notification(traceback.format_exc(), True)



