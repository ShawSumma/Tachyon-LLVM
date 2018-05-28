from llvmlite import ir
module = ir.Module()
# for i in dir(ir):
#     print(i) if 'Type' in i else ()
efns = {}
types = {}
ptrs = {}
fnty = {}
fnptrs = {}
argty = {}
retstack = []
def gtype(name):
    # print(name)
    if isinstance(name, str):
        name = {'type':'name', 'data':name}
    if name['type'] == 'name':
        name = name['data']
        if name == 'int' or name == int:
            return ir.IntType(64)
        if name == 'bool' or name == int:
            return ir.IntType(1)
        if name == 'float' or name == float:
            return ir.FloatType()
        if name == 'void' or name == None:
            return ir.IntType(64)
            # return ir.VoidType()
    if name['type'] == 'index':
        count = name['index'][0]['data']
        type = gtype(name['pre'])
        return ir.ArrayType(type, int(count))
    if name['type'] == 'list':
        print(name)
def require(name, fnty, argty):
    global efns
    if name in efns:
        return efns[name]
    else:
        fn = ir.FunctionType(fnty, argty)
        efns[name] = ir.Function(module, fn, name)
        return efns[name]
def rwalk(tree, want='return'):
    if tree['type'] == 'int':
        return gtype('int')
    elif tree['type'] == 'float':
        return gtype('float')
    elif tree['type'] == 'oper':
        pre = rwalk(tree['pre'])
        post = rwalk(tree['post'])
        if pre != post:
            print('line %s' % tree['line'])
            print('types prior to and after operator are missmatched')
        return pre
    elif tree['type'] == 'tuple' or tree['type'] == 'code':
        return rwalk(tree['data'][-1])
    elif tree['type'] == 'fn':
        return fnty[tree['fn']['data']]
    else:
        print('cant get type')
        print(tree)
        exit()
def tc(tree, state, expects=None, stage=None, eargs=[]):
    global types, ptrs, fnty, argty
    if stage == 'file':
        lis = []
        for i in tree:
            lis.append([i, tc(i, state, stage='fn-def')])
        for i, j in lis:
            tc(i, state, stage='fn-body', eargs=j)
    elif stage == 'fn-def':
        # print(tree)
        pre = tree['pre']
        fn = pre['fn']
        perams = pre['perams']
        name = fn['data']
        body = tree['post']
        etype = tree['data']
        oty = gtype(etype['data'])
        tys = []
        for pl, i in enumerate(perams):
            tup = ('arg', name, pl)
            fnty[tup] = gtype(i['datatype'])
            tys.append(fnty[tup])
        fty = ir.FunctionType(oty, tys)
        fnty[name] = oty
        fn = ir.Function(state, fty, name)
        fnptrs[name] = fn
        blck = fn.append_basic_block(name='body')
        blck = ir.IRBuilder(blck)
        return [blck, body, oty, zip(fn.args, perams)]
    elif stage == 'fn-body':
        blck, body, oty, zp = eargs
        types = {}
        ptrs = {}
        for ptr, j in zp:
            jtype = j['datatype']
            name = j['data']
            ptrs[name] = ptr
            types[name] = gtype(jtype)
        return blck.ret(tc(body, blck, expects=oty))
    elif tree['type'] == 'int':
        return ir.Constant(gtype('int'), int(tree['data']))
    elif tree['type'] == 'oper':
        oper = tree['oper']
        if oper in ['+','-','*','/','%']:
            pre = tc(tree['pre'], state, expects=expects)
            post = tc(tree['post'], state, expects=expects)
            if oper == '+':
                ret = state.add(pre, post)
            if oper == '-':
                ret = state.sub(pre, post)
            if oper == '*':
                ret = state.mul(pre, post)
            if oper == '/':
                ret = state.sdiv(pre, post)
            if oper == '%':
                ret = state.srem(pre, post)
            return ret
        if oper in ['==', '!=', '<', '>', '<=', '>=']:
            pre = tc(tree['pre'], state, expects=expects)
            post = tc(tree['post'], state, expects=expects)
            got = state.icmp_unsigned(oper, pre, post)
            return got
        else:
            print('unknown op', oper)
            exit()
    elif tree['type'] == 'tuple' or tree['type'] == 'code':
        expt = state.alloca(expects)
        for i in tree['data']:
            got = tc(i, state, expects=expects)
            state.store(got, expt)
        return state.load(expt)
    elif tree['type'] == 'fn':
        name = tree['fn']['data']
        # print(fnty)
        if name == 'put':
            args = [tc(i, state, expects=gtype('int')) for i in tree['perams']]
            fn = require('putchar', expects, [i.type for i in args])
        else:
            args = [tc(i, state, expects=fnty[('arg', name, pl)]) for pl, i in enumerate(tree['perams'])]
            fn = fnptrs[name]
        call = state.call(fn, args)
        if call.type != expects:
            c = str(call.type)
            e = str(expects)
            if c == 'void' and e == 'i64':
                return ir.Constant(gtype('int'), 0)
            if c == 'i64' and e == 'void':
                return ir.Constant(gtype('void'))
        return call
    elif tree['type'] == 'name':
        return ptrs[tree['data']]
    elif tree['type'] == 'if':
        cond64 = tc(tree['condition'], state)
        boolcond = state.trunc(cond64, ir.IntType(1))
        ret = state.alloca(expects)
        with state.if_else(boolcond) as (then, otherwise):
            with then:
                blck = then.args[0]
                state.store(tc(tree['then'], blck, expects=expects),ret)
            with otherwise:
                blck = then.args[0]
                state.store(tc(tree['else'], blck, expects=expects),ret)
        return state.load(ret)
    else:
        print(tree)
        exit()
def make(tree):
    global jitll
    # import view
    # view.view(tree)
    tc(tree, module, stage='file')
    ret = str(module)
    ret = ret.split('\n')
    ret = ret[3:]
    ret = '\n'.join(ret)
    ret = ';opt -S -O3 -o core/emit/main.ll core/emit/main.ll; lli core/emit/main.ll\n'+ret
    return ret
