def array_to_set(arr: list) -> set:
    s = set()
    for e in arr:
        s.add(e)
    return s


def set_to_array(s: set) -> list:
    list_ = list()
    for e in s:
        list_.append(e)
    return list_
