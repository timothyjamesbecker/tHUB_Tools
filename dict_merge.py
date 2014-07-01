
#test data key '01' and '02' are duplicates
#but have different values for m['01'] to merge...
m1 = {'01':{'111':'111'},'02':{'001':'001'},'03':{'22':{'01':{'222':'222'}}}}
m2 = {'01':{'112':'112'},'03':{'001':'001'},'04':{'222':'222'}}
m3 = {}
m4 = {'00':{}}
def merge(m1,m2):
    m = {} #destination map
    for k in set(m1.keys() + m2.keys()):
        try:
            m.setdefault(k,[]).append(m1[k])        
        except KeyError: pass
        try:
            m.setdefault(k,[]).append(m2[k])          
        except KeyError:pass

    for k_i in m:
        if type(m[k_i]) is list:
            v = m.pop(k_i)                  #pop the value list for key k
            n = {}                          #non-duplicate map
            for e in v:                     #for every item
                for k_j in e.keys():        #for each key
                    n.update({k_j:e[k_j]})  #dig out the items
            m.update({k_i:n})               #put back the items         
    return m

for i in range (0,100000):
    m1 = merge(m1,m2)
    m3 = merge(merge(m3,m4),m1)

print(m3)

