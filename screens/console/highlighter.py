from qtpy.QtGui import QSyntaxHighlighter, QTextCharFormat, QColor, QFont
from qtpy.QtCore import QRegularExpression
import keyword
import builtins as _builtins

class PythonHighlighter(QSyntaxHighlighter):
    STATE_NORMAL        = 0
    STATE_TRIPLE_DOUBLE = 1
    STATE_TRIPLE_SINGLE = 2

    CONTROL_KW = frozenset({
        'if', 'elif', 'else', 'for', 'while', 'break', 'continue',
        'return', 'yield', 'raise', 'try', 'except', 'finally',
        'with', 'pass', 'match', 'case', 'and', 'or', 'not', 'in', 'is',
    })
    TYPE_KW = frozenset({
        'None', 'True', 'False',
    })

    BUILTIN_NAMES = frozenset(
        name for name in dir(_builtins)
        if not name.startswith('_')
    )

    BRACKET_COLORS = ['#FFD700', '#DA70D6', '#179FFF']
    BRACKETS_OPEN  = set('([{')
    BRACKETS_CLOSE = set(')]}')

    def __init__(self, document):
        super().__init__(document)
        self._buildFormats()
        self._buildRules()

    def _fmt(self, color, bold=False, italic=False):
        f = QTextCharFormat()
        f.setForeground(QColor(color))
        if bold:   f.setFontWeight(QFont.Bold)
        if italic: f.setFontItalic(True)
        return f

    def _buildFormats(self):
        self.fmts = {
            'keyword':   self._fmt('#569CD6', bold=True),
            'ctrl':      self._fmt('#C586C0', bold=True),
            'type_kw':   self._fmt('#569CD6', bold=True),
            'builtin':   self._fmt('#4EC9B0'),
            'fn_def':    self._fmt('#DCDCAA'),
            'fn_call':   self._fmt('#DCDCAA'),
            'cls_name':  self._fmt('#4EC9B0'),
            'cls_call':  self._fmt('#4EC9B0'),
            'deco':      self._fmt('#DCDCAA', italic=True),
            'string':    self._fmt('#CE9178'),
            'multistr':  self._fmt('#CE9178'),
            'escape':    self._fmt('#D7BA7D'),
            'fstr_expr': self._fmt('#9CDCFE'),
            'number':    self._fmt('#B5CEA8'),
            'comment':   self._fmt('#6A9955', italic=True),
            'self_kw':   self._fmt('#569CD6', italic=True),
            'prop':      self._fmt('#9CDCFE'),
            'const':     self._fmt('#4FC1FF'),
            'op':        self._fmt('#D4D4D4'),
        }
        self.bracketFmts = [
            self._fmt(c) for c in self.BRACKET_COLORS
        ]

    def _buildRules(self):
        R = QRegularExpression
        opts = QRegularExpression.UseUnicodePropertiesOption

        self.rules = []

        self.rules.append((R(r'@[\w.]+', opts), 'deco'))

        self.rules.append((R(r'\bdef\s+(\w+)', opts), 'fn_def'))

        self.rules.append((R(r'\bclass\s+(\w+)', opts), 'cls_name'))

        self.rules.append((R(r'\b(self|cls)\b', opts), 'self_kw'))

        ctrlPat = r'\b(?:' + '|'.join(sorted(self.CONTROL_KW, key=len, reverse=True)) + r')\b'
        self.rules.append((R(ctrlPat, opts), 'ctrl'))

        typePat = r'\b(?:None|True|False)\b'
        self.rules.append((R(typePat, opts), 'type_kw'))

        otherKw = [
            kw for kw in keyword.kwlist
            if kw not in self.CONTROL_KW and kw not in self.TYPE_KW
        ]
        kwPat = r'\b(?:' + '|'.join(sorted(otherKw, key=len, reverse=True)) + r')\b'
        self.rules.append((R(kwPat, opts), 'keyword'))

        biPat = r'\b(?:' + '|'.join(sorted(self.BUILTIN_NAMES, key=len, reverse=True)) + r')\b'
        self.rules.append((R(biPat, opts), 'builtin'))

        self.rules.append((R(r'\b[A-Z][A-Z0-9_]{1,}\b(?!\s*\()', opts), 'const'))

        self.rules.append((R(r'\b([A-Z]\w*)\s*(?=\()', opts), 'cls_call'))

        self.rules.append((R(r'(?<=\.)[a-z_]\w*(?=\s*\()', opts), 'fn_call'))

        self.rules.append((R(r'(?<=\.)[a-z_]\w*', opts), 'prop'))

        self.rules.append((R(r'\b[a-z_]\w*(?=\s*\()', opts), 'fn_call'))

        self.rules.append((R(r'\b0[xX][0-9a-fA-F][0-9a-fA-F_]*\b', opts), 'number'))
        self.rules.append((R(r'\b0[bB][01][01_]*\b',                opts), 'number'))
        self.rules.append((R(r'\b0[oO][0-7][0-7_]*\b',              opts), 'number'))
        self.rules.append((R(r'\b\d[\d_]*(?:\.\d[\d_]*)?(?:[eE][+-]?\d+)?[jJ]?\b', opts), 'number'))

        _pfx = r'(?:[fFbBrRuU]|rb|br|fr|rf|Rb|bR|Fr|rF|RB|BR|FR|RF)?'
        for q in ('"', "'"):
            pat = rf'{_pfx}(?<!{q}{q}){q}(?:\\.|[^{q}\\\n])*{q}'
            self.rules.append((R(pat, opts), 'string'))

        self.rules.append((R(r'#[^\n]*', opts), 'comment'))

    def highlightBlock(self, text: str) -> None:
        state = self.previousBlockState()
        if state in (self.STATE_TRIPLE_DOUBLE, self.STATE_TRIPLE_SINGLE):
            delim = '"""' if state == self.STATE_TRIPLE_DOUBLE else "'''"
            end = text.find(delim)
            if end == -1:
                self.setFormat(0, len(text), self.fmts['multistr'])
                self.setCurrentBlockState(state)
                return
            closeEnd = end + 3
            self.setFormat(0, closeEnd, self.fmts['multistr'])
            self._applyRules(text, closeEnd, len(text))
            self._applyRainbow(text, closeEnd, len(text))
            self.setCurrentBlockState(self.STATE_NORMAL)
            return

        for delim, sid in (('"""', self.STATE_TRIPLE_DOUBLE),
                            ("'''", self.STATE_TRIPLE_SINGLE)):
            idx = self._findTriple(text, delim, 0)
            if idx != -1:
                self._applyRules(text, 0, idx)
                self._applyRainbow(text, 0, idx)
                close = text.find(delim, idx + 3)
                if close != -1:
                    self.setFormat(idx, close + 3 - idx, self.fmts['multistr'])
                    self._applyRules(text, close + 3, len(text))
                    self._applyRainbow(text, close + 3, len(text))
                    self.setCurrentBlockState(self.STATE_NORMAL)
                else:
                    self.setFormat(idx, len(text) - idx, self.fmts['multistr'])
                    self.setCurrentBlockState(sid)
                return

        self._applyRules(text, 0, len(text))
        self._applyRainbow(text, 0, len(text))
        self.setCurrentBlockState(self.STATE_NORMAL)

    def _findTriple(self, text: str, delim: str, start: int) -> int:
        idx = text.find(delim, start)
        return idx

    def _applyRules(self, text: str, start: int, end: int) -> None:
        if start >= end:
            return

        for pattern, kind in self.rules:
            fmt = self.fmts[kind]
            it = pattern.globalMatch(text, start)
            while it.hasNext():
                m = it.next()
                ms = m.capturedStart()
                if ms >= end:
                    break

                if kind == 'fn_def' and m.lastCapturedIndex() >= 1:
                    gs, gl = m.capturedStart(1), m.capturedLength(1)
                    if 0 <= gs < end:
                        self.setFormat(gs, gl, fmt)

                elif kind == 'cls_name' and m.lastCapturedIndex() >= 1:
                    gs, gl = m.capturedStart(1), m.capturedLength(1)
                    if 0 <= gs < end:
                        self.setFormat(gs, gl, fmt)

                elif kind == 'cls_call' and m.lastCapturedIndex() >= 1:
                    gs, gl = m.capturedStart(1), m.capturedLength(1)
                    if 0 <= gs < end:
                        self.setFormat(gs, gl, fmt)

                else:
                    length = min(m.capturedLength(), end - ms)
                    if length > 0:
                        self.setFormat(ms, length, fmt)

    def _applyRainbow(self, text: str, start: int, end: int) -> None:
        depth = 0
        i = start
        while i < min(end, len(text)):
            currentColor = self.format(i).foreground().color().name()
            if currentColor in {self.fmts['string'].foreground().color().name(),
                                  self.fmts['multistr'].foreground().color().name(),
                                  self.fmts['comment'].foreground().color().name()}:
                i += 1
                continue

            ch = text[i]
            if ch in self.BRACKETS_OPEN:
                self.setFormat(i, 1, self.bracketFmts[depth % 3])
                depth += 1
            elif ch in self.BRACKETS_CLOSE:
                depth = max(0, depth - 1)
                self.setFormat(i, 1, self.bracketFmts[depth % 3])
            i += 1