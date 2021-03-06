'''
Created on Nov 3, 2015

@author: boris
'''

from gold.statistic.MagicStatFactory import MagicStatFactory
from quick.statistic.RandomizationManagerV3Stat import RandomizationManagerV3Stat
from quick.statistic.StatisticV2 import StatisticV2


class TrackSimilarityToCollectionHypothesisV2Stat(MagicStatFactory):
    '''
    classdocs
    '''
    pass

#class TrackSimilarityToCollectionHypothesisV2StatSplittable(StatisticSumResSplittable):
#    pass
            
class TrackSimilarityToCollectionHypothesisV2StatUnsplittable(StatisticV2):    
    def _compute(self):
        return self._children[0].getResult()
    
    def _createChildren(self):
        self._addChild(RandomizationManagerV3Stat(self._region, self._trackStructure, **self._kwArgs))
