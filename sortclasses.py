import re
from collections import defaultdict
from datetime import date, datetime
from getschedule import getSchedule
import pandas as pd

schedulelink = getSchedule(date.today())
abbreviations_file = 'building_abbreviations.txt'


abbreviations = []
buildings = defaultdict(lambda: defaultdict(dict))

with open(abbreviations_file, "r+") as f:
    abbreviations = [line.strip() for line in f]
    abbreviations = set(abbreviations)

colnames = ['campus', 'M', 'T', 'W', 'R', 'F', 'start', 'end', 'facility']


# --> last 3 char are always numbers, sometimes there's a space though like BOUSA 106 or such...
# though some end in A,F etc

def sortdays(times, mon, tues, weds, thurs, fri):
    days = {'M': mon, 'T': tues, 'W': weds, 'R': thurs, 'F': fri}
    inclass = {}

    for d in days:  # this is awful but idk best way rn
        d1 = days[d].replace('Y', '1')
        d1 = d1.replace('N', '0')
        days[d] = int(d1)
        if days[d] == 1:
            inclass[d] = times

    return inclass


# Converts from HH:MM:SS AM/PM format into 24hr time HH:MM
def converttime(time):
    t1 = datetime.strptime(time, '%I:%M:%S %p')
    return datetime.strftime(t1, '%H:%M')


badfacilities = []


def sortbuildings(facility):
    build, room = re.split(r'(^[^\d]+)', facility)[1:]
    build = build.strip()

    if build in abbreviations:
        if room not in buildings[build]:
            buildings[build][room] = {'M': [], 'T': [], 'W': [], 'R': [], 'F': []}
        return build, room
    else:
        actualbuild = ''
        actualroom = ''
        firstpart = facility[:4]
        nonums = facility[:-3]

        if firstpart in abbreviations:
            actualbuild = firstpart
            actualroom = facility[4:]
        elif nonums in abbreviations:
            actualbuild = nonums
            actualroom = facility[-3:]
        else:
            badfacilities.append(facility)
            return None, None

        if actualroom not in buildings[actualbuild]:
            buildings[build][room] = {'M': [], 'T': [], 'W': [], 'R': [], 'F': []}
        return actualbuild, actualroom


# df = pd.read_excel(io=file, header=0, usecols="E, U:Y, AB, AC, AH", names=colnames)
df = pd.read_excel(schedulelink, header=0, usecols="E, U:Y, AB, AC, AH", names=colnames)
df.dropna(inplace=True)
df.drop(df[df['campus'] != "Storrs"].index, inplace=True)
df.drop(df[df['facility'] == 'WWWONLINE'].index, inplace=True)
df.drop(df[df['start'] == '.'].index, inplace=True)
df.reset_index(drop=True, inplace=True)

# df2 = pd.DataFrame(np.nan, index=[0, 1], columns=['building', 'room', ''])
failures = []

for index, row in df.iterrows():
    build, room = sortbuildings(row['facility'])
    if build is None:
        continue
    times = (converttime(row['start']), converttime(row['end']))
    inclass = sortdays(times, row['M'], row['T'], row['W'], row['R'], row['F'])

    for day in inclass:
        t = inclass[day]
        try:
            buildings[build][room][day].append(t)
        except KeyError:
            fail = [type(buildings[build][room]), index, buildings[build][room]]
            failures.append(fail)

with open('failures.txt', "w+") as f:
    for fail in failures:
        f.write(str(fail) + '\n')
with open('badfacilities.txt', "w+") as f:
    facilities = set()
    # It seems like mostly
    for bad in badfacilities:
        if bad not in facilities:
            f.write(str(bad) + '\n')
            facilities.add(bad)

builds = []
frames = []

for building, roomdata in buildings.items():
    builds.append(building)
    frames.append(pd.DataFrame.from_dict(roomdata, orient='index'))

df2 = pd.concat(frames, keys=builds, sort=False)

df2.to_excel('testing.xlsx')

# for building, room in

# df2 = pd.DataFrame.from_dict(buildings, orient='index')
