from avgui.settings.lists_of_segments import *
import re

def find_nth(haystack, needle, n):
    parts = haystack.split(needle, n + 1)
    if len(parts) <= n + 1:
        return -1
    return len(haystack) - len(parts[-1]) - len(needle)

def nth_is_present(haystack, needle, n):
    parts = haystack.split(needle, n + 1)
    if len(parts) <= n + 1:
        return False
    return True

# Redudant code -- Needs to be fixed
def does_line_have_rule(line):
    if any(e in line for e in full_line_list):
        return True
    elif any(e in line for e in up_to_colon_list):
        return True
    elif any(e in line for e in up_to_first_plus_list):
        return True
    elif any(e in line for e in up_to_second_plus_list):
        return True
    elif "LIN" in line or "UNH" in line:
        return True
    else:
        return False

def line_rules(line):
    end = len(line)-1

    # Segments that need the entire line
    if any(e in line for e in full_line_list):
        end = line.index("'")

    # All segments that need to be saved up to colon
    elif any(e in line for e in up_to_colon_list):
        end = line.index(":")

    # All segments that need to be saved up to the first plus
    elif any(e in line for e in up_to_first_plus_list):
        end = line.index("+")

    # All segments that need to be saved up to the second plus
    elif any(e in line for e in up_to_second_plus_list):
        # Check if the second plus isn't present. If that is the case end it at the first plus
       
        if not nth_is_present(line, "+", 1):
            end = line.index("'")
        else:
            end = find_nth(line, "+", 1)

    # Unique for LIN to reformat string to just include LIN####
    elif "LIN" in line:
        adjusted_line = re.sub(r'\+.+\+\+', '', line) # Removes everything between + and ++
        end = adjusted_line.index(":")
        return adjusted_line[0:end]

    # Unique for UNH to reformat string to just include UNHType
    elif "UNH" in line:
        adjusted_line = re.sub(r'\+.+\+', '', line) # Removes everything between + and +
        end = adjusted_line.index(":")
        return adjusted_line[0:end]

    return line[0:end]