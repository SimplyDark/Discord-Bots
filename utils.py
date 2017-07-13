def avg(list):
    return round(sum(list) / len(list))


def merge(merged, a, b):
    # Find min value between both list heads and add that to temp list

    if a and b:
        #print("a: " + str(a))
        #print("b: " + str(b))
        #print("merged: " + str(merged))
        return merge(merged + [min(a[0], b[0])],
                     a[1:] if min(a[0], b[0]) == a[0] else a,
                     b[1:] if min(a[0], b[0]) == b[0] and not a[0] == b[0] else b
                     )
    # Sort 'a' list if there are no more items in 'b' and 'a' has more than 1
    elif a and not b and len(a) > 1:
        return merged + merge([], a[:int(len(a)/2)], a[int(len(a)/2):])
    # Add last item into merged if there's no other items
    elif a and not b:
        return merged + a
    # Sort 'b' list if there are no more items in 'a' and 'b' has more than 1
    elif b and not a and len(b) > 1:
        return merged + merge([], b[:int(len(b)/2)], b[int(len(b)/2):])
    # Add last item into merged if there's no other items
    elif b and not a:
        return merged + b
    # Once finished return sorted array
    else:
        return merged


def mergesort(lst):
    # If list is empty return empty list
    if not lst:
        return []
    # If list only has 2 items return the min and max of list
    elif len(lst) == 2:
        #print("List: " + str(lst))
        return [min(lst), max(lst)]
    # If list only has 1 item return the list
    elif len(lst) == 1:
        #print("List: " + str(lst))
        return lst
    # Split list in half and recurse through function again
    else:
        #print("List: " + str(lst))
        return merge([], mergesort(lst[:int(len(lst)/2)]), mergesort(lst[int(len(lst)/2):]))