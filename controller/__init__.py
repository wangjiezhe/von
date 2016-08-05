import argparse
import model

from controller.add import main as do_add
from controller.edit import main as do_edit
from controller.reindex import main as do_reindex
from controller.search import main as do_search
from controller.show import main as do_show
from controller.ss import main as do_ss

class VonController:
	# Complicated
	def do_add(self, argv):
		do_add(argv)
	def do_edit(self, argv):
		do_edit(argv)
	def do_reindex(self, argv):
		do_reindex(argv)
	def do_search(self, argv):
		do_search(argv)
	def do_show(self, argv):
		do_show(argv)
	def do_ss(self, argv):
		do_ss(argv)
	do_status = do_ss

	# Shorter ones
	def do_clear(self, argv):
		parser = argparse.ArgumentParser(prog='clear',\
				description='Clears the Cache.')
		opts = parser.parse_args(argv)
		model.clearCache()
