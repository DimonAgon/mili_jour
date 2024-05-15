
import re, regex

name_rePattern = "\p{Lu}\p{Ll}+"
full_name_rePattern = "{}\s{}(?:[-]{})?".format(name_rePattern, name_rePattern, name_rePattern) #for any language
journal_rePattern = "(?!0)\d{3}"
ordinal_rePattern = "(?!0)\d{1,2}"
sterngth_rePattern = "(?!0)\d{2}"
report_headers_rePattern = "\s*(Студент)\s+((\d)(?:\s+(\d))*)"
report_row_rePattern = "({}|{})\s+((н|·|_)(?:\s+(н|·|_))*)".format(name_rePattern, full_name_rePattern)
report_rePattern = "{}\s+({}\s*)+".format(report_headers_rePattern, report_row_rePattern)

