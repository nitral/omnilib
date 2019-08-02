import collections
import inspect
import multiprocessing

import dill

_MapArgs = collections.namedtuple("_MapArgs", ["fn", "arg"])


class MRJobInputIterator(object):
    def __init__(self, mrjob_input, start=0):
        self.current = start
        self.args = mrjob_input.args
        self.total_inputs = len(self.args)
        if start >= self.total_inputs:
            raise ValueError("Start index out of range! Passed: {}, Max: {}", format(
                start, self.total_inputs - 1))
        self.serialized_map_fn = mrjob_input.serialized_map_fn

    def __iter__(self):
        return self

    def __next__(self):
        if self.current >= self.total_inputs:
            raise StopIteration()
        if self.serialized_map_fn is not None:
            to_return = _MapArgs(fn=self.serialized_map_fn,
                                 arg=dill.dumps(self.args[self.current]))
        else:
            to_return = self.args[self.current]
        self.current += 1
        return to_return


class MRJobInput(object):
    """Creates an iterable Input for the MRJob."""

    def __init__(self, inputs=None):
        if not inputs == None:
            self.args = inputs
        else:
            self.args = []
        self.serialized_map_fn = None

    def add_input(self, input):
        if input == None:
            raise ValueError("Input to a MRJob cannot be None!")
        self.args.append(input)
        return self

    def _set_map_fn(self, map_fn):
        self.serialized_map_fn = dill.dumps(map_fn)

    def __iter__(self):
        return MRJobInputIterator(self)

    def __len__(self):
        return len(self.args)


class MRJob(object):
    """Creates a multi-process MapReduce-based computation job.

    Uses a Pool to spawn single-threaded Map-phase workers who are assigned
    tasks on a rolling basis. After the map-phase finishes, all results are
    sent to a single-threaded single-process reduce function to emit the final
    result.
    """

    def __init__(self, num_processes=None, map_fn=None, reduce_fn=None, pool=None):
        """Creates a MRJob object.

        Args:
            num_processes (int): Map-phase worker pool size.
                If not specified or if `None` is passed, the result is
                dependent on `multiprocessing.Pool`.
            map_fn (function): The map-phase worker function.
                The function is executed by a single thread in each worker.
            reduce_fn (function): The final reduce function in the MR Job.
            pool (multiprocessing.Pool): An external worker-pool for the Map-phase
                An external pool cannot be sent along with `num_processes`
        """
        if num_processes is not None and num_processes <= 0:
            raise ValueError("Number of processes must be a positive integer!")
        elif not callable(map_fn):
            raise ValueError("Mapping function must be callable!")
        elif not callable(reduce_fn):
            raise ValueError("Reducer function must be callable!")
        elif pool is not None and num_processes is not None:
            raise ValueError(
                "Multiprocessing Pool and Number of Processes cannot be passed at the same time!")

        self.num_processes = num_processes
        self.map_fn = map_fn
        self.reduce_fn = reduce_fn

        # Initialize Pool of Workers
        if pool is not None:
            self.external_pool = True
            self.pool = pool
        else:
            self.external_pool = False
            self.pool = multiprocessing.Pool(processes=self.num_processes)

    def __del__(self):
        if self.external_pool is not None:
            self.pool.close()
            self.pool.join()

    def run(self, args=None):
        """Starts running the Map-Reduce job.

        Forwards the passed arguments to the map-phase workers.
        NOTE: It does not `close` or `join` the pool after completion.
        """
        # Create tasks as MRJobInput. This lets us generate the serialized Map Function on the fly.
        if not isinstance(args, MRJobInput):
            mrjob_input = MRJobInput(inputs=args)
        else:
            mrjob_input = args
        mrjob_input._set_map_fn(self.map_fn)

        # Run Mappers
        map_results = self.pool.map(func=_run_mapper, iterable=mrjob_input)

        # Run Reducer on mapper results and return
        return self.reduce_fn(map_results)


def _run_mapper(args):
    # Extract Mapper Arguments
    arg = dill.loads(args.arg)
    fn = dill.loads(args.fn)

    # Unpack arguments if the mapper function expects it. Then call the extracted mapper function.
    try:
        try_iterable = iter(arg)
    except TypeError:
        return fn(arg)
    else:
        if len(inspect.signature(fn).parameters) == len(arg) and len(arg) > 1:
            return fn(*arg)
        else:
            return fn(arg)
