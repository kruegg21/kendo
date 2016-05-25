#!/usr/bin/python2

# Test process for sanity checking

class IndependentProcess():
    """A process that can run independently of any others."""

    def __init__(self, arbitrator):
        """Construct an IndependentProcess."""

        self.pid = arbitrator.register_process(self)

    def run(self):
        """Run this IndependentProcess. Print some stuff then end."""

        print "IndependentProcess, PID = ", self.pid

if __name__ == "__main__":
    import kendo

    arbitrator = kendo.Kendo(num_locks=2, max_processes=2)

    p1 = IndependentProcess(arbitrator)
    p2 = IndependentProcess(arbitrator)

    arbitrator.run()
