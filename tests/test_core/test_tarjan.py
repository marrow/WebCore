# encoding: utf-8

from unittest import TestCase

from web.core.tarjan import strongly_connected_components, topological_sort, robust_topological_sort

scc = strongly_connected_components
ts = topological_sort
rtc = robust_topological_sort


class TestTarjan(TestCase):
    GOOD = dict(foo=['bar'], bar=[], baz=['foo'])
    BAD = dict(foo=['bar'], bar=['baz'], baz=['bar'])
    MISSING = dict(foo=['bar'], bar=['baz'])
    
    def test_strongly_connected_components_good(self):
        # standard (no tricks) dependency graph
        self.assertEquals(scc(self.GOOD), [('bar', ), ('foo', ), ('baz', )])
    
    def test_strongly_connected_components_bad(self):
        # baz and bar depend on each-other
        self.assertEquals(scc(self.BAD), [('baz', 'bar'), ('foo', )])
    
    def test_strongly_connected_components_ugly(self):
        # a dependency is missing so we explode
        self.assertRaises(KeyError, scc, self.MISSING)
    
    def test_topological_sort_good(self):
        # resolved from most dependent to least
        self.assertEquals(ts(self.GOOD), ['baz', 'foo', 'bar'])
    
    def test_topological_sort_bad(self):
        # only resolvable items are returned
        self.assertEquals(ts(self.BAD), ['foo'])
    
    def test_topological_sort_ugly(self):
        self.assertRaises(KeyError, ts, self.MISSING)
    
    def test_robust_topological_sort_good(self):
        # return parallel sets from least to most dependent
        self.assertEquals(rtc(self.GOOD), [('baz', ), ('foo', ), ('bar', )])

    def test_robust_topological_sort_bad(self):
        # like the strongly connected components, but reversed
        self.assertEquals(rtc(self.BAD), [('foo', ), ('baz', 'bar')])

    def test_robust_topological_sort_ugly(self):
        # as per the other ugly cases, we expect to bomb
        self.assertRaises(KeyError, rtc, self.MISSING)
