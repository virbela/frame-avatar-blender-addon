from traceback import format_exception
from textwrap import indent

#We could reuse this in other python stuff we do
#Note that when we expect failure we haven't specified exactly what failure to expect and this could be a future feature


class log_entry:
	class error:
		def __init__(self, test, error_type, error_value, traceback):
			self.test = test
			self.error_type = error_type
			self.error_value = error_value
			self.traceback = traceback

	class success:
		def __init__(self, test):
			self.test = test

class test_suite_context:
	def __init__(self, suite, should_fail):
		self.suite = suite
		self.should_fail = should_fail

	def __call__(self, description):
		return test_context(self.suite, description, should_fail=self.should_fail)


class test_suite:
	def __init__(self, description, verbose=False):
		self.description = description
		self.verbose = verbose
		self.log = list()
		self.fail_count = 0

	def __enter__(self):
		self.inform_user()
		return test_suite_context(self, False), test_suite_context(self, True)

	def __exit__(self, et, ev, tb):
		if not et:	#We will not exit the process here if there was some sort of error since that will make it much harder to see what is going on
			self.exit()

	def log_success(self, test, **named):
		self.log.append(log_entry.success(test, **named))
		print(f'        OK       Expectation: {test.nature:20}Description: {test.description}')

	def log_error(self, test, error_type, error_value, traceback, **named):
		self.log.append(log_entry.error(test, error_type, error_value, traceback, **named))
		self.fail_count += 1
		print(f'        FAIL     Expectation: {test.nature:20}Description: {test.description}')
		if self.verbose:
			print()
			if test.should_fail:
				print('            Test should have failed but did not')
			else:
				print(indent(''.join(format_exception(None, value=error_value, tb=traceback)), '            '))

	def inform_user(self):
		print('Running tests')
		print(f'    {self.description}')

	def exit(self):
		failed = self.fail_count
		count = len(self.log)

		#Maybe later we should have different verbosity levels but for now this is always output
		#and verbosity affects each individual test - specifically tracebacks and such
		print()
		print(f'TESTS FAILED: Concluded {count} tests of which {failed} failed')
		print()

		if failed:
			exit(1)
		else:
			exit(0)

class test_context:
	def __init__(self, suite, description, should_fail=False):
		self.suite = suite
		self.description = description
		self.should_fail = should_fail


	@property
	def nature(self):
		if self.should_fail:
			return 'throw exception'
		else:
			return 'no exception'

	def __enter__(self):
		pass

	def __exit__(self, et, ev, tb):

		if self.should_fail:
			successful = et is not None
		else:
			successful = et is None

		if successful:
			self.suite.log_success(self)
		else:
			self.suite.log_error(self, et, ev, tb)

		return True	#Don't raise exception
