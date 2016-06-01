import multiprocessing

####################################################################################
# GLOBAL LOCK
# used to make sure output lines print together
# and we have atomicity for certain operations
global_lock = multiprocessing.Lock()
####################################################################################

####################################################################################
# PROCESS
# very basic process
# n : process number
def process(n, lock0, lock1, remaining_time_list, skip_list, lock_held_list):
	det_mutex_lock(n, remaining_time_list, skip_list, lock0, lock_held_list, 0)
	det_mutex_lock(n, remaining_time_list, skip_list, lock1, lock_held_list, 1)

	det_mutex_unlock(n, remaining_time_list, skip_list, lock1, lock_held_list, 1)
	det_mutex_unlock(n, remaining_time_list, skip_list, lock0, lock_held_list, 0)
	remaining_time_list[n] = 10000
	return
####################################################################################

####################################################################################
# KENDO FUNCTIONS

# SHORTEST REMAINING TIME FIRST WAIT
# spins until thread has the shortest remaining time left

# skip_list is used to prevent the thread with highest priority
# spinning on lock that it does not have, resulting in deadlock
def srtf_wait(n, remaining_time_list, skip_list):
	while True:
		# atomically find highest priority process
		global_lock.acquire()
		best_process = 0
		for i in xrange(len(remaining_time_list)):
			if remaining_time_list[i] <= remaining_time_list[best_process] and skip_list[i] != 1:
				best_process = i
		if best_process == n:
			global_lock.release()
			break
		else:
			global_lock.release()
	return

# ATTEMPTS TO ACQUIRE MUTEX LOCK
# n : process number
def det_mutex_lock(n, remaining_time_list, skip_list, lock, lock_held_list, lock_number):
	while True:
		srtf_wait(n, remaining_time_list, skip_list)

		# error checking
		global_lock.acquire()
		
		print "Process", n, "'s Turn with Lock", lock_number
		print remaining_time_list
		print skip_list
		print lock_held_list
		print '\n'
		
		global_lock.release()

		global_lock.acquire()
		if try_lock(lock, lock_held_list, lock_number):
			print "Process", n, "Acquired Lock", lock_number
			remaining_time_list[n] -= 1
			skip_list = [0] * len(skip_list)
			global_lock.release()
			break
		else:
			skip_list[n] = 1
			global_lock.release()

def det_mutex_unlock(n, remaining_time_list, skip_list, lock, lock_held_list, lock_number):
	# atomically release and label lock as not held
	global_lock.acquire()
	lock_held_list[lock_number] = 0
	skip_list = [0] * len(skip_list)
	lock.release()

	# error checking
	print "Process", n, "Unlocking Lock", lock_number
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


	# CREATE LIST WITH REMAINING TIME 
	# FOR EACH PROCESS
	remaining_time_list = manager.list([2] * max_processes)

	# CREATE SKIP LIST
	# lrlt : lock released logical time list
	skip_list = manager.list([0] * max_processes)

	# CREATE LIST WITH LOCK HELD BOOLEAN
	lock_held_list = manager.list([0] * num_locks)

	# RUN PROCESSES
	p = range(max_processes)
	for i in xrange(max_processes):
		p[i] = multiprocessing.Process(target=process,  
							    	   args=(i, lock0, lock1, remaining_time_list, skip_list, lock_held_list))
		p[i].start()

	# WAIT FOR PROCESSES TO END
	for i in xrange(max_processes):
		p[i].join()

		
