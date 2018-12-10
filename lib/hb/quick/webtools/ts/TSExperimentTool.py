from proto.tools.hyperbrowser.GeneralGuiTool import GeneralGuiTool

from quick.util.debug import DebugUtil
from quick.webtools.mixin.GenomeMixin import GenomeMixin
from quick.application.UserBinSource import UserBinSource
from quick.multitrack.MultiTrackCommon import getGSuiteFromGalaxyTN
from quick.statistic.SummarizedInteractionPerTsCatV2Stat import SummarizedInteractionPerTsCatV2Stat
from quick.webtools.GeneralGuiTool import GeneralGuiToolMixin
import quick.gsuite.GuiBasedTsFactory as factory
from gold.track.TrackStructure import TrackStructureV2
from gold.application.HBAPI import doAnalysis
from gold.description.AnalysisDefHandler import AnalysisSpec
from quick.statistic.StatFacades import ObservedVsExpectedStat
from quick.webtools.mixin.DebugMixin import DebugMixin
from proto.hyperbrowser.HtmlCore import HtmlCore

class TSExperimentTool(GeneralGuiTool, DebugMixin, GenomeMixin):
    @classmethod
    def getToolName(cls):
        """
        Specifies a header of the tool, which is displayed at the top of the
        page.

        Mandatory method for all ProTo tools.
        """
        return "TS experiment"

    @classmethod
    def getInputBoxNames(cls):
        """
        Specifies a list of headers for the input boxes, and implicitly also
        the number of input boxes to display on the page. The returned list
        can have two syntaxes:

            1) A list of strings denoting the headers for the input boxes in
               numerical order.
            2) A list of tuples of strings, where each tuple has
               two items: a header and a key.

        The contents of each input box must be defined by the function
        getOptionsBoxK, where K is either a number in the range of 1 to the
        number of boxes (case 1), or the specified key (case 2).

        Note: the key has to be camelCase and start with a non-capital letter
              (e.g. "firstKey")

        Optional method. Default return value if method is not defined: []
        """
        return [('Select categorical GSuite of 4 tracks', 'gsuite')
                ] + \
                cls.getInputBoxNamesForGenomeSelection() + \
                [('Select query track', 'query'),
                 ('Select category', 'cat')
                ] + \
               cls.getInputBoxNamesForDebug()

    @classmethod
    def getOptionsBoxGsuite(cls):
        return GeneralGuiToolMixin.getHistorySelectionElement('gsuite')

    @classmethod
    def getOptionsBoxQuery(cls, prevChoices):
        return GeneralGuiToolMixin.getHistorySelectionElement()

    @classmethod
    def getOptionsBoxCat(cls, prevChoices):

        if prevChoices.gsuite:
            gSuiteTN = getGSuiteFromGalaxyTN(prevChoices.gsuite)
            return gSuiteTN.attributes

    @classmethod
    def execute(cls, choices, galaxyFn=None, username=''):
        #cls._setDebugModeIfSelected(choices)
        # from config.DebugConfig import DebugConfig
        # from config.DebugConfig import DebugModes
        # DebugConfig.changeMode(DebugModes.RAISE_HIDDEN_EXCEPTIONS_NO_VERBOSE)

        # DebugUtil.insertBreakPoint(5678, suspend=False)

        choices_gsuite = choices.gsuite
        selected_metadata= choices.cat
        choices_queryTrack = choices.query
        #genome = 'hg19'
        genome =  choices.genome

        queryTS = factory.getSingleTrackTS(genome, choices_queryTrack)
        refTS = factory.getFlatTracksTS(genome, choices_gsuite)

        categoricalTS = refTS.getSplittedByCategoryTS(selected_metadata)

        fullTS = TrackStructureV2()
        fullTS['query'] = queryTS
        fullTS['reference'] = categoricalTS
        spec = AnalysisSpec(SummarizedInteractionPerTsCatV2Stat)

        parameter = 'minLqMedUqMax'

        spec.addParameter('pairwiseStatistic', ObservedVsExpectedStat.__name__)
        spec.addParameter('summaryFunc',parameter)
        bins = UserBinSource('chr1','*',genome=genome)
        res = doAnalysis(spec, bins, fullTS)
        tsRes = res.getGlobalResult()['Result']

        htmlCore = HtmlCore()
        htmlCore.begin()

        if parameter == 'minAndMax':
            htmlCore.tableHeader(['Track', 'min-max'], sortable=False, tableId='tab1')
            for k, it in tsRes.iteritems():
                htmlCore.tableLine([k, str("%.2f" % it.getResult()[0]) + '-' + str("%.2f" % it.getResult()[1])])
            htmlCore.tableFooter()

        if parameter == 'minLqMedUqMax':

            dataList = []
            categories = []
            for keyE, itE in tsRes.iteritems():
                categories.append(keyE)
                dataList.append(list(itE.getResult()))

            from quick.webtools.restricted.visualization.visualizationGraphs import \
                visualizationGraphs
            vg = visualizationGraphs()
            res = vg.drawBoxPlotChart(dataList, categories=categories, seriesName=selected_metadata)
            htmlCore.line(res)

        htmlCore.end()
        print htmlCore

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

    # @classmethod
    # def getSubToolClasses(cls):
    #     """
    #     Specifies a list of classes for subtools of the main tool. These
    #     subtools will be selectable from a selection box at the top of the
    #     page. The input boxes will change according to which subtool is
    #     selected.
    #
    #     Optional method. Default return value if method is not defined: None
    #     """
    #     return None
    #
    # @classmethod
    # def isPublic(cls):
    #     """
    #     Specifies whether the tool is accessible to all users. If False, the
    #     tool is only accessible to a restricted set of users as well as admin
    #     users, as defined in the galaxy.ini file.
    #
    #     Optional method. Default return value if method is not defined: False
    #     """
    #     return False
    #
    # @classmethod
    # def isRedirectTool(cls):
    #     """
    #     Specifies whether the tool should redirect to an URL when the Execute
    #     button is clicked.
    #
    #     Optional method. Default return value if method is not defined: False
    #     """
    #     return False
    #
    # @classmethod
    # def getRedirectURL(cls, choices):
    #     """
    #     This method is called to return an URL if the isRedirectTool method
    #     returns True.
    #
    #     Mandatory method if isRedirectTool() returns True.
    #     """
    #     return ''
    #
    # @classmethod
    # def isHistoryTool(cls):
    #     """
    #     Specifies if a History item should be created when the Execute button
    #     is clicked.
    #
    #     Optional method. Default return value if method is not defined: True
    #     """
    #     return True
    #
    # @classmethod
    # def isBatchTool(cls):
    #     """
    #     Specifies if this tool could be run from batch using the batch. The
    #     batch run line can be fetched from the info box at the bottom of the
    #     tool.
    #
    #     Optional method. Default return value if method is not defined:
    #         same as isHistoryTool()
    #     """
    #     return cls.isHistoryTool()
    #
    # @classmethod
    # def isDynamic(cls):
    #     """
    #     Specifies whether changing the content of textboxes causes the page
    #     to reload. Returning False stops the need for reloading the tool
    #     after each input, resulting in less lags for the user.
    #
    #     Optional method. Default return value if method is not defined: True
    #     """
    #     return True
    #
    # @classmethod
    # def getResetBoxes(cls):
    #     """
    #     Specifies a list of input boxes which resets the subsequent stored
    #     choices previously made. The input boxes are specified by index
    #     (starting with 1) or by key.
    #
    #     Optional method. Default return value if method is not defined: True
    #     """
    #     return []
    #
    # @classmethod
    # def getToolDescription(cls):
    #     """
    #     Specifies a help text in HTML that is displayed below the tool.
    #
    #     Optional method. Default return value if method is not defined: ''
    #     """
    #     return ''
    #
    # @classmethod
    # def getToolIllustration(cls):
    #     """
    #     Specifies an id used by StaticFile.py to reference an illustration
    #     file on disk. The id is a list of optional directory names followed
    #     by a filename. The base directory is STATIC_PATH as defined by
    #     Config.py. The full path is created from the base directory
    #     followed by the id.
    #
    #     Optional method. Default return value if method is not defined: None
    #     """
    #     return None
    #
    # @classmethod
    # def getFullExampleURL(cls):
    #     """
    #     Specifies an URL to an example page that describes the tool, for
    #     instance a Galaxy page.
    #
    #     Optional method. Default return value if method is not defined: None
    #     """
    #     return None
    #
    # @classmethod
    # def isDebugMode(cls):
    #     """
    #     Specifies whether the debug mode is turned on. Debug mode is
    #     currently mostly used within the Genomic HyperBrowser and will make
    #     little difference in a plain Galaxy ProTo installation.
    #
    #     Optional method. Default return value if method is not defined: False
    #     """
    #     return False
    #
    @classmethod
    def getOutputFormat(cls, choices):
        return 'customhtml'
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

