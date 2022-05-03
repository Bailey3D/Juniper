import pymxs


def get_or_pick_selection():
    """Returns the current node selection if something is selected, else prompts the user to pick nodes
    :return <[node]:nodes> Node selection
    """
    output = []
    targets = pymxs.runtime.selection
    if(targets.count == 0):
        target = pymxs.runtime.pickObject()
        if(target):
            output = [target]
    else:
        output = []
        for i in targets:
            output.append(i)
    return output
