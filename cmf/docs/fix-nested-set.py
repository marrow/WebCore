#!/usr/bin/env python2.5
"""Repair a broken nested set structure.

This repair script should not alter the order of items unless the nested set structure is -severely- broken."""


from gothcandy import model


class Foo(object):
    def nest(self, parent, n, l=0):
        o = n
        parent.l = o
        for m, i in enumerate(parent.children):
            o = self.nest(i, o + 1, l+1)
        parent.r = o + 1
        print ("  " * l) + "Parent l=%d, r=%d, return=%d\t%r" % (parent.l, parent.r, o + 1, parent)
        return o + 1

if __name__ == '__main__':
    try:
        a = Foo()
        root = model.Asset.query.filter_by(l=1).one()
        
        a.nest(root, 1)
        
        model.DBSession.commit()
    
    except:
        print "!!! There was an error recreating the nested set structure."
        print "I hope you have backups."
        
        model.DBSession.rollback()
        
        raise
    
    else:
        print "Nested set structure recreated successfully."
        print "If you could file a bug report with instructions to reproduce the break, it'd be appreciated."
