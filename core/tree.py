# pairs mathching tokens
import pair
# error handleing
import errors

# trees code inside parens


def tree_paren(code):
    # raw token data
    datas = [i['data'] for i in code]
    # get pairs for each type
    pairs = {
        'paren': pair.pair(datas, ['(', ')']),
        'curly': pair.pair(datas, ['{', '}']),
        'square': pair.pair(datas, ['[', ']']),
    }
    pl = 0
    ret = [[]]
    # iterate over and make tuples and code out of the comma placement
    while pl < len(code):
        # is it left
        if pl in pairs['paren']:
            jmp = pairs['paren'][pl]
            rap = {
                'type': 'tuple',
                'data': tree_paren(code[pl + 1:jmp]),
            }
            ret[-1].append(rap)
            pl = jmp
        # is it right
        elif pl in pairs['curly']:
            jmp = pairs['curly'][pl]
            rap = {
                'type': 'code',
                'data': tree(code[pl + 1:jmp]),
            }
            ret[-1].append(rap)
            pl = jmp\
                # is it comma
        elif code[pl]['type'] == 'comma':
            ret.append([])
        # its not a paren or comma
        else:
            ret[-1].append(code[pl])
        pl += 1
    # delete empty sequences
    # this is why (1,,1,,1,,) returns [1,1,1]
    while [] in ret:
        del ret[ret.index([])]
    recal = []
    for i in ret:
        recal.append(tree_line(i))
    return recal

# a single "line" of code, lines end at newlines outside of paired things


def tree_line(code):
    # none is deleted, so no empty lines
    if len(code) == 0:
        return None
    # raw token data
    datas = [i['data'] for i in code]
    # types of tokens
    types = [i['type'] for i in code]
    # currently implemneted: if, else, loop, and while
    # if datas[0] == 'if':
    #     elval = tree_line(code[-1]) if datas[-2] == 'else' else None
    #     stp = -3 if datas[-2] == 'else' else -1
    #     ret = {
    #         'type': 'flow',
    #         'flow': datas[0],
    #         'condition': tree_line(code[1:stp]),
    #         'then': code[stp],
    #         'else': elval
    #     }
    #     return ret
    # its just a return value
    if len(code) == 1:
        return {'type': code[0]['type'], 'data': code[0]['data'], 'line': code[0]['line'] if 'line' in code[0] else None}
    # its math or listop
    if 'oper' in types:
        finds = []
        # error and listop
        finds += [['error'], ['.'], ['!', '!!'], ['..']]
        # common math
        finds += [['**', '^'], ['*', '/', '%'], ['+', '-']]
        # <> is in, not implemneted fully, equality part 1
        finds += [['<>'], ['<', '>', '<=', '>=']]
        # equality part 2
        finds += [['!=', '=='], ['||', '&&']]
        # list push and pop
        finds += [['->', '<-']]
        # ternary
        finds += [[':', '?']]
        # set
        finds += [['=']]
        # finds += [['-=', '+=', '/=', '**=', '*=', '=', '?=']]
        # its backwards
        finds = finds[::-1]
        # ob is operator break flag
        ob = False
        # finds operator that best matches
        for order in finds:
            for oper in order:
                if oper in datas:
                    ob = True
                    break
            if ob:
                break
        # if it was not fount: raise an error
        if oper == 'error':
            errors.e_unk_oper(datas[types.index('oper')])
        # list of backwards operators
        negitive = ['.', '->', '-']
        if oper not in negitive:
            oper_ind = datas.index(oper)
        else:
            oper_ind = len(datas) - 1 - datas[:: -1].index(oper)
        # set operators get their own logic
        if oper == ':':
            pli = datas.index('?')
            ple = len(datas)-datas[::-1].index(':')
            ret = {
                'type': 'if',
                'condition': tree_line(code[:pli]),
                'then': tree_line(code[pli+1:ple-1]),
                'else': tree_line(code[ple:])
            }
            return ret
        if oper in ['=']:
            pre = code[:oper_ind]
            isfn = isinstance(pre[-1], dict) and pre[-1]['type'] == 'tuple'
            pres = tree_line(pre[-2:]) if isfn else tree_line(pre[-1:])
            data = tree_line(pre[:-2]) if isfn else tree_line(pre[:-1])
            return {
                'type': 'set',
                'set': datas[oper_ind],
                'pre': pres,
                'post': tree_line(code[oper_ind + 1:]),
                'data': data
            }
        if oper == '.':
            code[oper_ind + 1]['type'] = 'str'
        return {
            'type': 'oper',
            'oper': oper,
            'pre': tree_line(code[:oper_ind]),
            'post': tree_line(code[oper_ind + 1:])
        }
    if types in [['name', 'name'],['name', 'list', 'name']]:
        return {
            'type': 'type',
            'data': code[1]['data'],
            'datatype': code[0]['data'],
        }
    # handle regular and multi tuples
    if len(code) > 1 and code[-1]['type'] == 'list':
        return {
            'type': 'index',
            'pre': tree_line(code[:-1]),
            'index': code[-1]['data']
        }
    if len(code) > 1 and code[-1]['type'] == 'tuple':
        return {
            'type': 'fn',
            'fn': tree_line(code[:-1]),
            'perams': code[-1]['data']
        }
# what to call from external code, code is tokens from lex.py


def tree(code, typ='newline'):
    # raw token datsa
    datas = [i['data'] for i in code]
    # get pairs for each type
    pairs = {
        'paren': pair.pair(datas, ['(', ')']),
        'curly': pair.pair(datas, ['{', '}']),
        'square': pair.pair(datas, ['[', ']']),
    }
    pl = 0
    ret = [[]]
    # iterate over and make tuples and code out of the comma placement
    while pl < len(code):
        # is it left
        if pl in pairs['paren']:
            jmp = pairs['paren'][pl]
            rap = {
                'type': 'tuple',
                'data': tree_paren(code[pl + 1:jmp]),
            }
            ret[-1].append(rap)
            pl = jmp
        elif pl in pairs['square']:
            jmp = pairs['square'][pl]
            rap = {
                'type': 'list',
                'data': tree_paren(code[pl + 1:jmp]),
            }
            ret[-1].append(rap)
            pl = jmp
        # is it right
        elif pl in pairs['curly']:
            jmp = pairs['curly'][pl]
            rap = {
                'type': 'tuple',
                'data': tree(code[pl + 1:jmp]),
            }
            ret[-1].append(rap)
            pl = jmp
        # it is newline
        elif code[pl]['type'] == 'newline':
            ret.append([])
        # its not left, right, or newline
        else:
            ret[-1].append(code[pl])
        pl += 1
    while [] in ret:
        del ret[ret.index([])]
    recal = []
    for i in ret:
        recal.append(tree_line(i))
    return recal
