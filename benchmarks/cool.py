def get_memory():
    """
    Get node total memory and memory usage in (KB).

    returns a dict like:
      {'total': 3075868, 'free': 283536, 'buffers': 1749044, 'cached': 552156, 'used': 491132}
    """
    with open("/proc/meminfo", "r") as mem:
        ret = {}
        for i in mem:
            sline = i.split()
            if str(sline[0]) == "MemTotal:":
                ret["total"] = int(sline[1])
            elif str(sline[0]) == "MemFree:":
                ret["free"] = int(sline[1])
            elif str(sline[0]) == "Buffers:":
                ret["buffers"] = int(sline[1])
            elif str(sline[0]) == "Cached:":
                ret["cached"] = int(sline[1])

        ret["used"] = int(ret["total"]) - (int(ret["free"] + ret["buffers"] + ret["cached"]))
    return ret


ALL_MEMORY = get_memory()

print('ALL_MEMORY["free"] ')
print(ALL_MEMORY["free"])
print()

print('ALL_MEMORY["free"] * 1000')
print(ALL_MEMORY["free"] * 1000)
# import pdb

# pdb.set_trace()
# print()
# print()
# print("ll")
# print()
