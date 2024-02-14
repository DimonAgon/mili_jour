
import re, regex

name_rePattern = "\p{Lu}\p{Ll}+\s\p{Lu}\p{Ll}+(?:[-]\p{Lu}\p{Ll}+)?" #for any language
journal_rePattern = "(?!0)\d{3}"
ordinal_rePattern = "(?!0)\d{1,2}"
sterngth_rePattern = "(?!0)\d{2}"

