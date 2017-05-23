import paths
from containers import index
from tinyxbmc import gui


class test(gui.form):
    def init(self, *args, **kwargs):
        self.bool("test1")
        self.edit("test2")
        self.edit("test3")
        self.edit("test4")
        self._prg = self.progress("test5")
        self.text("test6")
        self.text("test7")
        self.button("submit")
        self.button("cancel")
        self.button("tetel")
        self.button("submit1")
        self.button("cancel1")
        self.button("tetel1")
        self.prg = 0

    def onloop(self):
        self.prg += 1
        self.set(self._prg, self.prg % 100)

test(150, 500, "header")
index.index()
