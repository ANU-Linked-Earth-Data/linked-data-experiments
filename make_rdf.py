#!/usr/bin/env python3
from argparse import ArgumentParser, FileType
from collections import namedtuple
from datetime import datetime
from json import load, dumps, JSONEncoder
from pytz import timezone
from rdflib import Graph, Literal, Namespace, RDF, URIRef
from urllib.parse import quote_plus

LDE = Namespace('http://example.com/lde#')
GEO = Namespace('http://www.w3.org/2003/01/geo/wgs84_pos#')
LGDDS = Namespace('http://www.example.com/linkedGDDS#')
OWL = Namespace('http://www.w3.org/2002/07/owl#')

Accident = namedtuple('Accident', ['locations', 'uri', 'message', 'datetime'])
Location = namedtuple('Location', ['lat', 'lon', 'street', 'suburb', 'uri'])


def parse_date(date_str):
    # Parse string (no timezone)
    rest = date_str[:-4]
    time_format = '%Y-%m-%d%H:%M:%S'
    dt = datetime.strptime(rest, time_format)

    # Now get right timezone
    tz = timezone('Australia/Canberra')
    assert date_str[-4:] in {'AEDT', 'AEST'}
    # We don't even have to handle the AEDT/AEST case because pytz is smart
    # enough to do it for us
    dt = tz.localize(dt)

    return dt


def accident_data(tweet):
    if not tweet['mentioned_locations']:
        return None
    uri = 'http://example.com/accidents/{}'.format(tweet['id'])
    locs = []
    for loc_dict in tweet['mentioned_locations']:
        lat, lon = loc_dict['coords']
        street, suburb = loc_dict['name']
        loc_uri = 'http://example.com/streets/{}/{}'.format(
            *map(quote_plus, [street, suburb])
        )
        locs.append(Location(
            lat=lat, lon=lon, street=street, suburb=suburb, uri=loc_uri
        ))
    return Accident(
        locations=locs, uri=uri, message=tweet['normalised'],
        datetime=parse_date(tweet['datetime'])
    )


def slow(generator, suffix, interval=500, total=None):
    tot_str = '/' + str(total) if total is not None else ''
    for idx, val in enumerate(generator):
        if idx % interval == 0:
            print('{}{} {}'.format(idx, tot_str, suffix))
        yield val


def accident_triples(tweet, data, ident):
    """Produces some triples describing a single accident, identified by ident.
    The identifier can then be stuck in a CoverageJSON-like document."""
    rv = [
        (ident, RDF.type, LDE.Accident),
        (ident, LDE.description, Literal(tweet['normalised']))
    ]
    for loc in data.locations:
        loc_uri = URIRef(loc.uri)
        rv.append((ident, LDE.location, loc_uri))
        rv.append((loc_uri, RDF.type, LDE.Street))
        rv.append((loc_uri, LDE.streetName, Literal(loc.street)))
        rv.append((loc_uri, LDE.suburbName, Literal(loc.suburb)))
        rv.append((loc_uri, GEO.lat, Literal(loc.lat)))
        rv.append((loc_uri, GEO['long'], Literal(loc.lon)))  # heh
    return rv


class DatetimeJSONEncoder(JSONEncoder):
    def default(self, obj):
        if isinstance(obj, datetime):
            return obj.isoformat()
        return super().default(obj)


def accident_coverage_triples(txy_list, accident_urls):
    assert len(txy_list) == len(accident_urls)
    axis = LDE.AccidentAxis
    cov = LDE.AccidentDataCoverage
    dom = LDE.AccidentDataDomain
    rng = LDE.AccidentDataRange

    # Boilerplate for coverage and domain
    yield from [
        (cov, RDF.type, OWL.NamedIndividual),
        (cov, RDF.type, LGDDS.Coverage),
        (cov, LGDDS.hasDomain, dom),
        (cov, LGDDS.hasRange, rng),
        (dom, RDF.type, OWL.NamedIndividual),
        (dom, RDF.type, LGDDS.txyTrajectoryDomain),
        (cov, LGDDS.hasAxis, axis)
    ]

    # Domain for the accidents
    json_txy = dumps(txy_list, cls=DatetimeJSONEncoder)
    json_components = dumps(['t', 'x', 'y'])
    yield from [
        (axis, RDF.type, OWL.NamedIndividual),
        (axis, RDF.type, LGDDS.txyTupleAxis),
        (axis, LGDDS.axisSize, Literal(len(txy_list))),
        (axis, LGDDS.axisValues, Literal(json_txy)),
        (axis, LGDDS.tupleComponents, Literal(json_components))
    ]

    # Range for the accident
    json_urls = dumps(accident_urls)
    yield from [
        (rng, RDF.type, OWL.NamedIndividual),
        (rng, RDF.type, LGDDS.Range),
        (rng, LGDDS.hasDataType, LGDDS.StringDataType),
        (rng, LGDDS.rangeValues, Literal(json_urls))
    ]


def build_graph(tweets):
    rv = Graph()
    rv.namespace_manager.bind('lde', LDE)
    rv.namespace_manager.bind('linkedgdds', LGDDS)
    rv.namespace_manager.bind('owl', OWL)

    # These two lists will be used to construct the coverage
    txy_list = []
    accident_url_list = []

    for tweet in slow(tweets, 'tweets processed so far', total=len(tweets)):
        data = accident_data(tweet)
        if data is None:
            continue
        ident = URIRef(data.uri)
        # First add data describing the accident
        for triple in accident_triples(tweet, data, ident):
            rv.add(triple)

        # Build up lists necessary to produce coverage
        t = data.datetime
        for loc in data.locations:
            x = loc.lon
            y = loc.lat
            txy_list.append((t, x, y))
            accident_url_list.append(ident)

    for triple in accident_coverage_triples(txy_list, accident_url_list):
        rv.add(triple)

    return rv

parser = ArgumentParser()
parser.add_argument(
    '--tweets', type=FileType('r'), default='data/tweets.json'
)
parser.add_argument(
    '--streets', type=FileType('r'), default='data/streets.json'
)
parser.add_argument(
    '--out', type=FileType('wb'), default='data/accidents.ttl'
)

if __name__ == '__main__':
    args = parser.parse_args()
    streets = load(args.streets)
    tweets = load(args.tweets)
    print('Loaded {} tweets and {} streets'.format(len(tweets), len(streets)))
    graph = build_graph(tweets)
    graph.serialize(args.out, format='turtle')
    print('Result written to', args.out.name)
