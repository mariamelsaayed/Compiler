import sys
import networkx as nx
import matplotlib.pyplot as plt
import random

G = nx.DiGraph()
output=[]
def draw(token):
    pos = hierarchy_pos(G,output[0][0])
    nx.draw(G,pos=pos, with_labels=True,node_size=5000,node_color='pink')
    plt.draw()
    plt.show()

def hierarchy_pos(G, root=None, width=1., vert_gap = 0.2, vert_loc = 0, xcenter = 0.5):

    if not nx.is_tree(G):
        raise TypeError('cannot use hierarchy_pos on a graph that is not a tree')

    if root is None:
        if isinstance(G, nx.DiGraph):
            root = next(iter(nx.topological_sort(G)))  #allows back compatibility with nx version 1.11
        else:
            root = random.choice(list(G.nodes))

    def _hierarchy_pos(G, root, width=1., vert_gap = 0.2, vert_loc = 0, xcenter = 0.5, pos = None, parent = None):
        
        if pos is None:
            pos = {root:(xcenter,vert_loc)}
        else:
            pos[root] = (xcenter, vert_loc)
        children = list(G.neighbors(root))
        if not isinstance(G, nx.DiGraph) and parent is not None:
            children.remove(parent)  
        if len(children)!=0:
            dx = width/len(children) 
            nextx = xcenter - width/2 - dx/2
            for child in children:
                nextx += dx
                pos = _hierarchy_pos(G,child, width = dx, vert_gap = vert_gap, 
                                    vert_loc = vert_loc-vert_gap, xcenter=nextx,
                                    pos=pos, parent = root)
        return pos


    return _hierarchy_pos(G, root, width, vert_gap, vert_loc, xcenter)

index = 0

def if_stmt(token,i):
    
    i += 1
    if(i>=len(token)):
             print('Illegal grammar rule if_stmt:no exp after if')
             parser(token,i)
    i,exp_node = exp(token,i)
    
    G.add_edge('if',exp_node)
    
    if(token[i][1] == 'THEN'):
        #G.add_node('then')
        i += 1
        if(i>=len(token)):
             print('Illegal grammar rule if_stmt: no then after if')
             #TODO I guess this should be sys.exit() as the rule is wrong
             parser(token,i)
             
        i, stmt_seq_node = stmt_seq(token,i)
        
        G.add_edge('if',stmt_seq_node)
        
    else:
        print('Illegal grammar rule if_stmt')
        sys.exit()

    if(token[i][1] == 'ELSE'):
        #G.add_node('else')
        i += 1
        if(i>=len(token)):
             print('Illegal grammar rule if_stmt: no statment after else')
             #TODO I guess this should be sys.exit() as the rule is wrong
             parser(token,i)
             
        i, stmt_seq_node = stmt_seq(token,i)

        G.add_edge('if','else')
        G.add_edge('else',stmt_seq_node)
        
    if(token[i][1] == 'END'):
        #G.add_node('end')
        i += 1
        if(i>=len(token)):
             print('program ended successfuly')
             return i,'if'
             parser(token,i)
    else:
        print('Illegal grammar rule if_stmt: no end')
        sys.exit()
    i = stmt_seq(token,i) # msh 3rfa leh ndhna hna
    return i,'if'
    
    
            

def repeat_stmt(token,i):
    i += 1
    if(i>=len(token)):
             print('7aseb error len: el prog 5ls')
             parser(token,i)
             
    i = stmt_seq(token,i)
    if(token[i][1] == 'UNTIL'):
        G.add_node('until')
        i = exp(token,i)
    else:
        print('7aseb error')
        sys.exit()
    return i
    


def assign_stmt(token,i):
    print('assign_stmt')
    i += 1
    print('i=',i)
    if(i>=len(token)):
             print('Illegal grammar rule assign_stmt')
             #TODO I guess this should be sys.exit() as the rule is wrong
             parser(token,i)
             
    if(token[i][0] == ':='):
        
        assign_node = str('assign ('+ token[i-1][0] + ')')
        #G.add_node(node)
        
        i += 1
        if(i>=len(token)):
             print('Illegal grammar rule assign_stmt')
             #TODO I guess this should be sys.exit() as the rule is wrong
             parser(token,i)
             
        i,exp_node = exp(token,i)
        G.add_edge(assign_node,exp_node)
        
    else:
        print('Illegal grammar rule assign_stmt')
        sys.exit()
    return i, assign_node
    

def read_stmt(token,i):
    print('wsl l read_stmt')
    i += 1
    if(i>=len(token)):
             print('Illegal grammar rule read_stmt not finished')
             #TODO I guess this should be sys.exit() as the rule is wrong
             parser(token,i)
    
    if(token[i][1] == 'IDENTIFIER'):
        
        read_node = str('read ('+ token[i][0] + ')')
        #G.add_node(read_node,node_shape='d')
        output.append([read_node,'READ'])
        #G.add_node(node)
        
        print(token[i][0])
        i += 1
        if(i>=len(token)):
             print('read_stmt finished')
             # momkn y5leh y-return hna msln
             parser(token,i)# but what if this was wrong, msln el mfrod fe ba2y if_stmt msln
        print('fe ID i:',i)
    else:
        print('Illegal grammar rule read_stmt')
        sys.exit()
        
    return i,read_node
    


def write_stmt(token,i):
    
    G.add_node('write')
    i += 1
    if(i>=len(token)):
        print('7aseb error len: el prog 5ls')
        parser(token,i)
         
    i = exp(token,i)
    return i

def exp(token,i):
    i,s_exp_node = simple_exp(token,i)
    flag,i,prev_comp_node = comparison_op(token,i)
    if flag:
        parent_comp_node = prev_comp_node
        G.add_edge(parent_comp_node,s_exp_node)
    #print('edgde added')
        while flag:
            print('d5l comp',i)
            i,s_exp_node = simple_exp(token,i)
            flag,i,comp_node = comparison_op(token,i)
            if (flag==True):
                G.add_edge(comp_node,s_exp_node)
                prev_comp_node = comp_node
            elif(flag == False):
                G.add_edge(prev_comp_node,s_exp_node)
                break
    else:
        parent_comp_node = s_exp_node
    return i, parent_comp_node

def comparison_op(token,i):
    if token[i][0] == '<' or token[i][0] == '>' or token[i][0] == '=':
        #TODO create node fel tree
        node = str('op ('+ token[i][0] + ')')
        print('d5l comp i=',i)
        #G.add_node(node)
        
        #print(token,i)
        i += 1
        if(i>=len(token)):
             print('Illegal grammar rule comparison_op')
             #TODO I guess this should be sys.exit() as the rule is wrong
             parser(token,i)
        return True,i,node
    else:
        print('Illegal grammar rule comparison_op')
        return False,i,None
        #sys.exit()

def simple_exp(token,i):
    i,t_node = term(token,i)
    flag,i,node = addop(token,i)
    if flag == False:
        return i, t_node
    else:        
        while flag:
            #i += 1 #t2rebn
            i,node = term(token,i)
            flag,i,node = addop(token,i)
    return i, node


def term(token,i):
    i, f_node = factor(token,i)
    flag,i,node = mulop(token,i)
    if flag == False:
        return i, f_node
    else:        
        while flag==True:
            #i += 1 #t2rebn
            i, node = factor(token,i)
            flag,i,node = mulop(token,i)
    return i, node

def addop(token,i):
    if token[i][0] == '+' or token[i][0] == '-':
        #TODO create node fel tree
        node = str('op ('+ token[i][0] + ')')
        #G.add_node(node)
        
        #print(token)
        i += 1
        if(i>=len(token)):
             print('Illegal grammar rule addop')
             #TODO I guess this should be sys.exit() as the rule is wrong
             parser(token,i)
        return True,i,node
    else:
        print('not addop')
        return False,i,None
        #sys.exit()
    #return i


def mulop(token,i):
    if token[i][0] == '*' or token[i][0] == '/' :
        #TODO create node fel tree
        node = str('op ('+ token[i][0] + ')')
        #G.add_node(node)
        
        #print(token)
        i += 1
        if(i>=len(token)):
             print('Illegal grammar rule mulop')
             parser(token,i)
        return True,i,node
    else:
        print('not mulop')
        return False,i,None
        #sys.exit()

def factor(token,i):
    if token[i][0] == '(':
        i += 1
        if(i>=len(token)):
             print('Illegal grammar rule factor')
             #TODO
             parser(token,i)
             
        i,node = exp(token,i)
        #TODO draw?
        i += 1
        if(i>=len(token)):
             print('Illegal grammar rule factor')
             #TODO
             parser(token,i)
             
        if token[i][0] == ')':
            i += 1
            if(i>=len(token)):
             print('factor finished successfuly')
             parser(token,i)
             
        else:
            print('Illegal grammar rule factor')
            sys.exit()
            
    elif token[i][1] == 'NUMBER' or token[i][1] == 'IDENTIFIER':
        #print('fh')
        #TODO create node fel tree
        if(token[i][1] == 'NUMBER'):
            node = str('const ('+ token[i][0] + ')')
            
        elif(token[i][1] == 'IDENTIFIER'):
            node = str('id ('+ token[i][0] + ')')
        
        #G.add_node(node)
        
        #print(token[i][0])
        i += 1
        if(i>=len(token)):
             print('factor finished successfuly')
             parser(token,i)
    else:
        print('Illegal grammar rule factor')
        sys.exit()
    return i, node
        


def stmt_seq(token,i):
    print('stmt_seq')
    
    i,stmt_node = stmt(token,i)
    prev_node = stmt_node
    
    print('i=',i)
    print('hna')
    while(token[i][1]=='SEMICOLON'):
        i += 1
        if(i<len(token)):
            i,next_node = stmt(token,i)
            G.add_edge(prev_node,next_node)
            prev_node = next_node
            if(i>=len(token)):
                parser(token,i)
        else:
            #m3na kda en mfesh 7aga b3dha
            #TODO tb lw fe 7aga ablaha? :')
            G.add_node(prev_node)
            print('stmt_seq finished successfuly')
            parser(token,i)
        '''
        if(i>=len(token)):
                print('stmt_seq finished successfuly')
                parser(token,i)
        '''
        
        
        

        
    '''
    while(1):
        print('fe while i:',i)
        print('hna brdo')
        if(token[i][1]=='SEMICOLON'):
            #TODO create node fel tree 
            print(token)
            i += 1
            if(i>=len(token)):
                print('7aseb error len: el prog 5ls')
                parser(token,i)
                     
            i = stmt(token,i)
        else:
            print('msh semicolon')
            sys.exit()
    '''
    return i,prev_node
        
        

def stmt(token,i) :
    print('stmt')
    print('i=',i)
    if(token[i][1] == 'IF'):
        print('d5l if')
        #G.add_node('if')
        i, node = if_stmt(token,i)
        if(i>=len(token)):
            print('stmt finished')
            return i,node 
            parser(token,i)
        
    elif(token[i][1] == 'REPEAT'):
        G.add_node('repeat')
        i = repeat_stmt(token,i)
        if(i>=len(token)):
            print('stmt finished')
            parser(token,i)
        
    elif (token[i][1] == 'IDENTIFIER'):
        i,node = assign_stmt(token,i)
        if(i>=len(token)):
            print('stmt finished')
            parser(token,i)
        
    elif(token[i][1]=='READ'):
        print('read wslt')
        i,node = read_stmt(token,i)
        if(i>=len(token)):
            print('stmt finished')
            parser(token,i)
            
        
    elif(token[i][1]=='WRITE'):
        i = write_stmt(token,i)
        if(i>=len(token)):
            print('stmt finished')
            parser(token,i)
        
    else :
        print('Illegal grammar rule stmt')
        sys.exit()
    return i,node 

def parser(token,m):
    print(token)
    if(m>=len(token)):
        #pos = hierarchy_pos(G,token[0][0])
        
        draw(token)
        #plt.savefig("path.png")
        sys.exit()
        
        
    else:
        while(m<len(token)):
            print('hiii ',m)
            m,node = stmt_seq(token,m)

tokens = input("Enter list")
lo = []

token_li = tokens.split("$")#TODO lma n-create el gui nbadlha b eno y-replace \n b ; b3d kda y-split
for k in range(len(token_li)):
    token_list = token_li[k].split(",")
    token_list = [x.strip(' ') for x in token_list]
    lo.append(token_list)



print(lo)
parser(lo,0)


nx.draw(G, with_labels=True)
plt.draw()
plt.show()



