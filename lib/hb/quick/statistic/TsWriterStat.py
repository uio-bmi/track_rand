# Copyright (C) 2009, Geir Kjetil Sandve, Sveinung Gundersen and Morten Johansen
# This file is part of The Genomic HyperBrowser.
#
#    The Genomic HyperBrowser is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    The Genomic HyperBrowser is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with The Genomic HyperBrowser.  If not, see <http://www.gnu.org/licenses/>.
from gold.statistic.MagicStatFactory import MagicStatFactory
from quick.statistic.StatisticV2 import StatisticV2
from quick.statistic.TrackWriterStat import TrackWriterStat
import os
from urllib import quote
from proto.hyperbrowser.StaticFile import GalaxyRunSpecificFile

class TsWriterStat(MagicStatFactory):
    pass


class TsWriterStatUnsplittable(StatisticV2):

    def _compute(self):
         resultFileNames = []

         for child in self._children:
             resultFileNames.append(child.getResult())

         return resultFileNames

    def _createChildren(self):
        for singleTrackTs in self._trackStructure.getLeafNodes():
            self._addChild(TrackWriterStat(region=self._region, track=singleTrackTs.track, trackFilePath=singleTrackTs.metadata['trackFilePath'], **self._kwArgs))
