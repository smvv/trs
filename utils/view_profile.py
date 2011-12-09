#!/usr/bin/python
import sys
from pstats import Stats

s = Stats(sys.argv[1])

for profile in sys.argv[2:]:
    s.add(profile)

s.sort_stats('cumulative')

s.print_stats()

