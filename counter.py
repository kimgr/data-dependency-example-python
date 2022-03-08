#!/usr/bin/python


class Counter:
    """This is a counter which can be given a "granularity" configuration
    which decides when some external entity shall be informed about
    the changes in the counter. The granularity can be "value based"
    (external should be informed when value crosses a threshold) or
    "time based" (external should be informed at least within
    specified time from when value last changed) or both.

    As an example this could be the quota usage for your cellular data
    subscription. Don't want to update some database to persist your
    quota for every packet you send, but if you have sent enough data
    it better be updated (say every 1MB), or enough time has passed
    (so that if you just send 0.9MB it still eventually get
    persisted).

    """
    def __init__(self):
        self.is_scheduled = False
        self.passed_value_limit = False
        self.val = 0

    def take(self, scheduler):
        if self.is_scheduled:
            scheduler.remove(self)
        self.is_scheduled = False
        self.passed_value_limit = False
        res = self.val
        self.val = 0
        return res

    def add(self, increment, now, scheduler, granularity):

        # Schedule counter if it has time based granularity
        if granularity.time_based:
            # and this is the first update
            if self.val == 0:
                scheduler.add(self, now + granularity.time_based)
                self.is_scheduled = True

        # Actually account
        self.val += increment

        if granularity.value_based and not self.passed_value_limit and self.val >= granularity.value_based:
            if self.is_scheduled:
                scheduler.remove(self)
                self.is_scheduled = False
            return CounterState.READY

        return CounterState.PENDING
