import multiprocessing
import unittest

from omnilib import compute as c


class TestMRJob(unittest.TestCase):
    def test_map(self):
        def map(num):
            return num

        def reduce(arr):
            return arr

        inputs = [1, 2, 3, 4]
        job = c.MRJob(num_processes=2, map_fn=map, reduce_fn=reduce)
        self.assertEqual(job.run(inputs), inputs)

    def test_reduce(self):
        def map(num):
            return num

        def reduce(arr):
            return sum(arr)

        inputs = [1, 2, 3, 4]
        job = c.MRJob(num_processes=2, map_fn=map, reduce_fn=reduce)
        self.assertEqual(job.run(inputs), 10)

    def test_external_pool(self):
        def map(num1, num2):
            return num1 + num2

        def reduce(arr):
            return sum(arr)

        external_pool = multiprocessing.Pool(processes=2)
        job = c.MRJob(pool=external_pool, map_fn=map, reduce_fn=reduce)
        inputs = c.MRJobInput().add_input(
            [1, 2]).add_input([2, 3]).add_input([3, 4])
        self.assertEqual(job.run(inputs), 15)

    def test_mrjobinput_add_input(self):
        inputs = [1, 2, 3, 4, 5]
        mr_job_inputs = c.MRJobInput()
        for val in inputs:
            mr_job_inputs.add_input(val)
        for i, val in enumerate(mr_job_inputs):
            self.assertEqual(inputs[i], val)

    def test_mrjobinput_input_init(self):
        inputs = [1, 2, 3, 4, 5]
        mr_job_inputs = c.MRJobInput(inputs)
        for i, val in enumerate(mr_job_inputs):
            self.assertEqual(inputs[i], val)

    def test_reducer_augment_input(self):
        def map(arr):
            return arr

        def reduce(arr):
            total = 0
            for val in arr:
                total += sum(val)
            return (arr, total)

        inputs = [[1, 2], [2, 3], [3, 4], [4, 5]]
        job = c.MRJob(num_processes=2, map_fn=map, reduce_fn=reduce)
        result_tuple = job.run(inputs)
        # Check Sum
        self.assertEqual(result_tuple[1], 24)
        # Check if mapper output is forwarded properly.

        self.assertTrue(result_tuple[0] == inputs)


if __name__ == '__main__':
    unittest.main()
