#!/usr/bin/python2

class SimpleProcess():
    """A simple process that simulates nested locking."""

    def __init__(self, arbitrator, lock0_num, lock1_num):
        """Construct a SimpleProcess.

        Args:
        arbitrator - the kendo (or other) arbitrator
        lock0_num  - number of the 1st lock used by this
        lock1_num  - number of the 2nd lock used by this
        """

        self.arbitrator = arbitrator
        self.lock0_num = lock0_num
        self.lock1_num = lock1_num
        
        # FIXME: horrible dependencies; processes need their own pids...
        self.pid = arbitrator.register_process(self)

    def run(self):
        """Run this SimpleProcess. Just acquire 2 locks in nested sequence and
        then release them.
        """
        
        print "SimpleProcess, PID = ", self.pid, " starting..."

        self.arbitrator.det_mutex_lock(self.pid, self.lock0_num)
        self.arbitrator.det_mutex_lock(self.pid, self.lock1_num)

        self.arbitrator.det_mutex_unlock(self.pid, self.lock1_num)
        self.arbitrator.det_mutex_unlock(self.pid, self.lock0_num)
                
        # FIXME: remove this after the scheduling's fixed
        self.arbitrator.clocks[self.pid] = 10000

        print "SimpleProcess, PID = ", self.pid, " done!"

if __name__ == "__main__":
    import kendo

    print "Testing SimpleProcess..."

    kendo_arbitrator = kendo.Kendo(max_processes=2, num_locks=2, debug=True)
    
    process1 = SimpleProcess(kendo_arbitrator, 0, 1)
    process2 = SimpleProcess(kendo_arbitrator, 0, 1)
    
    kendo_arbitrator.run()

    print "Done testing SimpleProcess!"
