import os

from gold.application.HBAPI import doAnalysis
from gold.description.AnalysisDefHandler import AnalysisSpec
from gold.gsuite import GSuiteComposer
from gold.gsuite.GSuite import GSuite
from gold.gsuite.GSuiteTrack import GalaxyGSuiteTrack, GSuiteTrack
from gold.track.trackstructure import TsRandAlgorithmRegistry
from gold.track.trackstructure.TsRandAlgorithmRegistry import getRequiredArgsForAlgorithm, getKwArgsForAlgorithm, \
    BIN_SOURCE_ARG, EXCLUDED_TS_ARG, WITHIN_TRACKS_CATEGORY, PERMUTED_SEGS_AND_INTERSEGS_STR
from gold.track.trackstructure.TsUtils import getRandomizedVersionOfTs
from quick.application.UserBinSource import UserBinSource
from quick.gsuite.GuiBasedTsFactory import getFlatTracksTS, getSingleTrackTS
from quick.multitrack.MultiTrackCommon import getGSuiteFromGalaxyTN
from quick.statistic.TsWriterStat import TsWriterStat
from quick.webtools.GeneralGuiTool import GeneralGuiTool
from proto.HtmlCore import HtmlCore
from quick.webtools.mixin.RandAlgorithmMixin import RandAlgorithmMixin
from quick.webtools.mixin.UserBinMixin import UserBinMixin
from gold.gsuite.GSuiteTrack import FileGSuiteTrack


class RandomizationGuiTool(GeneralGuiTool, RandAlgorithmMixin, UserBinMixin):
    @classmethod
    def getToolName(cls):
        return "Randomization GUI"

    #
    @classmethod
    def getInputBoxNames(cls):
        return [('Basic user mode', 'isBasic'),
                ("", 'toolDescTop'),
                ('Reference genome: ', 'genome'),
                ('Choose a file with chromosome lengths of a custom genome build : ', 'chooseChrnLenFile'),
                ('Number of tracks to shuffle: ', 'numberOfTracks'),
                ('Number of desired randomizations of each track: ', 'numberOfRandomizations'),
                ('Select the BED or Gsuite file to shuffle: ', 'chooseTrackFiles'),
                ('Restrict the shuffling to certain regions?', 'universeRegions'),
                ('Select the BED file containing universe of regions', 'universeRegionFileUpload'),
                #('Type of shuffling (horizontal or vertical): ', 'shufflingType'),
                ('Shuffling distribution: ', 'shufflingDistribution'),
                #('Preserve clumping of genomic regions? ', 'preserveClumping'),
                #('Allow overlap of shuffled locations? ', 'allowOverlaps'),
                #('Allow truncation of sizes in special cases? ', 'truncateSizes'),
                ('Should the shuffling be reproducible? ', 'reproduceShuffling'),
                ('Enter a seed value in the textbox: ', 'enterSeed'),
                ('Number of times to randomize: ', 'numberOfTimesToRandomize')
                ] \
               + cls.getInputBoxNamesForRandAlgSelection() \
                + cls.getInputBoxNamesForUserBinSelection()

    @staticmethod
    def getOptionsBoxIsBasic():
        return False

    @classmethod
    def getOptionsBoxToolDescTop(cls, prevChoices):
        core = HtmlCore()
        core.bigHeader('genomic-permutation-tools')
        core.smallHeader('a collection of permutation approaches to shuffle genomic regions')
        core.divider()
        return '__rawStr__', str(core)

    CUSTOM_REFERENCE_GENOME = 'Custom reference genome'


    @classmethod
    def getOptionsBoxGenome(cls, prevChoices):
        return '__genome__'
        #return ['Human (hg19)', 'Human (hg38)', 'Mouse (mm9)', 'Mouse (mm10)',cls.CUSTOM_REFERENCE_GENOME]

    @classmethod
    def getOptionsBoxChooseChrnLenFile(cls, prevChoices):
        # if prevChoices.missingGenome:
        if prevChoices.genome == cls.CUSTOM_REFERENCE_GENOME:
            return ('__history__',)

    SINGLE_TRACK = 'Single genomic track'
    MULTIPLE_TRACKS = 'Multiple genomic tracks'

    @classmethod
    def getOptionsBoxNumberOfTracks(cls, prevChoices):  # Alt: getOptionsBox1()
        return [cls.SINGLE_TRACK, cls.MULTIPLE_TRACKS]

    ONE_RAND = 1
    THREE_RAND = 3
    TEN_RAND = 10
    FIFTY_RAND = 50
    HUNDRED_RAND = 100

    @classmethod
    def getOptionsBoxNumberOfRandomizations(cls, prevChoices):
        return [cls.ONE_RAND, cls.THREE_RAND,cls.TEN_RAND,cls.FIFTY_RAND,cls.HUNDRED_RAND]

    HORIZONTAL = 'Shuffling should be within each genomic track'
    VERTICAL = 'Shuffling should be across all the multiple tracks'
    @classmethod
    def getOptionsBoxShufflingType(cls, prevChoices):
        if prevChoices.numberOfTracks in [cls.MULTIPLE_TRACKS]:
            return [cls.HORIZONTAL, cls.VERTICAL]

    WITHIN = 'shuffle within each chromosome'
    ACROSS = 'shuffle across chromosomes'
    @classmethod
    def getOptionsBoxShufflingDistribution(cls, prevChoices):
            return [cls.WITHIN, cls.ACROSS]

    PRESERVE = 'Preserve the distances between genomic regions'
    IGNORE = 'Ignore clumping of genomic regions when shuffling'

    @classmethod
    def getOptionsBoxPreserveClumping(cls, prevChoices):
        return [cls.PRESERVE, cls.IGNORE]

    ALLOW = 'Allow the shuffled regions to overlap'
    NO = 'Do not allow the shuffled regions to overlap'
    @classmethod
    def getOptionsBoxAllowOverlaps(cls, prevChoices):
        return [cls.ALLOW, cls.NO]

    TRUNCATE = 'Truncate the sizes of genomic regions in special cases'
    CANNOT = 'Do not truncate the sizes of genomic regions'

    @classmethod
    def getOptionsBoxTruncateSizes(cls, prevChoices):
        return [cls.TRUNCATE, cls.CANNOT]

    YES = 'Make the shuffling reproducible'
    UNNECESSARY= 'Not required'

    @classmethod
    def getOptionsBoxReproduceShuffling(cls, prevChoices):
        return [cls.UNNECESSARY,cls.YES]

    @classmethod
    def getOptionsBoxEnterSeed(cls, prevChoices):
        if prevChoices.reproduceShuffling in [cls.YES]:
            return ('textbox')

    @classmethod
    def getOptionsBoxNumberOfTimesToRandomize(cls, prevChoices):
        return ['1', '3', '5', '10', '50', '100']

    @classmethod
    def getOptionsBoxChooseTrackFiles(cls, prevChoices):
        if prevChoices.numberOfTracks in [cls.SINGLE_TRACK,cls.MULTIPLE_TRACKS]:
            #return ('__history__', 'bed','gsuite')
            return GeneralGuiTool.getHistorySelectionElement('gsuite')

    WHOLE_GENOME = 'No, use the whole genome'
    EXPLICIT_UNIVERSE = 'Yes, perform the shuffling only in the explicit set of regions supplied'

    @classmethod
    def getOptionsBoxUniverseRegions(cls, prevChoices):  # Alt: getOptionsBox2()
            return [cls.WHOLE_GENOME, cls.EXPLICIT_UNIVERSE]

    @classmethod
    def getOptionsBoxUniverseRegionFileUpload(cls, prevChoices):
        if prevChoices.universeRegions in [cls.EXPLICIT_UNIVERSE]:
            return ('__history__', 'bed')

    @classmethod
    def getOptionsBoxFirstKey(cls):  # Alt: getOptionsBox1()
        return ['testChoice1', 'testChoice2', '...']

    @classmethod
    def getOptionsBoxSecondKey(cls, prevChoices):  # Alt: getOptionsBox2()
        return ''


    @classmethod
    def execute(cls, choices, galaxyFn=None, username=''):
        """
        Is called when execute-button is pushed by web-user. Should print
        output as HTML to standard out, which will be directed to a results
        page in Galaxy history. If getOutputFormat is anything else than
        'html', the output should be written to the file with path galaxyFn.
        If needed, StaticFile can be used to get a path where additional
        files can be put (cls, e.g. generated image files). choices is a list
        of selections made by web-user in each options box.

        Mandatory unless isRedirectTool() returns True.
        """
        choices_gsuite = choices.chooseTrackFiles
        choices_randType = choices.randType
        choices_randAlg = choices.randAlg
        choices_numberOfTimesToRandomize = choices.numberOfTimesToRandomize
        assert choices_gsuite is not None

        genome =  choices.genome
        assert genome is not None
        analysisBins = UserBinMixin.getUserBinSource(choices)

        gsuite = getGSuiteFromGalaxyTN(choices_gsuite)
        for i, gsTrack in enumerate(gsuite.allTracks()):
            assert gsTrack.trackName is not None, "gsuite track %s has track name None" % gsTrack
        ts = getFlatTracksTS(genome, choices_gsuite)

        cls.run_on_extracted_variables(ts, analysisBins, choices_numberOfTimesToRandomize, choices_randAlg,
                                       choices_randType, galaxyFn, genome)

    @classmethod
    def run_on_extracted_variables(cls, ts, analysisBins, choices_numberOfTimesToRandomize, choices_randAlg,
                                   choices_randType, galaxyFn, genome):
        assert choices_numberOfTimesToRandomize==1 #For now, since ts probably needs to be unique each time..

        outputGSuite = GSuite()
        for i in range(0, int(choices_numberOfTimesToRandomize)):
            randTvProvider = cls._createTrackViewProvider(ts, analysisBins, genome, choices_randAlg, choices_randType,
                                                          False, None)  # the last False and non are temporary..
            randomizedTs = getRandomizedVersionOfTs(ts, randTvProvider)

            # output files
            for singleTrackTs in randomizedTs.getLeafNodes():
                uri = "outputfile"

                uri = FileGSuiteTrack.generateURI(path='/home/ivargry/outfile', suffix='bed',
                                          trackName=['trackname'], doQuote=False)

                #uri = "file:/home/ivargry/test/test/file2;bed"

                title = singleTrackTs.metadata.pop('title')
                gSuiteTrack = FileGSuiteTrack(uri, title=title + '.randomized', fileFormat='primary', trackType='segments',
                                          genome=genome, attributes=singleTrackTs.metadata)
                outputGSuite.addTrack(gSuiteTrack)
                singleTrackTs.metadata['trackFilePath'] = gSuiteTrack.path
                singleTrackTs.metadata['randomization_run'] = i

            spec = AnalysisSpec(TsWriterStat)

            res = doAnalysis(spec, analysisBins, randomizedTs)
        GSuiteComposer.composeToFile(outputGSuite, galaxyFn)

    @classmethod
    def _createTrackViewProvider(cls, origTs, binSource, genome, randType, randAlg, selectExcludedTrack, excludedTrack):
        reqArgs = getRequiredArgsForAlgorithm(randType, randAlg)
        kwArgs = getKwArgsForAlgorithm(randType, randAlg)

        args = []
        for arg in reqArgs:
            if arg == EXCLUDED_TS_ARG:
                if selectExcludedTrack == cls.YES:
                    raise NotImplementedError()
                    excludedTs = getSingleTrackTS(genome, excludedTrack)
                else:
                    excludedTs = None
                args.append(excludedTs)
            if arg == BIN_SOURCE_ARG:
                args.append(binSource)

        tvProvider = TsRandAlgorithmRegistry.createTrackViewProvider(
            randType, randAlg, *args, **kwArgs
        )

        tvProvider.setOrigTrackStructure(origTs)
        tvProvider.setBinSource(binSource)

        return tvProvider

    @classmethod
    def validateAndReturnErrors(cls, choices):
        """
        Should validate the selected input parameters. If the parameters are
        not valid, an error text explaining the problem should be returned.
        The GUI then shows this text to the user (if not empty) and greys
        out the execute button (even if the text is empty). If all
        parameters are valid, the method should return None, which enables
        the execute button.

        Optional method. Default return value if method is not defined: None
        """
        return None


    def getOutputFormat(cls, choices):
        """
        The format of the history element with the output of the tool. Note
        that if 'html' is returned, any print statements in the execute()
        method is printed to the output dataset. For text-based output
        (e.g. bed) the output dataset only contains text written to the
        galaxyFn file, while all print statements are redirected to the info
        field of the history item box.

        Note that for 'html' output, standard HTML header and footer code is
        added to the output dataset. If one wants to write the complete HTML
        page, use the restricted output format 'customhtml' instead.

        Optional method. Default return value if method is not defined:
        'html'
        """
        return 'gsuite'
    #
    # @classmethod
    # def getOutputName(cls, choices=None):
    #     return cls.getToolSelectionName()
    #     """
    #     The title (name) of the main output history element.
    #
    #     Optional method. Default return value if method is not defined:
    #     the name of the tool.
    #     """


if __name__ == "__main__":
    from gold.track.TrackStructure import SingleTrackTS, FlatTracksTS
    from gold.track.Track import PlainTrack
    t = PlainTrack(["test"])
    single_track_ts = SingleTrackTS(t, {"title": "dummy"})
    ts = FlatTracksTS()
    ts["test"] = single_track_ts

    print(ts)
    print(t)

    analysisBins = UserBinSource("chr1", "*", genome="hg18")
    RandomizationGuiTool.run_on_extracted_variables(ts, analysisBins, 1, WITHIN_TRACKS_CATEGORY,
                                   PERMUTED_SEGS_AND_INTERSEGS_STR, "", "hg18")

