def flatten(some_list):
    result = []
    for element in some_list:
        if isinstance(element, list):
            result.extend(flatten(element))
        else:
            result.append(element)
    return result
