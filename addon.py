import paths
from containers import index
from tinyxbmc import gui
from tinyxbmc import addon


class test(gui.form):
    def init(self, *args, **kwargs):
        self.bool("test1", "tbool1")
        self.edit("test2", "test2")
        self.edit("test3", "test3")
        self.edit("test4", "test4")
        self.progress("test5", "test5")
        self.text("test6", "test6")
        self.text("test7", "test7")
        self.button("submit", "submit", None)
        self.button("cancel", "cancel", None)
        self.button("tetel", "caasdasncel", None)
        self.button("submit1", "submit", None)
        self.button("cancel1", "cancel", None)
        #self.button("tetel1", "caasdasncel", None)
        self.prg = 0

    def onloop(self):
        self.prg += 1
        self.set("test5", self.prg % 100)

test(150, 500, "header")
index.index()
