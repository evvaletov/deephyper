import argparse
import os
import csv
import time
import logging
from importlib import import_module
from importlib.util import find_spec

class OptConfig:
    '''Optimizer-related options'''

    def __init__(self, args):
        HERE = os.path.dirname(os.path.abspath(__file__)) # search dir
        package = os.path.basename(os.path.dirname(HERE)) # 'deephyper'

        self.backend = args.backend
        self.max_evals = args.max_evals 
        self.individuals_per_worker = args.individuals_per_worker 
        self.ga_num_gen = args.ga_num_gen 
        self.evaluator = args.evaluator
        self.repeat_evals = args.repeat_evals
        self.num_workers = args.num_workers
        self.uniform_sampling = args.uniform_sampling
        
        # for example, the default value of args.benchmark is "b1.addition_rnn"
        benchmark_directory = args.benchmark.split('.')[0] # "b1"
        self.benchmark = args.benchmark
        problem_module_name = f'{package}.benchmarks.{benchmark_directory}.problem'
        problem_module = import_module(problem_module_name)

        # get the path of the b1/addition_rnn.py file here:
        self.benchmark_module_name = f'{package}.benchmarks.{args.benchmark}'
        self.benchmark_filename = find_spec(self.benchmark_module_name).origin
        
        # create a problem instance and configure the skopt.Optimizer
        instance = problem_module.Problem()
        self.params = list(instance.params)
        self.starting_point = instance.starting_point
        
        spaceDict = instance.space
        self.space = [spaceDict[key] for key in self.params]

def sk_optimizer_from_config(opt_config, random_state):
    from skopt import Optimizer
    from deephyper.search.ExtremeGradientBoostingQuantileRegressor import \
         ExtremeGradientBoostingQuantileRegressor
    logger = logging.getLogger(__name__)
    if opt_config.uniform_sampling:
        optimizer = Optimizer(
            opt_config.space,
            base_estimator='dummy',
            acq_optimizer='sampling',
            random_state=random_state,
            n_initial_points=np.inf
        )
        logger.info("Creating skopt.Optimizer with 'dummy' base_estimator")
    else:
        optimizer = Optimizer(
            opt_config.space,
            base_estimator=ExtremeGradientBoostingQuantileRegressor(),
            acq_optimizer='sampling',
            acq_func='LCB',
            acq_func_kwargs={'kappa':0},
            random_state=random_state,
            n_initial_points=opt_config.num_workers
        )
        logger.info("Creating skopt.Optimizer with XGB base_estimator")
    return optimizer

def conf_logger():
    logger = logging.getLogger('deephyper')

    handler = logging.FileHandler('deephyper.log')
    formatter = logging.Formatter(
        '%(asctime)s|%(process)d|%(levelname)s|%(name)s:%(lineno)s] %(message)s', 
        "%Y-%m-%d %H:%M:%S"
    )
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    logger.setLevel(logging.DEBUG)
    logger.info("\n\nLoading Deephyper\n--------------")
    return logger

class DelayTimer:
    def __init__(self, max_minutes=None, period=2):
        if max_minutes is None:
            max_minutes = float('inf')
        self.max_minutes = max_minutes
        self.max_seconds = max_minutes * 60.0
        self.period = period
        self.delay = True

    def pretty_time(self, seconds):
        '''Format time string'''
        seconds = round(seconds, 2)
        minutes, seconds = divmod(seconds, 60)
        hours, minutes = divmod(minutes, 60)
        return "%02d:%02d:%02.2f" % (hours,minutes,seconds)

    def __iter__(self):
        start = time.time()
        nexttime = start + self.period
        while True:
            now = time.time()
            elapsed = now - start
            if elapsed > self.max_seconds:
                raise StopIteration
            else:
                yield self.pretty_time(elapsed)
            tosleep = nexttime - now
            if tosleep <= 0 or not self.delay:
                nexttime = now + self.period
            else:
                nexttime = now + tosleep + self.period
                time.sleep(tosleep)


def create_parser():
    '''Command line parser'''
    parser = argparse.ArgumentParser()

    parser.add_argument("--benchmark", default='b1.addition_rnn',
                        help="name of benchmark module (e.g. b1.addition_rnn)"
                       )
    parser.add_argument("--backend", default='tensorflow',
                        help="Keras backend module name"
                       )
    parser.add_argument('--max-evals', type=int, default=100,
                        help='maximum number of evaluations'
                       )
    parser.add_argument('--num-workers', type=int, default=10,
                        help='Number of points to ask for initially'
                       )
    parser.add_argument('--ga-individuals-per-worker', type=int, default=10,
                        help='Initial population is num_workers *'
                        ' ind-per-worker', dest='individuals_per_worker'
                       )
    parser.add_argument('--ga-num-gen', type=int, default=40)
    parser.add_argument('--uniform-sampling', action='store_true',
                        default=False, help='for skopt optimizers; use dummy'
                        ' base_estimator (default is False)'
                       )
    parser.add_argument('--from-checkpoint', default=None,
                        help='path of checkpoint file from a previous run'
                       )
    parser.add_argument('--evaluator', default='balsam')
    parser.add_argument('--repeat-evals', action='store_true',
                        help='Re-evaluate points visited by hyperparameter optimizer'
                       )
    return parser