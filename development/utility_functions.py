import hist

def summarize(d,ntabs=1):
    '''
    Visualises a dictionary lazily:
        Gets integral of any hist.Hist object
        Gets initial value of any coffea.analysis_tools.Cutflow objects
        Gets type of of any other object
    Returns a print-ready string
    '''
    tab = '\t'*ntabs
    print_string ='{\n'
    for key,value in d.items():
        print_string += f"{tab}{key} : "
        if isinstance(value,dict):
            print_string += summarize(value, ntabs=ntabs+1)
        elif isinstance(value, hist.hist.Hist):
            print_string += f"{type(value)}\tIntegral:{value.sum()}\n"
        else :
            print_string += f"{type(value)}\n"
    print_string += tab+'}\n'
    return print_string
