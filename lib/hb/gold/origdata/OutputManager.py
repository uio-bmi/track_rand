from collections import OrderedDict
from gold.origdata.OutputDirectory import OutputDirectory
from gold.util.CustomExceptions import AbstractClassError
from gold.util.CommonFunctions import createDirPath

class OutputManager(object):
    def __new__(cls, genome, trackName, allowOverlaps, geSourceManager):
        if len(geSourceManager.getAllChrs()) == 1:
            return OutputManagerSingleChr.__new__(OutputManagerSingleChr, genome, trackName, \
                                                  allowOverlaps, geSourceManager)
        else:
            return OutputManagerSeveralChrs.__new__(OutputManagerSeveralChrs, genome, trackName, \
                                                    allowOverlaps, geSourceManager)

    def _createOutputDirectory(self, genome, chr, trackName, allowOverlaps, geSourceManager):
        dirPath = createDirPath(trackName, genome, chr, allowOverlaps)
        
        from quick.util.GenomeInfo import GenomeInfo
        return  OutputDirectory(dirPath, geSourceManager.getPrefixList(), \
                                geSourceManager.getNumElementsForChr(chr), \
                                GenomeInfo.getChrLen(genome, chr), \
                                geSourceManager.getValDataType(), \
                                geSourceManager.getValDim(), \
                                geSourceManager.getEdgeWeightDataType(), \
                                geSourceManager.getEdgeWeightDim(), \
                                geSourceManager.getMaxNumEdgesForChr(chr), \
                                geSourceManager.getMaxStrLensForChr(chr), \
                                geSourceManager.isSorted())

    def writeElement(self, genomeElement):
        raise AbstractClassError()
        
    def writeRawSlice(self, genomeElement):
        raise AbstractClassError()
        
    def close(self):
        raise AbstractClassError()


class OutputManagerSingleChr(OutputManager):
    def __new__(cls, *args, **kwArgs):
        return object.__new__(cls)
    
    def __init__(self, genome, trackName, allowOverlaps, geSourceManager):
        allChrs = geSourceManager.getAllChrs()
        assert len(allChrs) == 1
        
        self._outputDir = self._createOutputDirectory\
            (genome, allChrs[0], trackName, allowOverlaps, geSourceManager)
    
    def writeElement(self, genomeElement):
        self._outputDir.writeElement(genomeElement)
        
    def writeRawSlice(self, genomeElement):
        self._outputDir.writeRawSlice(genomeElement)
            
    def close(self):
        self._outputDir.close()


class OutputManagerSeveralChrs(OutputManager):
    def __new__(cls, *args, **kwArgs):
        return object.__new__(cls)
    
    def __init__(self, genome, trackName, allowOverlaps, geSourceManager):
        allChrs = geSourceManager.getAllChrs()

        self._outputDirs = OrderedDict()
        for chr in allChrs:
            self._outputDirs[chr] = self._createOutputDirectory\
                (genome, chr, trackName, allowOverlaps, geSourceManager)
            
    def writeElement(self, genomeElement):
        self._outputDirs[genomeElement.chr].writeElement(genomeElement)
        
    def writeRawSlice(self, genomeElement):
        self._outputDirs[genomeElement.chr].writeRawSlice(genomeElement)
            
    def close(self):
        for dir in self._outputDirs.values():
            dir.close()
