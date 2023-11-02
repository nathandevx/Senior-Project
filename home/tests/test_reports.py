from home.tests.base import BaseTestCase


class ReportBaseTestCase(BaseTestCase):
	def setUp(self):
		super().setUp()

	def _superuser_access(self, url):
		self.client.login(username=self.superuser.username, password=self.password)
		response = self.client.get(url)
		return response.status_code

	def _non_superuser_access(self, url):
		self.client.login(username=self.user1.username, password=self.password)
		response = self.client.get(url)
		return response.status_code

	def _superuser_login(self):
		self.client.login(username=self.superuser.username, password=self.superuser_password)


class TestReportList(ReportBaseTestCase):
	def setUp(self):
		super().setUp()

	def test_access(self):
		pass

class TestReportOrders(ReportBaseTestCase):
	def setUp(self):
		super().setUp()

	def test_access(self):
		pass


class TestReportProducts(ReportBaseTestCase):
	def setUp(self):
		super().setUp()

	def test_access(self):
		pass


class TestReportBlogs(ReportBaseTestCase):
	def setUp(self):
		super().setUp()

	def test_access(self):
		pass


class TestReportCharts(ReportBaseTestCase):
	def setUp(self):
		super().setUp()

	def test_access(self):
		pass


class TestReportExport(ReportBaseTestCase):
	def setUp(self):
		super().setUp()

	def test_access(self):
		pass


class TestReportAPIStatus(ReportBaseTestCase):
	def setUp(self):
		super().setUp()

	def test_access(self):
		pass

