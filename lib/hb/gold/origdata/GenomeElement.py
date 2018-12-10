from gold.track.GenomeRegion import GenomeRegion
from gold.util.CommonConstants import BINARY_MISSING_VAL
from gold.util.CustomExceptions import NotSupportedError

class GenomeElement(GenomeRegion):
    @staticmethod
    def createGeFromTrackEl(trackEl, tf, globalCoords=True):
        genomeAnchor = trackEl._trackView.genomeAnchor
        genome = genomeAnchor.genome
        start = None if (tf.isDense() and tf.isInterval()) else trackEl.start()
        end = None if (not tf.isInterval() and not tf.isDense()) else trackEl.end()
        edges = trackEl.edges()[trackEl.edges() != ''] if trackEl.edges() is not None else None
        weights = trackEl.weights()[trackEl.edges() != ''] if trackEl.weights() is not None else None

        if globalCoords:
            chr = genomeAnchor.chr
            if start is not None:
                start += genomeAnchor.start
            if end is not None:
                end += genomeAnchor.start
        else:
            chr = str(genomeAnchor)

        return GenomeElement(genome, chr, start, end, trackEl.val(), trackEl.strand(), \
                             id=trackEl.id(), edges=edges, weights=weights, \
                             extra=dict([(key, getattr(trackEl, key)()) for key in trackEl.getAllExtraKeysInOrder()]), \
                             orderedExtraKeys=trackEl.getAllExtraKeysInOrder())

    def __init__(self, genome=None, chr=None, start=None, end=None, val=None, strand=None, id=None, edges=None, weights=None, extra=None, orderedExtraKeys=None, isBlankElement=False, **kwArgs):
        # __dict__ is used for speedup, so that __setattr__ is not called
        members = self.__dict__
        members['genome'] = genome
        members['chr'] = chr #sequence id (string)
        members['start'] = start #start posision (int, 0-indexed)
        members['end'] = end #end position (int, 0-indexed, end-exclusive)
        members['val'] = val #value (float (number), string (category (n>1) or character (n=1)), int (1 for case, 0 for control, -1 for missing) or lists of the same)
        members['strand'] = strand #DNA strand (int, 1 for '+', 0 for '-', -1 for missing)
        members['id'] = id #unique id (string)
        members['edges'] = edges #ids of linked elements (list of strings)
        members['weights'] = weights #resp. weights of edges (list of values, using similar types as for 'value' above)
        members['isBlankElement'] = isBlankElement

        if extra is None:
            members['orderedExtraKeys'] = [] #keys in extra dict in correct order. Is used instead of OrderedDict because of performance issues
            members['extra'] = {}
        else:
            if orderedExtraKeys is None:
                members['orderedExtraKeys'] = extra.keys()
            else:
                members['orderedExtraKeys'] = orderedExtraKeys
            members['extra'] = dict(extra) #dict of extra columns, from column name (str) -> contents (str)

        for kw in kwArgs:
            members['orderedExtraKeys'].append(kw)
            members['extra'][kw] = kwArgs[kw]

    def __copy__(self):
        raise NotSupportedError('Shallow copy.copy() of GenomeElement objects is not supported, '
                                'as this produces unwanted effects. Please use instance method '
                                'getCopy() or copy.deepcopy() instead. getCopy() is by far the '
                                'most efficient of the two.')

    def getCopy(self):
        extraCopy = dict(self.extra)
        orderedExtraKeysCopy = list(self.orderedExtraKeys)
        return GenomeElement(self.genome, self.chr, self.start, self.end, self.val, self.strand, self.id, self.edges, self.weights, extraCopy, orderedExtraKeysCopy)

    def __getattr__(self, item):
        try:
            return self.__dict__['extra'][item]
        except KeyError:
            raise AttributeError('GenomeElement object does not contain extra '
                                 'key: "%s". Extra contents: %s'
                                 % (item, self.__dict__['extra']))

    def __setattr__(self, item, value):
        if item not in self.__dict__ and 'extra' in self.__dict__:
            if item not in self.__dict__['extra']:
                self.__dict__['orderedExtraKeys'].append(item)
            self.__dict__['extra'][item] = value
        else:
            object.__setattr__(self, item, value)

    def __str__(self):
        #return self.toStr()

        #self.start+1 because we want to show 1-indexed, end inclusive output
        return (str(self.chr) + ':' if not self.chr is None else '')\
            + (str(self.start+1) if not self.start is None else '')\
            + ('-' + str(self.end) if not self.end is None else '')\
            + ((' (Pos)' if self.strand else ' (Neg)') if not self.strand in [None, BINARY_MISSING_VAL] else '')\
            + ((' [' + str(self.val) + ']') if self.val is not None else '')

    def __repr__(self):
        return str(self)

    def toStr(self):
        #self.start+1 because we want to show 1-indexed, end inclusive output
        return (str(self.genome) + ':' if not self.genome is None else '')\
            + (str(self.chr) + ':' if not self.chr is None else '')\
            + (str(self.start+1) if not self.start is None else '')\
            + ('-' + str(self.end) if not self.end is None else '')\
            + ((' (Pos)' if self.strand else ' (Neg)') if not self.strand in [None, BINARY_MISSING_VAL] else '')\
            + ((' [' + str(self.val) + ']') if self.val != None else '')\
            + ((' id="%s"' % self.id) if self.id != None else '')\
            + ((' edges="%s"' % str(self.edges)) if self.edges != None else '')\
            + ((' weights="%s"' % str(self.weights)) if self.weights != None else '')\
            + ((' extra="%s"' % str(self.extra)) if self.extra != {} else '')

    def __cmp__(self, other):
        if other is None:
            return -1
        else:
            #print self.toStr()
            #print other.toStr()
            #print [cmp(getattr(self, attr), getattr(other, attr)) for attr in ['genome','chr','start','end','val','strand','id','edges','weights','extra']]
            try:
                return cmp([self.genome, self.chr, self.start, self.end, self.val, self.strand, self.id, self.edges, self.weights, self.extra] , \
                    [other.genome, other.chr, other.start, other.end, other.val, other.strand, other.id, other.edges, other.weights, other.extra])
            except:
                if isinstance(other, GenomeRegion):
                    return GenomeRegion.__cmp__(self, other)

    def overlaps(self, other):
        assert all((getattr(self, attr) is None) == (getattr(other, attr) is None) \
                   for attr in ['genome', 'chr', 'start', 'end'])
        if self.reprIsDense():
            return False

        if self.genome is not None:
            if self.genome != other.genome:
                return False

        if self.chr != other.chr:
            return False

        if not None in [self.start, self.end]:
            return False if self.start >= other.end or self.end <= other.start else True
        else:
            return True if (self.start is not None and self.start == other.start) or \
                            (self.end is not None and self.end == other.end) else False

    def reprIsDense(self):
        return self.start is None and self.end is None

    def validAsRegion(self):
        return not None in [self.genome, self.chr, self.start, self.end]
