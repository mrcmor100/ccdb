import logging
import posixpath
import sys
import os

from ccdb import TypeTable, Assignment
from ccdb import AlchemyProvider
from ccdb.cmd import CliCommandBase, UtilityArgumentParser
from ccdb.path_utils import ParseRequestResult, parse_request, parse_time
from ccdb import BraceMessage as Lfm   # lfm is aka log format message. See BraceMessage desc about

log = logging.getLogger("ccdb.cmd.commands.cat")


# *********************************************************************
#   Class Cat - Show assignment data by ID                           *
# *********************************************************************
class Cat(CliCommandBase):
    """Show assignment data by ID"""

    # ccdb utility class descr part
    # ------------------------------
    command = "cat"
    name = "Cat"
    short_descr = "Show assignment data by ID"
    uses_db = True

    # specific values
    show_borders = True
    show_header = True
    show_comments = False
    show_date = False

    def __init__(self, context):
        CliCommandBase.__init__(self, context)

    # ----------------------------------------
    #   process
    # ----------------------------------------
    def execute(self, args):
        """
        Process this command
        :param args:
        :return: 0 if command was successful, value!=0 means command was not successful
        :rtype: int
        """
        if log.isEnabledFor(logging.DEBUG):
            log.debug(Lfm("{0}Cat command is in charge {0}\\", os.linesep))
            log.debug(Lfm(" |- arguments : '" + "' '".join(args) + "'"))

        assert self.context is not None

        parsed_args = self.process_arguments(args)

        if parsed_args.ass_id:
            assignment = self.get_assignment_by_id(parsed_args.ass_id)
        else:
            assignment = self.get_assignment_by_request(parsed_args.request)

        if assignment:
            # now we have to know, how to print an assignment
            data = assignment.constant_set.data_table

            if len(data) and len(data[0]):
                if parsed_args.user_request_print_horizontal:
                    self.print_assignment_horizontal(assignment, parsed_args.show_header, parsed_args.show_borders,
                                                     parsed_args.show_comments)
                elif parsed_args.user_request_print_vertical:
                    self.print_assignment_vertical(assignment, parsed_args.show_header, parsed_args.show_borders, parsed_args.show_comments)
                else:
                    if len(data) == 1 and len(data[0]) > 3:
                        self.print_assignment_vertical(assignment, parsed_args.show_header, parsed_args.show_borders,
                                                       parsed_args.show_comments)
                    else:
                        self.print_assignment_horizontal(assignment, parsed_args.show_header, parsed_args.show_borders,
                                                         parsed_args.show_comments)
            else:
                log.warning("Assignment contains no data")
        else:
            print("Cannot fill data for assignment with this ID")
            return 1

        return 0

    # ----------------------------------------
    #   gets assignment by database id
    # ----------------------------------------
    def get_assignment_by_id(self, assignment_id):
        """gets assignment by database id"""

        provider = self.context.provider
        assert isinstance(provider, AlchemyProvider)
        return self.context.provider.get_assignment_by_id(assignment_id)

    # ----------------------------------------
    #   gets assignment by parsed request
    # ----------------------------------------
    def get_assignment_by_request(self, request):
        """gets assignment by parsed request
        @param request: Parsed request
        @type request: ParseRequestResult
        """

        # If we are in interactive or test mode, and path is not absolute, combine current path and provided path
        if not request.path.startswith('/') and self.context.current_path:
            request.path = posixpath.join(self.context.current_path, request.path)

        # In non-interactive mode, cat should handle path without leading / as absolute anyway
        # Check mode and if relative path is given
        if request.path_is_parsed and not request.path.startswith("/"):
            # PatCH the PaTH
            request.path = "/" + request.path

        # get the assignment from DB
        return self.context.provider.get_assignment_by_request(request)

    # ----------------------------------------
    #   process_arguments
    # ----------------------------------------
    def process_arguments(self, args):
        parser = UtilityArgumentParser(add_help=False)
        parser.add_argument("obj_name", default="", nargs='?')

        # border
        group = parser.add_mutually_exclusive_group()
        group.add_argument("-b", "--borders", action="store_true", dest='show_borders', default=True)
        group.add_argument("-nb", "--no-borders", action="store_false", dest='show_borders')

        # header
        group = parser.add_mutually_exclusive_group()
        group.add_argument("-h", "--header", action="store_true", dest='show_header', default=True)
        group.add_argument("-nh", "--no-header", action="store_false", dest='show_header')

        # comments
        group = parser.add_mutually_exclusive_group()
        group.add_argument("-c", "--comments", action="store_true", dest='show_comments', default=False)
        group.add_argument("-nc", "--no-comments", action="store_false", dest='show_comments')

        # horizontal or vertical
        parser.add_argument("-ph", "--horizontal", action="store_true", dest='user_request_print_horizontal')
        parser.add_argument("-pv", "--vertical", action="store_true", dest='user_request_print_vertical')

        # Assignment parameters
        parser.add_argument("-v", "--variation")
        parser.add_argument("-a", "--id", dest='ass_id')
        parser.add_argument("-r", "--run")
        parser.add_argument("-t", "--time", required=False)

        # Parse args
        result = parser.parse_args(args)

        # Parse ccdb request
        result.request = parse_request(result.obj_name) if result.obj_name else ParseRequestResult()

        # Check if user set the variation
        if not result.request.variation_is_parsed and result.variation:
            result.request.variation = result.variation
            result.request.variation_is_parsed = True

        # Check if user set the default variation
        if not result.request.variation_is_parsed and self.context.current_variation:
            result.request.variation = self.context.current_variation
            result.request.variation_is_parsed = True

        # Check if user set the run
        if not result.request.run_is_parsed and result.run:
            result.request.run = int(result.run)
            result.request.run_is_parsed = True

        # Check if user set the default run
        if not result.request.run_is_parsed and self.context.current_run:
            result.request.run = self.context.current_run
            result.request.run_is_parsed = True

        # Check if user set time
        if not result.request.time_is_parsed and result.time:
            result.request.time_str = result.time
            result.request.time = parse_time(result.time)
            result.request.time_is_parsed = True

        return result

    # --------------------------------------------------------------------------------
    #   print_assignment_vertical
    # --------------------------------------------------------------------------------
    def print_assignment_horizontal(self, assignment, print_header=True, display_borders=True, comments=False):
        """
        print table with assignment data horizontally

        :param assignment : Assignment object ot print
        :type assignment: Assignment

        :param print_header: print header with column information or not
        :type print_header: bool

        :param comments: print comments

        :param display_borders: print '|' borders or not
        :type display_borders: bool

        """
        log.debug(Lfm(" |- print asgmnt horizontally: header {0}, borders {1}, comments {2}"
                      "", print_header, display_borders, comments))

        border = "|" if display_borders else " "

        assert isinstance(assignment, Assignment)
        table = assignment.constant_set.type_table
        assert isinstance(table, TypeTable)

        # PRINT COMMENTS
        if comments:
            # this line sep hack is for Windows. Where os.linesep is \r\n, but file might have \n only line seps
            comment_str = assignment.comment
            if os.name == 'nt':
                # we make sure that it is always os.linesep on windows
                comment_str = comment_str.replace('\r\n', '\n').replace('\n', os.linesep)

            sharped_lines = "#" + str(comment_str).replace(os.linesep, os.linesep + "#")
            print(sharped_lines)

        column_names = [column.name for column in table.columns]
        column_types = [column.type for column in table.columns]
        data = assignment.constant_set.data_list

        columns_count = len(column_names)

        assert len(column_names) == len(column_types)
        assert (len(data) % columns_count) == 0

        min_width = 10
        column_width = [10 for _ in range(columns_count)]
        total_data_width = 0

        # determine column length
        for i in range(0, columns_count):
            if len(column_names[i]) > min_width:
                column_width[i] = len(column_names[i])
            else:
                column_width[i] = min_width

            total_data_width += column_width[i]

        # this is our cap, if we need it....
        cap = "+" + (total_data_width + 3 * columns_count - 1) * "-" + "+"

        # print header if needed
        if print_header:

            # cap?
            if display_borders:
                print((self.theme.AsgmtBorder + cap))

            # names line
            for i in range(0, columns_count):
                sys.stdout.write(self.theme.AsgmtBorder + border + self.theme.Reset)
                col_format = " %%-%is " % column_width[i]
                sys.stdout.write(self.theme.AsgmtHead + col_format % column_names[i] + self.theme.Reset)

            print((self.theme.AsgmtBorder + border + self.theme.Reset))  # last border

            # types line
            for i in range(0, columns_count):
                sys.stdout.write(self.theme.AsgmtBorder + border + self.theme.Reset)
                col_format = " %%-%is " % column_width[i]
                sys.stdout.write(self.theme.AsgmtType + col_format % column_types[i] + self.theme.Reset)
            print((self.theme.AsgmtBorder + border + self.theme.Reset))  # last border

        # cap?
        if display_borders:
            print((self.theme.AsgmtBorder + cap))

        # data line by line
        column_iter = 0
        for dataItem in data:
            # place data
            sys.stdout.write(self.theme.AsgmtBorder + border + self.theme.Reset)
            col_format = " %%-%is " % column_width[column_iter]
            sys.stdout.write(self.theme.AsgmtValue + col_format % dataItem + self.theme.Reset)
            column_iter += 1

            # new line?
            if column_iter == columns_count:
                column_iter = 0
                print((self.theme.AsgmtBorder + border + self.theme.Reset))

        # final cap?
        if display_borders:
            print((self.theme.AsgmtBorder + cap))

    # --------------------------------------------------------------------------------
    #   print_assignment_horizontal
    # --------------------------------------------------------------------------------
    def print_assignment_vertical(self, assignment, print_header=True, display_borders=True, comments=False):
        """
        print columns vertically and rows horizontally

        :param assignment : Assignment object ot print
        :type assignment: Assignment

        :param print_header: print header with column information or not
        :type print_header: bool

        :param display_borders: print '|' borders or not
        :type display_borders: bool

        :param comments: print comments
        """
        log.debug(Lfm(" |- print asgmnt vertically: header {0}, borders {1}, comments {2}",
                      print_header, display_borders, comments))

        assert isinstance(assignment, Assignment)

        border = " "
        if display_borders:
            border = "|"

        table = assignment.constant_set.type_table
        isinstance(table, TypeTable)

        # PRINT COMMENTS
        if comments:
            print(("#" + str(assignment.comment).replace(os.linesep, "#" + os.linesep)))

        column_names = [column.name for column in table.columns]
        column_types = [column.type for column in table.columns]
        data = assignment.constant_set.data_table

        if not data:  # no rows
            return
        if not data[0]:  # no columns
            return
        assert len(column_names) == len(column_types)
        assert len(data[0]) == len(column_names)

        # present data as columns, each column has cells
        columns = []
        header_columns_added = 0
        if print_header:
            columns.append(column_names)
            columns.append(column_types)
            header_columns_added = 2

        for _ in data:
            columns.append([])

        # fill data to columns
        for rowI in range(0, len(data)):
            for colI in range(0, len(data[rowI])):
                columns[rowI + header_columns_added].append(data[rowI][colI])

        column_widths = [len(max(column, key=len)) for column in columns]
        total_width = 0
        for length in column_widths:
            total_width += length

        # totalDataLength = 0

        # #determine column length
        # for i in range(0, columnsNum):
        #    if len(columnNames[i]) > minLength:
        #        columnLengths[i] = len(columnNames[i])
        #    else:
        #        columnLengths[i] = minLength

        #    totalDataLength += columnLengths[i];

        # this is our cap, if we need it....
        cap = "+" + (total_width + 3 * len(columns) - 2) * "-" + "+"

        # print header if needed
        # names line
        #    for i in range(0, columnsNum):
        #        sys.stdout.write(self.theme.AsgmtBorder + border + self.theme.Reset)
        #        frmt = " %%-%is "%columnLengths[i]
        #        sys.stdout.write(self.theme.AsgmtHead + frmt%columnNames[i] + self.theme.Reset)
        #
        #    print self.theme.AsgmtBorder + border + self.theme.Reset #last border
        #    #types line
        #    for i in range(0, columnsNum):
        #        sys.stdout.write(self.theme.AsgmtBorder + border + self.theme.Reset)
        #        frmt = " %%-%is "%columnLengths[i]
        #        sys.stdout.write(self.theme.AsgmtType + frmt%columnTypes[i] + self.theme.Reset)
        #    print self.theme.AsgmtBorder + border + self.theme.Reset #last border

        # cap?
        if display_borders:
            print((self.theme.AsgmtBorder + cap + self.theme.Reset))

        # #data line by line
        # columnIter = 0

        for rowI in range(0, len(columns[0])):
            sys.stdout.write(self.theme.AsgmtBorder + border + self.theme.Reset)

            for colI in range(0, len(columns)):
                # place data
                data_item = columns[colI][rowI]
                frmt = " %%-%is " % column_widths[colI]
                if colI == 0 and print_header:
                    sys.stdout.write(self.theme.AsgmtHead + frmt % data_item + self.theme.Reset)
                elif colI == 1 and print_header:
                    sys.stdout.write(self.theme.AsgmtType + '(' + (frmt % data_item).strip() + ')' + self.theme.Reset)
                    sys.stdout.write(self.theme.AsgmtBorder + border + self.theme.Reset)
                else:
                    sys.stdout.write(self.theme.AsgmtValue + frmt % data_item + self.theme.Reset)

            sys.stdout.write(self.theme.AsgmtBorder + border + self.theme.Reset + os.linesep)

        # #final cap?
        if display_borders:
            print((self.theme.AsgmtBorder + cap + self.theme.Reset))

    # ----------------------------------------
    #   print_help
    # ----------------------------------------
    def print_help(self):
        """Prints help of the command"""

        print("""Show data values for assignment.

Usage:
    cat <request or table path>
    cat -a <assignment_id>   #Where assignment_id provided by 'vers <table path>' command

Formatting flags:

    -c  or --comments     - Show comments on/off
    -nc or --no-comments

    -ph or --horizontal   - Print table horizontally
    -pa or --vertical     - Print table vertically
    (If no '--horizontal' or '--vertical' flag is given, the layout of table is determined automatically:
    vertical layout if table has only 1 row and more than 3 columns, horizontal otherwise)

    -b  or --borders      - Switch show borders on of off
    -nb or --no-borders

    -h  or --header       - Show header on/off
    -nh or --no-header

    -t  or --time         - Show time
    -nt or --no-time

Examples:
    > cat /test/test_vars/test_table               #print latest data for test_table
    > cat /test/test_vars/test_table::subtest      #print latest data in subtest variation
    > cat /test/test_vars/test_table:::2012-08     #print data latest for august 2012

See also 'dump' command which is 'cat' formatted to save data to files. 'help dump'

    """)
