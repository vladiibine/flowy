from pyswf.workflow import Workflow, ActivityProxy
from pyswf.client import WorkflowClient


my_client = WorkflowClient('SeversTest', 'prime_task_list')


@my_client
class PrimeTest(Workflow):
    name = 'a'
    version = '123'

    div = ActivityProxy('Divider2', '1')

    def run(self, n=None):
        n = n if n is not None else 7 * 11
        for i in range(2, n/2 + 1):
            r = self.div(n, i)
            if r.result():
                print '%s is divisible by %s' % (n, i)
                return 'not prime'
        return 'prime'


my_client.run()