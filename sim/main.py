import argparse
import yaml
from simulation import Simulation

if __name__ == '__main__':

    parser = argparse.ArgumentParser()
    parser.add_argument('--config', type=str, required=True)
    parser.add_argument('--cloudtype', type=str, required=True)
    config = parser.parse_args().config
    cloudtype = parser.parse_args().cloudtype

    with open(config, "r") as stream:
        try:
            args = yaml.safe_load(stream)
        except yaml.YAMLError as exc:
            print(exc)
    
    jobname = args['jobname']
    minpts = args['minpts']
    maxpts = args['maxpts']
    interval = args['interval']
    batch = args['batch']
    numrunsper = args['numrunsper']
    comps = args['comps']
    anoms = args['anoms']

    simulation = Simulation(
        jobname=jobname,
        minpts=minpts,
        maxpts=maxpts,
        interval=interval,
        numrunsper=numrunsper,
        batch=batch,
        cloudtype=cloudtype,
        which_comps=comps,
        anomalies=anoms
    )
    simulation.simulate()
