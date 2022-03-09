#!/usr/bin/python


class Counter:
    """This is a counter which can be given a "policy" configuration
    which decides when some external entity shall be informed about
    the changes in the counter. The policy can be "value based"
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

    def add(self, increment, now, scheduler, policy):
        """Add increment to counter, possibly schedule it, and evaluate it
        aginst policy. Return True if value limit policy is met or False if
        still pending.
        """
        first_update = (self.val == 0)

        # Actually account
        self.val += increment

        # Schedule counter if it has time based policy and this is the first
        # update
        if policy.time_limit and first_update:
            scheduler.add(self, now + policy.time_limit)
            self.is_scheduled = True

        if policy.value_limit and not self.passed_value_limit and self.val >= policy.value_limit:
            if self.is_scheduled:
                scheduler.remove(self)
                self.is_scheduled = False
            return True

        return False
