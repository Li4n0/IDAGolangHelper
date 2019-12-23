import idaapi
import Gopclntab
import Utils
import Firstmoduledata
import Types
import idc
import idautils
import pygore

class GoSettings(object):


    def __init__(self):
        self.storage = {}
        self.bt_obj = Utils.get_bitness(idc.BeginEA())
        self.structCreator = Utils.StructCreator(self.bt_obj)
        self.processor = None
        self.typer = None
        self.binaryPath = idaapi.get_path(idaapi.PATH_TYPE_IDB)[:-4]
        
    def getVal(self, key):
        if key in self.storage:
            return self.storage[key]
        return None

    def setVal(self, key, val):
        self.storage[key] = val

    def getGopcln(self):
        gopcln_addr = self.getVal("gopcln")
        if gopcln_addr is None:
            gopcln_addr = Gopclntab.findGoPcLn()
            self.setVal("gopcln", gopcln_addr)
        return gopcln_addr

    def findModuleData(self):
        gopcln_addr = self.getGopcln()
        fmd = Firstmoduledata.findFirstModuleData(gopcln_addr, self.bt_obj)
        self.setVal("firstModData", fmd)
        return

    def tryFindGoVersion(self):
        f = pygore.GoFile(self.binaryPath)
        v = f.get_compiler_version()
        f.close()
        return "Go Compiler Version should be %s" % (v.name)

    def renameFunctions(self):
        gopcln_tab = self.getGopcln()
        Gopclntab.rename(gopcln_tab, self.bt_obj)
    
    def renameStructs(self):
        f = pygore.GoFile(self.binaryPath)
        c = f.get_compiler_version()
        print('Compiler: {}\nTimestamp: {}\nSHA {}\n'.format(c.name, c.timestamp, c.sha))

        #pkgs = f.get_packages()
        types = f.get_types()
        f.close()
        for type in types:
            Utils.rename(type.addr, type.name)
            print type.addr, type.name

    def getVersionByString(self):
        pos = idautils.Functions().next()
        if idc.FindBinary(pos, idc.SEARCH_DOWN, "67 6f 31 2e 31 30") != idc.BADADDR:
            return 'Go 1.10'
        if idc.FindBinary(pos, idc.SEARCH_DOWN, "67 6f 31 2e 39") != idc.BADADDR:
            return 'Go 1.9'
        if idc.FindBinary(pos, idc.SEARCH_DOWN, "67 6f 31 2e 38") != idc.BADADDR:
            return 'Go 1.8'
        if idc.FindBinary(pos, idc.SEARCH_DOWN, "67 6f 31 2e 37") != idc.BADADDR:
            return 'Go 1.7'
        if idc.FindBinary(pos, idc.SEARCH_DOWN, "67 6f 31 2e 36") != idc.BADADDR:
            return 'Go 1.6'
        if idc.FindBinary(pos, idc.SEARCH_DOWN, "67 6f 31 2e 35") != idc.BADADDR:
            return 'Go 1.5'
        if idc.FindBinary(pos, idc.SEARCH_DOWN, "67 6f 31 2e 34") != idc.BADADDR:
            return 'Go 1.4'
        if idc.FindBinary(pos, idc.SEARCH_DOWN, "67 6f 31 2e 33") != idc.BADADDR:
            return 'Go 1.3'
        if idc.FindBinary(pos, idc.SEARCH_DOWN, "67 6f 31 2e 32") != idc.BADADDR:
            return 'Go 1.2'

    def createTyper(self, typ):
        if typ == 0:
            self.typer = Types.Go12Types(self.structCreator)
        elif typ == 1:
            self.typer = Types.Go14Types(self.structCreator)
        elif typ == 2:
            self.typer = Types.Go15Types(self.structCreator)
        elif typ == 3:
            self.typer = Types.Go16Types(self.structCreator)
        elif typ == 4 or typ == 5:
            self.typer = Types.Go17Types(self.structCreator)
        elif typ == 6: #1.9
            self.typer = Types.Go17Types(self.structCreator)
        elif typ == 7: #1.10
            self.typer = Types.Go17Types(self.structCreator)

    def typesModuleData(self, typ):
        if typ < 2:
            return
        if self.getVal("firstModData") is None:
            self.findModuleData()
        fmd = self.getVal("firstModData")
        if fmd is None:
            return
        if self.typer is None:
            self.createTyper(typ)
        robase = None
        if typ == 4:
            beg, end, robase = Firstmoduledata.getTypeinfo17(fmd, self.bt_obj)
            self.processor = Types.TypeProcessing17(beg, end, self.bt_obj, self, robase)
        elif typ == 5:
            beg, end, robase = Firstmoduledata.getTypeinfo18(fmd, self.bt_obj)
            self.processor = Types.TypeProcessing17(beg, end, self.bt_obj, self, robase)
        elif typ == 6:
            beg, end, robase = Firstmoduledata.getTypeinfo18(fmd, self.bt_obj)
            self.processor = Types.TypeProcessing19(beg, end, self.bt_obj, self, robase)
        elif typ == 7:
            beg, end, robase = Firstmoduledata.getTypeinfo18(fmd, self.bt_obj)
            self.processor = Types.TypeProcessing19(beg, end, self.bt_obj, self, robase)
        else:
            beg, end = Firstmoduledata.getTypeinfo(fmd, self.bt_obj)
            self.processor = Types.TypeProcessing(beg, end, self.bt_obj, self)
        print "%x %x %x" % (beg, end, robase)
        for i in self.processor:
            pass
        return
