import gold.gsuite.GSuiteConstants as GSuiteConstants
from quick.webtools.GeneralGuiTool import GeneralGuiTool


# This is a template prototyping GUI that comes together with a corresponding
# web page.

class ExtractSubtracksTool(GeneralGuiTool):
    GSUITE_OUTPUT_LOCATION = GSuiteConstants.LOCAL
    GSUITE_OUTPUT_FILE_FORMAT = GSuiteConstants.PREPROCESSED
    GSUITE_OUTPUT_TRACK_TYPE = 'any, dependent on the track type of the selected tracks'

    @staticmethod
    def getToolName():
        '''
        Specifies a header of the tool, which is displayed at the top of the
        page.
        '''
        return "Compile GSuite from HyperBrowser repository"

    @staticmethod
    def getInputBoxNames():
        '''
        Specifies a list of headers for the input boxes, and implicitly also the
        number of input boxes to display on the page. The returned list can have
        two syntaxes:

            1) A list of strings denoting the headers for the input boxes in
               numerical order.
            2) A list of tuples of strings, where each tuple has
               two items: a header and a key.

        The contents of each input box must be defined by the function
        getOptionsBoxK, where K is either a number in the range of 1 to the
        number of boxes (case 1), or the specified key (case 2).

        Note: the key has to be camelCase (e.g. "firstKey")
        '''
        return [('', 'basicQuestionId'),
                ('Select genome','genome'),
                ('Select parent track','parentTrack')]

    #@staticmethod
    #def getInputBoxOrder():
    #    '''
    #    Specifies the order in which the input boxes should be displayed, as a
    #    list. The input boxes are specified by index (starting with 1) or by
    #    key. If None, the order of the input boxes is in the order specified by
    #    getInputBoxNames.
    #    '''
    #    return None

    @staticmethod
    def getOptionsBoxBasicQuestionId():
        return '__hidden__', None

    @staticmethod
    def getOptionsBoxGenome(prevChoices): # Alternatively: getOptionsBox1()
        '''
        Defines the type and contents of the input box. User selections are
        returned to the tools in the prevChoices and choices attributes to other
        methods. These are lists of results, one for each input box (in the
        order specified by getInputBoxOrder()).

        The input box is defined according to the following syntax:

        Selection box:          ['choice1','choice2']
        - Returns: string

        Text area:              'textbox' | ('textbox',1) | ('textbox',1,False)
        - Tuple syntax: (contents, height (#lines) = 1, read only flag = False)
        - The contents is the default value shown inside the text area
        - Returns: string

        Password field:         '__password__'
        - Returns: string

        Genome selection box:   '__genome__'
        - Returns: string

        Track selection box:    '__track__'
        - Requires genome selection box.
        - Returns: colon-separated string denoting track name

        History selection box:  ('__history__',) | ('__history__', 'bed', 'wig')
        - Only history items of specified types are shown.
        - Returns: colon-separated string denoting galaxy track name, as
                   specified in ExternalTrackManager.py.

        History check box list: ('__multihistory__', ) | ('__multihistory__', 'bed', 'wig')
        - Only history items of specified types are shown.
        - Returns: OrderedDict with galaxy id as key and galaxy track name
                   as value if checked, else None.

        Hidden field:           ('__hidden__', 'Hidden value')
        - Returns: string

        Table:                  [['header1','header2'], ['cell1_1','cell1_2'], ['cell2_1','cell2_2']]
        - Returns: None

        Check box list:         OrderedDict([('key1', True), ('key2', False), ('key3', False)])
        - Returns: OrderedDict from key to selection status (bool).
        '''
        return '__genome__'

    @staticmethod
    def getOptionsBoxParentTrack(prevChoices): # Alternatively: getOptionsBox2()
        '''
        See getOptionsBoxFirstKey().

        prevChoices is a namedtuple of selections made by the user in the
        previous input boxes (that is, a namedtuple containing only one element
        in this case). The elements can accessed either by index, e.g.
        prevChoices[0] for the result of input box 1, or by key, e.g.
        prevChoices.key (case 2).
        '''
        return '__track__'

    #@staticmethod
    #def getOptionsBox3(prevChoices):
    #    return ['']

    #@staticmethod
    #def getOptionsBox4(prevChoices):
    #    return ['']

    #@staticmethod
    #def getDemoSelections():
    #    return ['testChoice1','..']

    @staticmethod
    def execute(choices, galaxyFn=None, username=''):
        '''
        Is called when execute-button is pushed by web-user. Should print
        output as HTML to standard out, which will be directed to a results page
        in Galaxy history. If getOutputFormat is anything else than HTML, the
        output should be written to the file with path galaxyFn. If needed,
        StaticFile can be used to get a path where additional files can be put
        (e.g. generated image files). choices is a list of selections made by
        web-user in each options box.
        '''

        from quick.gsuite.GSuiteHbIntegration import getSubtracksAsGSuite
        import gold.gsuite.GSuiteComposer as GSuiteComposer

        genome = choices.genome
        parentTrack = choices.parentTrack.split(':')
        if parentTrack == ['']:
            parentTrack = []

        gSuite = getSubtracksAsGSuite(genome, parentTrack, username)

        GSuiteComposer.composeToFile(gSuite, galaxyFn)

    @classmethod
    def validateAndReturnErrors(cls, choices):
        '''
        Should validate the selected input parameters. If the parameters are not
        valid, an error text explaining the problem should be returned. The GUI
        then shows this text to the user (if not empty) and greys out the
        execute button (even if the text is empty). If all parameters are valid,
        the method should return None, which enables the execute button.
        '''

        errorStr = cls._checkGenome(choices.genome)
        if errorStr:
            return errorStr

    @classmethod
    def getOutputName(cls, choices):
        from quick.gsuite.GSuiteHbIntegration import getGSuiteHistoryOutputName
        from quick.util.CommonFunctions import prettyPrintTrackName

        if choices.genome:
            parentTrack = choices.parentTrack.split(':')
            if parentTrack == ['']:
                description = 'All tracks'
            else:
                description = prettyPrintTrackName(parentTrack)

            return getGSuiteHistoryOutputName('preprocessed', description)

    #@staticmethod
    #def getSubToolClasses():
    #    '''
    #    Specifies a list of classes for subtools of the main tool. These
    #    subtools will be selectable from a selection box at the top of the page.
    #    The input boxes will change according to which subtool is selected.
    #    '''
    #    return None
    #
    @staticmethod
    def isPublic():
        '''
        Specifies whether the tool is accessible to all users. If False, the
        tool is only accessible to a restricted set of users as defined in
        LocalOSConfig.py.
        '''
        return True

    #@staticmethod
    #def isRedirectTool():
    #    '''
    #    Specifies whether the tool should redirect to an URL when the Execute
    #    button is clicked.
    #    '''
    #    return False
    #
    #@staticmethod
    #def getRedirectURL(choices):
    #    '''
    #    This method is called to return an URL if the isRedirectTool method
    #    returns True.
    #    '''
    #    return ''
    #
    #@staticmethod
    #def isHistoryTool():
    #    '''
    #    Specifies if a History item should be created when the Execute button is
    #    clicked.
    #    '''
    #    return True
    #
    #@staticmethod
    #def isDynamic():
    #    '''
    #    Specifies whether changing the content of texboxes causes the page to
    #    reload.
    #    '''
    #    return True
    #
    #@staticmethod
    #def getResetBoxes():
    #    '''
    #    Specifies a list of input boxes which resets the subsequent stored
    #    choices previously made. The input boxes are specified by index
    #    (starting with 1) or by key.
    #    '''
    #    return []
    #
    @classmethod
    def getToolDescription(cls):
        '''
        Specifies a help text in HTML that is displayed below the tool.
        '''
        from proto.hyperbrowser.HtmlCore import HtmlCore

        core = HtmlCore()
        core.paragraph('This tool can be used to compile a GSuite file referring to a subset of the tracks '
                       'in the HyperBrowser repository. To use the tool, please follow these steps:')
        core.orderedList(['Select the genome build',
                          'Select the parent track, i.e. the top level in the track hierarchy that '
                          'you are interested in. The tool will return all tracks that are found in the '
                          'hierarchy underneath the selected parent track, descending into all sublevels.'])
        core.divider()
        core.smallHeader('Note')
        core.paragraph('Even though this tool can be used to build GSuite compilations of any tracks, '
                       'the resulting GSuite file will be more usable if the track are somewhat homogeneous '
                       'in track type.')

        cls._addGSuiteFileDescription(core,
                                      outputLocation=cls.GSUITE_OUTPUT_LOCATION,
                                      outputFileFormat=cls.GSUITE_OUTPUT_FILE_FORMAT,
                                      outputTrackType=cls.GSUITE_OUTPUT_TRACK_TYPE)

        return str(core)

    #
    #@staticmethod
    #def getToolIllustration():
    #    '''
    #    Specifies an id used by StaticFile.py to reference an illustration file
    #    on disk. The id is a list of optional directory names followed by a file
    #    name. The base directory is STATIC_PATH as defined by Config.py. The
    #    full path is created from the base directory followed by the id.
    #    '''
    #    return None
    #
    # @staticmethod
    # def getFullExampleURL():
    #     return 'u/hb-superuser/p/compile-gsuite-from-hyperbrowser-repository--intersect-preprocessed-tracks-in-gsuite-with-a-single-track---example'
    #
    #@classmethod
    #def isBatchTool(cls):
    #    '''
    #    Specifies if this tool could be run from batch using the batch. The
    #    batch run line can be fetched from the info box at the bottom of the
    #    tool.
    #    '''
    #    return cls.isHistoryTool()
    #
    #@staticmethod
    #def isDebugMode():
    #    '''
    #    Specifies whether debug messages are printed.
    #    '''
    #    return False
    #
    @staticmethod
    def getOutputFormat(choices):
        '''
        The format of the history element with the output of the tool. Note
        that html output shows print statements, but that text-based output
        (e.g. bed) only shows text written to the galaxyFn file.In the latter
        case, all all print statements are redirected to the info field of the
        history item box.
        '''
        return 'gsuite'
