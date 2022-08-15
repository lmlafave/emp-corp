import os
import re

from subprocess import run

class MergeException(Exception):
	def __init__(self, *args):
		if args:
			self.msg = args[0]
		else:
			self.msg = 'Merge unsuccessful'

	def __str__(self):
		return self.msg

class IncompleteMergeDoneException(MergeException):
	def __init__(self, num_failed):
		super().__init__(str(num_failed) + ' branches could not be merged.')

class DataMergeExeNotFoundException(MergeException):
	def __init__(self, path):
		super().__init__('DataMerge.exe not found at ' + path + '.')

class DaqNotFoundException(MergeException):
	def __init__(self, path):
		super().__init__('No file named \'daq\' found at ' + path + '.')

class EmpdatNotFoundException(MergeException):
	def __init__(self, path):
		super().__init__('No files with extension \'.empdat\' found at ' + path + '.')

def merge_leaves(root, ignore_branches = None):
	datamerge_exe = os.path.expanduser('~\AppData\Roaming\EMP\DataMerge\DataMerge.exe')
	if not os.path.exists(datamerge_exe):
		datamerge_exe = os.path.abspath(input('Enter path to DataMerge.exe on this machine, or press [Enter] to abort:'))
	if datamerge_exe == '':
		print('Program aborted.')
		return None

	try:
		if not os.path.exists(datamerge_exe):
			raise DataMergeExeNotFoundException

		csv_paths = []

		num_failed = 0
		num_ignored_found = 0
		for branch, twigs, leaves in os.walk(root):
			if ignore_branches is not None and os.path.normpath(branch) in map(os.path.normpath, ignore_branches):
				num_ignored_found += 1
			else:
				try:
					log_re = re.compile('log|lab(?=.*\.empdat)')
					logs = [os.path.join(branch, leaf) for leaf in filter(log_re.match, leaves)]

					if not logs == []:
						if not 'daq' in leaves:
							raise DaqNotFoundException(branch)
						else:
							csv_paths.append(os.path.join(branch, 'data.csv'))

							if not 'data.csv' in leaves:
								run([datamerge_exe, os.path.join(branch, 'daq'), *logs], input=os.path.abspath(csv_paths[-1]), text=True)
					elif 'daq' in leaves:
						raise EmpdatNotFoundException(branch)

				except MergeException as merge_err:
					print(merge_err)
					num_failed += 1

		if not num_failed == 0:
			raise IncompleteMergeDoneException(num_failed)

# TO-DO: Refactor error-tracker variables after Google's Python style guide.
	except IncompleteMergeDoneException as incomplete_err:
		print(incomplete_err)

	finally:
		if num_ignored_found == 0:
			print('Merge execution completed.')
		else:
			print(f'Merge execution completed with {len(ignore_branches)} directories ignored ({num_ignored_found} found in tree, {len(ignore_branches) - num_ignored_found} not found).')
	return csv_paths
