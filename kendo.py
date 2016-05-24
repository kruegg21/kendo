import multiprocessing

####################################################################################
# GLOBAL LOCK
# used to make sure output lines print together
global_lock = multiprocessing.Lock()
####################################################################################

####################################################################################
# PROCESS
# very basic process
# n : process number
def process(n, lock0, lock1, clocks, lrlt_list, lock_held_list):
	det_mutex_lock(n, clocks, lock0, lrlt_list[0], lock_held_list[0])
	det_mutex_unlock(n, clocks, lock0, lrlt_list, lock_held_list, 0)
####################################################################################

####################################################################################
# KENDO FUNCTIONS

# WAITS FOR DETERMINISTIC LOGICAL CLOCK TO BE GLOBAL MINIMUM
# n : process number
# clocks : list of deterministic logical clocks
def wait_for_turn(n, clocks):
	process_clock_value = clocks[n]
	while True:
		if process_clock_value < min(clocks) or \
		   (process_clock_value == min(clocks) and n == clocks.index(min(clocks))):
			clocks[n] += 1
			break
	return

# ATTEMPTS TO ACQUIRE MUTEX LOCK
# n : process number
def det_mutex_lock(n, clocks, lock, lrlt, lock_held):
	while True:
		wait_for_turn(n, clocks)
		if not lock_held:
			lock.acquire()
			if lrlt >= clocks[n]:
				lock.release()
			else:
				# error checking
				global_lock.acquire()
				print "Process", n, "Locking"
				print clocks
				print '\n'
				global_lock.release()
				break
		clocks[n] += 1
	clocks[n] += 1

def det_mutex_unlock(n, clocks, lock, lrlt_list, lock_held_list, lock_number):
	lrlt_list[lock_number] = clocks[n]
	lock_held_list[lock_number] = 0
	lock.release()
	clocks[n] += 1

	# error checking
	global_lock.acquire()
	print "Process", n, "Unlocking"
	print clocks
	print '\n'
	global_lock.release()
####################################################################################

if __name__ == "__main__":
	# MAXIMUM NUMBER OF PROCESSES AND NUMBER OF LOCKS
	# with current code, these values need to be specified
	max_processes = 5
	num_locks = 2

	# CREATE LOCK TO SHARE BETWEEN PROCESS
	# we can create any number of locks depending on synchronization needs
	manager = multiprocessing.Manager()
	lock0 = manager.Lock()
	lock1 = manager.Lock()


	# CREATE LIST WITH DETERMINISTIC LOGICAL CLOCKS 
	# FOR EACH PROCESS
	clocks = manager.list([0] * max_processes)

	# CREATE LIST WITH RELEASE TIME FOR EACH LOCK
	# lrlt : lock released locical time list
	lrlt_list = manager.list([0] * num_locks)

	# CREATE LIST WITH LOCK HELD BOOLEAN
	lock_held_list = manager.list([0] * num_locks)

	# RUN PROCESSES
	p = range(max_processes)
	for i in xrange(max_processes):
		p[i] = multiprocessing.Process(target=process,  
							    args=(i, lock0, lock1, clocks, lrlt_list, lock_held_list))
		p[i].start()

	# WAIT FOR PROCESSES TO END
	for i in xrange(max_processes):
		p[i].join()
