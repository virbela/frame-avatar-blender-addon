

def get_by_name_substring(str, lst: list) -> list:
    return lst

def get_by_name_with_without_substring(withList : list, withoutList : list, objectList : list) -> list:
    print(withList)
    print(withoutList)
    return objectList

# Returns a 1 or 2 digit integer from a string
# given a substring. 
# i.e. 
# str "L_Eye__TakesColor__Variants_08"
# substr "__Variants_"
# returns 8
def int_after_substring(str : str, substr : str) -> int:
    i = str.index(substr)
    l = len(substr)
    return int(str[i+l:i+l+2])



