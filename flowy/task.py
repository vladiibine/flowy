import json
from functools import partial

from boto.swf.exceptions import SWFResponseError
from flowy import logger, posint_or_none, str_or_none
from flowy.exception import SuspendTask, TaskError
from flowy.result import Error, Placeholder, Result, Timeout


serialize_result = staticmethod(json.dumps)
deserialize_result = staticmethod(json.loads)
deserialize_args = staticmethod(json.loads)


@staticmethod
def serialize_args(*args, **kwargs):
    return json.dumps([args, kwargs])


class Task(object):
    def __init__(self, input, token):
        self._input = input
        self._token = token

    @property
    def token(self):
        return str(self._token)

    def __call__(self):
        args, kwargs = self._deserialize_arguments(str(self._input))
        try:
            result = self.run(*args, **kwargs)
        except SuspendTask:
            self._suspend()
        except Exception as e:
            logger.exception("Error while running the task:")
            self._fail(e)
        else:
            return self._finish(result)

    def run(self, *args, **kwargs):
        raise NotImplementedError

    def _suspend(self):
        raise NotImplementedError

    def _fail(self, reason):
        raise NotImplementedError

    def _finish(self, result):
        raise NotImplementedError
        self._scheduler.complete(self._serialize_result(result))

    _serialize_result = serialize_result
    _deserialize_arguments = deserialize_args


class SWFActivity(Task):
    def __init__(self, swf_client, input, token):
        self._swf_client = swf_client
        super(SWFActivity, self).__init__(input, token)

    def _suspend(self):
        pass

    def _fail(self, reason):
        try:
            self._swf_client.respond_activity_task_failed(
                reason=str(reason)[:256], task_token=self.token
            )
        except SWFResponseError:
            logger.exception('Error while failing the activity:')
            return False
        return True

    def _finish(self, result):
        try:
            result = str(self._serialize_result(result))
        except TypeError:
            logger.exception('Could not serialize result:')
            return False
        try:
            self._swf_client.respond_activity_task_completed(
                result=result, task_token=self.token
            )
        except SWFResponseError:
            logger.exception('Error while completing the activity:')
            return False
        return True

    def heartbeat(self):
        try:
            self._swf_client.record_activity_task_heartbeat(
                task_token=self.token)
        except SWFResponseError:
            logger.exception('Error while sending the heartbeat:')
            return False
        return True


class Workflow(Task):
    def options(self, **kwargs):
        return self._scheduler.options(**kwargs)

    def restart(self, *args, **kwargs):
        arguments = self._serialize_restart_arguments(*args, **kwargs)
        return self._scheduler.restart(arguments)

    def _finish(self, result):
        r = result
        if isinstance(result, Result):
            r = result.result()
        elif isinstance(result, (Error, Timeout)):
            try:
                result.result()
            except TaskError as e:
                return self._scheduler.fail(str(e))
        elif isinstance(result, Placeholder):
            return self._scheduler.suspend()
        return super(Workflow, self)._finish(r)

    def schedule_activity(self, *args, **kwargs):
        pass

    def schedule_workflow(self, *args, **kwargs):
        pass

    _serialize_restart_arguments = serialize_args


class TaskProxy(object):
    def __get__(self, obj, objtype):
        if obj is None:
            return self
        if not hasattr(obj, '_scheduler'):
            raise AttributeError('no scheduler bound to the task')
        return partial(self, obj._scheduler)

    _serialize_arguments = serialize_args
    _deserialize_result = deserialize_result


class ActivityProxy(TaskProxy):
    def __init__(self, task_id,
                 heartbeat=None,
                 schedule_to_close=None,
                 schedule_to_start=None,
                 start_to_close=None,
                 task_list=None,
                 retry=3,
                 delay=0,
                 error_handling=False):
        self._kwargs = dict(
            task_id=task_id,
            heartbeat=posint_or_none(heartbeat),
            schedule_to_close=posint_or_none(schedule_to_close),
            schedule_to_start=posint_or_none(schedule_to_start),
            start_to_close=posint_or_none(start_to_close),
            task_list=str_or_none(task_list),
            retry=max(int(retry), 0),
            delay=max(int(delay), 0),
            error_handling=bool(error_handling)
        )

    def __call__(self, scheduler, *args, **kwargs):
        return scheduler.remote_activity(
            args=args, kwargs=kwargs,
            args_serializer=self._serialize_arguments,
            result_deserializer=self._deserialize_result,
            **self._kwargs
        )


class WorkflowProxy(TaskProxy):
    def __init__(self, task_id,
                 decision_duration=None,
                 workflow_duration=None,
                 task_list=None,
                 retry=3,
                 delay=0,
                 error_handling=False):
        self._kwargs = dict(
            task_id=task_id,
            decision_duration=posint_or_none(decision_duration),
            workflow_duration=posint_or_none(workflow_duration),
            task_list=str_or_none(task_list),
            retry=max(int(retry), 0),
            delay=max(int(delay), 0),
            error_handling=bool(error_handling)
        )

    def __call__(self, scheduler, *args, **kwargs):
        return scheduler.remote_subworkflow(
            args=args, kwargs=kwargs,
            args_serializer=self._serialize_arguments,
            result_deserializer=self._deserialize_result,
            **self._kwargs
        )
