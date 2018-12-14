import codecs
import copy
import os
import re
import subprocess
import sys
import time
import unittest

from tfsnippet.utils import TemporaryDirectory, humanize_duration


class ExamplesTestCase(unittest.TestCase):
    """
    Test case to ensure all examples can run for at least one step.
    """

    @unittest.skipUnless(os.environ.get('RUN_EXAMPLES_TEST_CASE') == '1',
                         'RUN_EXAMPLES_TEST_CASE is not set to 1, thus skipped')
    def test_examples_can_run_one_step(self):
        timer = -time.time()

        # discover all example scripts
        def walk(pa, dst):
            for fn in os.listdir(pa):
                fp = os.path.join(pa, fn)
                if os.path.isdir(fp):
                    walk(fp, dst)
                elif fp.endswith('.py'):
                    with codecs.open(fp, 'rb', 'utf-8') as f:
                        cnt = f.read()
                    if re.search(
                            r'''if\s+__name__\s*==\s+(['"])__main__\1:''',
                            cnt):
                        if 'max_step=config.max_step' not in cnt:
                            raise RuntimeError('Example script does not have '
                                               'max_step configuration: {}'.
                                               format(fp))
                        dst.append(fp)
            return dst

        examples_dir = os.path.join(
            os.path.split(os.path.abspath(__file__))[0],
            '../../tfsnippet/examples'
        )
        examples_scripts = walk(examples_dir, [])

        # run all examples scripts for just max_step
        env_dict = copy.copy(os.environ)
        env_dict['MLSTORAGE_EXPERIMENT_ID'] = 'null_id'

        for example_script in examples_scripts:
            print('Run {} ...'.format(example_script))

            with TemporaryDirectory() as tempdir:
                with codecs.open(os.path.join(tempdir, 'config.json'),
                                 'wb', 'utf-8') as f:
                    f.write('{"max_step":1}\n')
                subprocess.check_call([sys.executable, '-u', example_script],
                                      cwd=tempdir, env=env_dict)
                print('')

        # report finished tests
        print('Finished to run {} example scripts in {}.'.format(
            len(examples_scripts), humanize_duration(time.time() + timer)))
