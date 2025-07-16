import threading
import weakref
import automojo.testbase as testbase

from automojo.testbase.results.model.progressdelivery import SummaryProgressDelivery
from automojo.interop.protocols.tasker.taskingprogressmonitor import TaskingProgressMonitor


class FailingPromise:
    def __init__(self, monitor: TaskingProgressMonitor):
        self.tasking_id = "failing"
        self._monitor = monitor

    def get_progress(self):
        # Stop the monitor after this call to ensure the loop exits
        self._monitor._pulling_progress = False
        raise RuntimeError("progress failure")


def test_pull_progress_entry_handles_missing_progress() -> None:
    updates = []

    def progress_callback(progress_list):
        updates.append(progress_list)
        return

    summary = SummaryProgressDelivery(progress_interval=0.0, progress_callback=progress_callback)
    monitor = TaskingProgressMonitor(summary, [])

    prom = FailingPromise(monitor)
    monitor._monitored_promise_refs = {prom.tasking_id: weakref.ref(prom)}

    sgate = threading.Event()
    exc = None
    try:
        monitor._pull_progress_entry(sgate)
    except BaseException as err:
        exc = err

    testbase.assert_equal(exc, None)
    testbase.assert_equal(len(updates), 1)
    testbase.assert_equal(updates[0], [])
    return
