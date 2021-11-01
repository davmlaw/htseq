import pytest
import sys
import os
import glob
import distutils.util
from pathlib import Path
import unittest
import pytest

build_dir = "build/lib.%s-%s" % (distutils.util.get_platform(), sys.version[0:3])

sys.path.insert(0, os.path.join(os.getcwd(), build_dir))
import HTSeq


class TestGenomicArray(unittest.TestCase):
    def test_init(self):
        # Autoallocation
        ga = HTSeq.GenomicArray("auto")

        # Infinite length chromosomes
        ga = HTSeq.GenomicArray(['1', '2'])

        # Fixed chromosomes
        ga = HTSeq.GenomicArray({
            '1': 5898,
            '2': 4876,
        })

        # Store: ndarray
        ga = HTSeq.GenomicArray({
            '1': 5898,
            '2': 4876,
            },
            storage='ndarray',
        )

        # Store: memmap
        ga = HTSeq.GenomicArray({
            '1': 5898,
            '2': 4876,
            },
            storage='memmap',
            memmap_dir='.',
        )

    def test_steps(self):
        for storage in ['step', 'ndarray']:
            ga = HTSeq.GenomicArray({
                '1': 5898,
                '2': 4876,
                },
                storage=storage,
            )
            steps = ga.steps()
            steps_exp = [
                (HTSeq.GenomicInterval('1', 0, 5898, strand='+'), 0),
                (HTSeq.GenomicInterval('1', 0, 5898, strand='-'), 0),
                (HTSeq.GenomicInterval('2', 0, 4876, strand='+'), 0),
                (HTSeq.GenomicInterval('2', 0, 4876, strand='-'), 0),
            ]
            for step, step_exp in zip(steps, steps_exp):
                self.assertEqual(step, step_exp)



if __name__ == '__main__':

    suite = TestGenomicArray()
    suite.test_init()
