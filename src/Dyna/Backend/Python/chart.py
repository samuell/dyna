from collections import defaultdict
from utils import notimplemented
from defn import aggregator
from term import Term, _repr


class Chart(object):

    def __init__(self, name, arity, agg_name):
        self.name = name
        self.arity = arity
        self.intern = {}   # args -> term
        self.ix = [defaultdict(set) for _ in xrange(arity)]
        self.agg_name = agg_name

    def new_aggregator(self):
        return aggregator(self.agg_name)

    def __repr__(self):
        rows = [term for term in self.intern.values() if term.value is not None]
        x = '\n'.join('%-30s := %s' % (term, _repr(term.value)) for term in sorted(rows))
        return '%s\n=================\n%s' % (self.name, x)

    def __getitem__(self, s):
        assert len(s) == self.arity + 1, \
            'Chart %r: item width mismatch: arity %s, item %s' % (self.name, self.arity, len(s))

        args, val = s[:-1], s[-1]

        assert val is not None

        # filter set of candidates by each bound argument
        b = [(ix[x]) for (ix, x) in zip(self.ix, args) if not isinstance(x, slice)]

        if len(b) == 0:
            # all arguments are free.
            candidates = self.intern.itervalues()

        elif len(b) == 1:
            candidates = iter(b[0])

        else:
            b.sort(key=len)           # start with smaller ones
            candidates = b[0] & b[1]
            for ix in b[2:]:
                candidates &= ix
            candidates = iter(candidates)

        # handle the value column separately because we don't index it yet.
        if isinstance(val, slice):
            for term in candidates:
                if term.value is not None:
                    yield term, term.args, term.value
        else:
            for term in candidates:
                if term.value == val:
                    yield term, term.args, term.value

    def insert(self, args):        # TODO: rename
        try:
            return self.intern[args]
        except KeyError:
            self.intern[args] = term = Term(self.name, args)
            term.aggregator = self.new_aggregator()
            # index new term
            for i, x in enumerate(args):
                self.ix[i][x].add(term)
            return term