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
	det_mutex_lock(n, clocks, lock0, lrlt_list, lock_held_list, 0)

	det_mutex_lock(n, clocks, lock1, lrlt_list, lock_held_list, 1)
	det_mutex_unlock(n, clocks, lock1, lrlt_list, lock_held_list, 1)

	det_mutex_unlock(n, clocks, lock0, lrlt_list, lock_held_list, 0)
	clocks[n] = 10000
####################################################################################

####################################################################################
# KENDO FUNCTIONS

# WAITS FOR DETERMINISTIC LOGICAL CLOCK TO BE GLOBAL MINIMUM
# n : process number
# clocks : list of deterministic logical clocks
def wait_for_turn(n, clocks):
	process_clock_value = clocks[n]
	while True:
		# error checking
		print n, clocks

		if process_clock_value < min(clocks) or \
		   (process_clock_value == min(clocks) and n == clocks.index(min(clocks))):
			break
	return

# ATTEMPTS TO ACQUIRE MUTEX LOCK
# n : process number
def det_mutex_lock(n, clocks, lock, lrlt_list, lock_held_list, lock_number):
	while True:
		wait_for_turn(n, clocks)

		# error checking
		global_lock.acquire()
		print "Process", n, "'s Turn with Lock", lock_number
		print clocks
		print lrlt_list
		print '\n'
		global_lock.release()

		global_lock.acquire()
		if try_lock(lock, lock_held_list, lock_number):
			global_lock.release()
			if lrlt_list[lock_number] >= clocks[n]:
				# atomically release and label lock as not held
				global_lock.acquire()
				lock.release()
				lock_held_list[lock_number] = 0
				global_lock.release()
			else:
				# error checking
				global_lock.acquire()
				print "Process", n, "Locking Lock", lock_number
				print clocks
				print '\n'
				global_lock.release()
				break
		else:
			global_lock.release()
		clocks[n] += 1
	clocks[n] += 1

def det_mutex_unlock(n, clocks, lock, lrlt_list, lock_held_list, lock_number):
	# atomically release and label lock as not held
	global_lock.acquire()
	lock_held_list[lock_number] = 0
	lrlt_list[lock_number] = clocks[n]
	lock.release()
	clocks[n] += 1

	# error checking
	print "Process", n, "Unlocking Lock", lock_number
	print clocks
	print lrlt_list[lock_number]
	print '\n'
	global_lock.release()

# returns True if lock is free and acquires lock, returns False if lock is not free
def try_lock(lock, lock_held_list, lock_number):
	if not lock_held_list[lock_number]:
		lock_held_list[lock_number] = 1
		lock.acquire()
		return True
	else:
		return False

def pause_logical_clock():
	return

def resume_logical_clock():
	return

def incriment_logical_clock():
	return 
####################################################################################

if __name__ == "__main__":
	# MAXIMUM NUMBER OF PROCESSES AND NUMBER OF LOCKS
	# with current code, these values need to be specified
	max_processes = 4
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
	# lrlt : lock released logical time list
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
