#!/usr/bin/env python

#stdlib imports
import argparse
import sys
import time
import os, os.path

import sensorloc

#third party imports
from obspy import UTCDateTime

def main(options, parser):
    streams = sensorloc.Streams()
    # parse Mini-SEED files
    try:
        for f in options.miniseeds:
            streams.addFile(f)
        extent = streams.getTimeExtent(True)
    except Exception,msg:
        print 'Error reading Mini-SEED: "%s"' % msg
        parser.print_help()
        sys.exit(1)
    # when verbose, list loaded streams
    if options.verbose:
        print streams
    # filter traces
    streams.simulate(
            responses=sensorloc.Responses(options.responseDirectory),
            response_units=options.responseUnits,
            pre_filt=options.prefilt,
            taper=options.taper)
    # trim traces after filtering
    try:
        if options.startTime is not None or options.endTime is not None:
            streams.trim(starttime=options.startTime, endtime=options.endTime)
    except Exception,msg:
        print 'Error trimming: "%s"' % msg
    # run bandpass filter
    if options.filter:
        streams.filter('bandpass',
                freqmin=options.freqmin,
                freqmax=options.freqmax,
                corners=options.corners)
    # write output
    if not os.path.isdir(options.outputDirectory):
        os.makedirs(options.outputDirectory)
    try:
        suffix = ''
        if options.simulate:
            suffix += '.d'
        if options.filter:
            suffix += '.f'
        streams.write(options.outputDirectory, encoding='FLOAT64', suffix=suffix)
    except Exception,msg:
        print 'Error writing output: "%s"' % msg
    # generate plot
    if options.plot:
        streams.plot()




# when script is run instead of imported
if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Filter Mini-SEED files')

    parser.add_argument('miniseeds', metavar='SEED', nargs='+',
            help='Mini-SEED files to process')
    parser.add_argument('-v', '--verbose', dest='verbose', action='store_true')
    parser.add_argument('-p', '--plot', default=False, action='store_true',
            help='Save a plot (PNG format) of the chopped data.')
    parser.add_argument('--outputDirectory', default='.',
            help='Output directory for processed Mini-SEED files')
    parser.add_argument('--simulate', default=False, action='store_true',
            help='Remove instrument response using RESP files')
    parser.add_argument('--prefilt', default=None, nargs=4, type=float,
            help='Bandpass filter to apply before simulate, 4 corner frequencies')
    parser.add_argument('--responseDirectory', default='.',
            help='Directory with response files for traces in input Mini-SEEDs')
    parser.add_argument('--responseUnits', default='ACC',
            help='Units for simulate call')
    parser.add_argument('--taper', default=False, action='store_true')
    parser.add_argument('--filter', default=False, action='store_true',
            help='Bandpass filter (after) removing instrument response')
    parser.add_argument('--freqmin', type=float, default=None,
            help='Minimum frequency for bandpass filter')
    parser.add_argument('--freqmax', type=float, default=None,
            help='Maximum frequency for bandpass filter')
    parser.add_argument('--corners', type=int, default=4,
            help='Number of corners for bandpass filter')
    parser.add_argument('-s', '--start', dest='startTime', metavar='STARTTIME',
            help='Trim time series (YYYY-MM-DDTHH:MM:SS.sss) after simulate and filter',
            type=UTCDateTime)
    parser.add_argument('-e', '--end', dest='endTime', metavar='ENDTIME',
            help='Trim time series (YYYY-MM-DDTHH:MM:SS.sss) after simulate and filter',
            type=UTCDateTime)

    main(parser.parse_args(),parser)
