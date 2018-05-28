import lex
import tree
import sys
import view
import bytecode as gen


def run_code(code, mid=0):
    toks = lex.make(code)
    code_tree = tree.tree(toks)

    ret = gen.make(code_tree)
    f = open('core/emit/main.ll', 'w')
    f.write(ret)
    f.close()


def repl():
    while 1:
        uin = input('>>> ')
        ran = run_code(uin)['data']
        if ran is not None:
            print(ran)


if len(sys.argv) > 1:
    if sys.argv[1][0] != '-':
        if sys.argv[1] == 'BC':
            run.run(open('core/emit/interm.rion', 'r').read())
        else:
            run_code(open(sys.argv[1]).read())
    else:
        f = open(sys.argv[2]).read()
        run.run(f)
else:
    repl()
