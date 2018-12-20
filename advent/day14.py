def new_idxs(recipes, idxs):
    return [(1 + recipes[idx] + idx) % len(recipes) for idx in idxs]
    
def extend(r, idxs):
    new_num = str(sum(r[idx] for idx in idxs))
    r.extend(map(int, new_num))
    return r, new_idxs(r, idxs)
    


def run(n_times, n_recipes):
    recipes = list(map(int, '37'))
#     recipes = list(map(int, '03'))
#     recipes = list(map(int, '37'))
    idxs = range(len(recipes))
    for _ in range(n_times + n_recipes):
        recipes, idxs = extend(recipes, idxs)
    return ''.join(map(str, recipes[n_times:n_times + n_recipes])), idxs


run(30121, 10)

def run2(n_times):
    recipes = list(map(int, '37'))
#     recipes = list(map(int, '03'))
#     recipes = list(map(int, '37'))
    idxs = range(len(recipes))
    for _ in range(n_times):
        recipes, idxs = extend(recipes, idxs)
    return ''.join(map(str, recipes))

res = run2(100000000)

len(res)

'030121' in res

res.index('030121')
