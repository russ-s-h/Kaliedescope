class Program:
    def __init__(self):
        self.func_list = []
        self.symtable = []

class Function:
    def __init__(self, name, ftype, params, entry, symtable, insts):
        self.name = name
        self.ftype = ftype
        self.params = params
        self.symtable = symtable
        self.insts = insts

        self.Program = None
        self.entry = '__Entry'
        self.end = '__End'

        self.Bbtable = {}
        self.dom = {}
        self.idom = {}
        self.tree = {}
        self.df = {}
        #context in which something is being done
        self.context = {}
        #define nessesary instructions for every program
        self.insts.insert(0,[None, 'Deflabel', ['Label', self.entry]])
        self.insts[1:1] = [[p[1], 'defparam', p[0]] for p in params]

class BasicBlock:
    def __init__(self, name):
        self.name = name
        #subsequent names
        self.succ = []
        #leading names
        self.pred = []
        #instructions inside the block
        self.insts = []

