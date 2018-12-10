"""
Created on Nov 3, 2015

@author: boris
"""
from gold.track.TSResult import TSResult
from gold.util.CommonFunctions import smartMeanWithNones, smartSum
from quick.statistic.PairedTSStat import PairedTSStat
from quick.statistic.StatisticV2 import StatisticV2
from gold.util.CustomExceptions import ShouldNotOccurError, InvalidStatArgumentError
from gold.statistic.MagicStatFactory import MagicStatFactory
from gold.track.TrackStructure import TrackStructureV2
from quick.util.CommonFunctions import minAndMax, minLqMedUqMax


class SummarizedInteractionWithOtherTracksV2Stat(MagicStatFactory):
    """
    STAT Q k,n

    Calculate the summary function (min, max, avg, sum) for all the interactions of first track
    in self._tracks with the rest of the tracks. An interaction is defined by the pair-wise statistic
    whose name is passed in as the argument rawStatistic.
    @rawStatistic - str
    @summaryFunc - function
    @reverse - boolean
    """
    pass

#class SummarizedInteractionWithOtherTracksStatSplittable(StatisticSumResSplittable):
#    pass

class SummarizedInteractionWithOtherTracksV2StatUnsplittable(StatisticV2):

    functionDict = {
                    'sum': smartSum,
                    'avg': smartMeanWithNones,
                    'max': max,
                    'min': min,
                    'minAndMax': minAndMax,
                    'raw': 'RawResults',
                    'minLqMedUqMax': minLqMedUqMax
                    }
    
    def _init(self, pairwiseStatistic=None, summaryFunc=None, reverse='No', **kwArgs):
        #NB! Any received parameter termed rawStatistic is ignored, as pairwiseStatistic will take this role in children
        self._pairwiseStatistic = self.getRawStatisticClass(pairwiseStatistic)

        self._summaryFunction = self._resolveFunction(summaryFunc)
        #self._summaryFunction = self[summaryFunc] #TODO: Should we replace the whole _resolveFunction with this one. Is such an error not clear enough?
        self._reversed = reverse
        self._kwArgs = kwArgs
    
    def _resolveFunction(self, summaryFunc):
        if summaryFunc not in self.functionDict:
            raise ShouldNotOccurError(str(summaryFunc) + 
                                      ' not in list, must be one of ' + 
                                      str(sorted(self.functionDict.keys())))
        else: 
            return self.functionDict[summaryFunc]
        
    def _compute(self):
        resTs = TSResult(self._computeTrackStructure)
        #listOfPairRTSs = [child.getResult() for child in self._children]
        # fullTs = TrackStructureV2()
        rawResults = []
        for key, child in self._childrenDict.iteritems():
            pairRTS = child.getResult()
            resTs[key] = pairRTS
            rawResults.append(pairRTS.getResult() )

        if self._summaryFunction == 'RawResults':
            resTs.setResult(rawResults)
        else:
            resTs.setResult( self._summaryFunction(rawResults) )
        return resTs
            
    def _createChildren(self):
        ts = self._trackStructure
        if self._reversed == 'No':
            pairedTS = ts['query'].makePairwiseCombinations(ts['reference'])
        elif self._reversed == 'Yes':
            pairedTS = ts['reference'].makePairwiseCombinations(ts['query'])
        else:
            raise InvalidStatArgumentError('reverse must be one of "Yes" or "No"')

        self._childrenDict = {}
        for pairTSKey in pairedTS:
            self._childrenDict[pairTSKey] = self._addChild(PairedTSStat(self._region, pairedTS[pairTSKey], pairedTsRawStatistic=self._pairwiseStatistic, **self._kwArgs))

        self._computeTrackStructure = pairedTS
