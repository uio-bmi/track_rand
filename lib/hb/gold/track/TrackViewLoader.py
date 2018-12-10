from gold.track.TrackFormat import TrackFormat
from gold.track.TrackView import TrackView
from gold.track.BoundingRegionShelve import BoundingRegionShelve
from gold.util.CompBinManager import CompBinManager
from gold.util.CommonConstants import RESERVED_PREFIXES
from collections import OrderedDict

class TrackViewLoader:
    @staticmethod
    def _getArray(trackData, arrayName, brInfo, bin=None):
        array = trackData.get(arrayName)
        
        if brInfo is not None and array is not None:
            #print arrayName
            #print 'bin: ', bin
            if bin is not None:
                #print 'br',brInfo.startBinIdx, brInfo.endBinIdx
                #print [x for x in array]
                #print array[brInfo.startBinIdx:brInfo.endBinIdx]
                if brInfo.startBinIdx == brInfo.endBinIdx:
                    return 0
                array = array[brInfo.startBinIdx:brInfo.endBinIdx]
            else:
                #print 'br',brInfo.startIdx, brInfo.endIdx
                #print [x for x in array]
                #print array[brInfo.startIdx:brInfo.endIdx]
                array = array[brInfo.startIdx:brInfo.endIdx]
                
        return array[bin] if bin is not None else array

    @staticmethod
    def loadTrackView(trackData, region, borderHandling, allowOverlaps, trackName=[]):
        """
        trackData : see TrackSource.getTrackData {'id' : smartmemmap}
        region : see GenomeRegion
        """
        #brShelve = BoundingRegionShelve(region.genome, trackName, allowOverlaps)
        brShelve = trackData.boundingRegionShelve
        brInfo = brShelve.getBoundingRegionInfo(region) if brShelve is not None else None
        
        extraArrayNames = [arrayName for arrayName in trackData if arrayName not in \
                           RESERVED_PREFIXES.keys() + ['leftIndex', 'rightIndex']]
        
        reservedArrays = [TrackViewLoader._getArray(trackData, arrayName, brInfo) for arrayName in RESERVED_PREFIXES]
        extraArrays = [TrackViewLoader._getArray(trackData, arrayName, brInfo) for arrayName in extraArrayNames]
        trackFormat = TrackFormat( *(reservedArrays + [OrderedDict(zip(extraArrayNames, extraArrays))]) )
        
        if trackFormat.reprIsDense():
            if brInfo is None:
                leftIndex = region.start
                rightIndex = region.end
            else:
                leftIndex = region.start - brInfo.start
                rightIndex = region.end - brInfo.start 
        else:
            leftBin = CompBinManager.getBinNumber(region.start)
            rightBin = CompBinManager.getBinNumber(region.end-1)
            #leftBin = region.start/COMP_BIN_SIZE
            #rightBin = (region.end-1)/COMP_BIN_SIZE
            
            if trackData.get('leftIndex') is None or trackData.get('rightIndex') is None:
                raise IOError('Preprocessed track not found. TrackData: ' + ', '.join(trackData.keys()))
            
            leftIndex = TrackViewLoader._getArray(trackData, 'leftIndex', brInfo, leftBin)
            rightIndex = TrackViewLoader._getArray(trackData, 'rightIndex', brInfo, rightBin)
        
        slicedReservedArrays = [(array[leftIndex:rightIndex] if array is not None else None) for array in reservedArrays]
        slicedExtraArrays = [(array[leftIndex:rightIndex] if array is not None else None) for array in extraArrays]
        
        argList = [region] + slicedReservedArrays + [borderHandling, allowOverlaps] + [OrderedDict(zip(extraArrayNames, slicedExtraArrays))]
        tv = TrackView( *(argList) )
        
        if not trackFormat.reprIsDense():
            tv.sliceElementsAccordingToGenomeAnchor()
            #tv._doScatteredSlicing()
        return tv
