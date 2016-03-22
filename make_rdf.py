#!/usr/bin/env python3
from rdflib import Graph, Literal, Namespace, RDF, URIRef
from argparse import ArgumentParser, FileType
from collections import namedtuple
from json import load
from urllib.parse import quote_plus

LDE = Namespace('http://example.com/lde#')
GEO = Namespace('http://www.w3.org/2003/01/geo/wgs84_pos#')

Accident = namedtuple('Accident', ['locations', 'uri', 'message', 'datetime'])
Location = namedtuple('Location', ['lat', 'lon', 'street', 'suburb', 'uri'])


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
        locations=locs, uri=uri, message=tweet['normalised'], datetime=tweet['datetime']
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
        rv.append((loc_uri, GEO['long'], Literal(loc.lon))) # heh
    return rv


def build_graph(tweets):
    # TODO: Should also build coverage according to CovJSON spec here.
    rv = Graph()
    rv.namespace_manager.bind('lde', LDE)
    for tweet in slow(tweets, 'tweets processed so far', total=len(tweets)):
        data = accident_data(tweet)
        if data is None:
            continue
        ident = URIRef(data.uri)
        # First add data describing the accident
        for triple in accident_triples(tweet, data, ident):
            rv.add(triple)
        # Now, for each location mentioned, add the accident to our coverage at
        # that location
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
