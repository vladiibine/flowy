from flowy import Workflow, ActivityProxy, WorkflowProxy
from flowy import make_config, workflow_config


@workflow_config('SimpleWorkflow', 13, 'constant_list', 3, 5)
class SimpleWorkflow(Workflow):
    """
    Does nothing

    """
    div = ActivityProxy(
        name='SimpleActivity',
        version=1,
        task_list='constant_list',
    )

    def run(self, remote):
        print("what?")
        r = remote.div()
        print(r.result())
        return True


if __name__ == '__main__':
    my_config = make_config('RolisTest')

    # f = open("/home/local/3PILLAR/rszabo/flowy/mocks_output.txt", "w")
    # f.close()
    # f = open("/home/local/3PILLAR/rszabo/flowy/mocks.txt", "w")
    # f.close()

    # Start a workflow
    SimpleWorkflowID = my_config.workflow_starter('SimpleWorkflow', 13)
    print 'Starting: ', SimpleWorkflowID()

    # Start the workflow loop
    my_config.scan()
    my_config.start_workflow_loop(task_list='constant_list')
