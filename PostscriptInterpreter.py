#Trevor Mozingo
#Simplified Post Script Interpreter

'''
This is a simplified post script interpreter using only the primary operations.
Note: instead of the dict operator -> dictz will represent an operator that
creates a single empty dictionary and places it on the operator stack
-> begin will move the empty dictionary to the dictionary stack
'''

import re

opstack = []                                        #operator stack is used in the calculation process
dictstack = [{}]                                    #dictionary stack keeps track of variables and their definitions

program = """
/fact{
   dictz exch exch begin
      /n exch def
         n 2 lt
         { 1}
         {n 1 sub fact n mul }
      ifelse
   end
} def
5 fact =
"""                                                 #same factorial program -> note: handle "=" by calling printTop

statusValue = 0                                     #status value is used for keeping track of matching brackets

'''
Utility functions (status1-4) perform error checks
for the program
'''
def Status1(n, run):                                #status1 checks to make sure all brackets are matched up correctly
    global statusValue
    statusValue += n
    if run == 1:
        if statusValue < 0:                         #brackets should never occur to be negative when checking 
            print("error: 1 - bracket mismatch")
            exit(0)
    elif run == 0:
        if statusValue != 0:
            print("error: 1 - bracket mismatch")    #if the end of the statement is reached and the brackets do not cancel out (add to zero) then there is a bracket mismatch
            exit(0)

def Status2():                                      #status 2 checks to see if the opstack is empty before a pop operation
    if opstack == []:
        print("error: 2 - empty opstack")
        exit(0)

def Status3():                                      #status 3 checks to see if the dict stack is emtpy before a pop opeartion
    if dictstack == []:
        print("error: 3 - empty dictstack")
        exit(0)

def Status4():                                      #on lookup of a variable -> if it is not defined in the dictionary, then it dne so throw an error
    print("error: 4 - variable dne")
    exit(0)

def Status5():                                      #trap will catch invalid logic or code -> example: add with wrong variables etc
    print("error 5 - invalid program logic")
    exit(0)
    
def CreateArguments(programTokens):                 #create arguments will format all of the tokens into correct format for scopes and definitions of variables 
    programArguments = []   
    while programTokens != []:
        
        programArguments.append(programTokens.pop(0))

        try:                                        #check if input is a numerical value
            programArguments[-1] = int(programArguments[-1])
        except:
            pass

        if programArguments[-1] == "{":             #check if the input is a lhs bracket
            Status1(1 ,1)
            programArguments.pop()
            programArguments.append(CreateArguments(programTokens)) #if it is a lhs bracket, recursively fill the iterior of the bracket with the scoped arguments

        elif programArguments[-1] == "}":           #after the lhs bracket was filled with inner arguments, close it with the rhs bracket
            Status1(-1, 1)
            programArguments.pop()                  #for recursion purposes, if this is an inner scoped argument --> '['...']' ] ], then return the inner most brackets to be appended to the higher encapsulation
            return programArguments
    
    Status1(0, 0)                                   #check for brackets mismatch
    statusValue = 0                                 #set status value back to 0 
    return programArguments
          
def Tokenize(s):                                    #break apart program into its correct tokens
    programTokens = re.findall("/?[a-zA-Z][a-zA-Z0-9_]*|[-]?[0-9]+|%.*|[^ \t\n]", s)
    return CreateArguments(programTokens)           #now arrayify the tokens to prepare for execution

def opPush(value):                                  #trivial push operand onto stack
    opstack.append(value)

def dictPush(d):                                    #push new dictionary onto the stack
    dictstack.append(d)

def dictPop():                                      #pop the dictioanry off the stack
    Status3()
    return dictstack.pop()

def lookup(name):                                   #looks up variable in the dictionary current scope
    v = 0
    tmp = []
    
    for each1 in dictstack:
        tmp.append(each1)

    tmp.reverse()
    
    for each in tmp:
        v = each.get(name, "dictfault")             #if it is not in the scope -> return arbitrary value
        if v != "dictfault":
            return v
    if v == "dictfault":                            #if definition is not in any scope -> then it is a dictfault
        Status4()
    return v

def psIf():                                         #if statement -> if true, then perform the above operation
    rhs = opPop()
    lhs = opPop()
    lcopy = []                                      #create a copy so that the defintions are not modified later on
    
    if lhs == True:
        handler.clear()                             #clear the current argument
        for each in rhs:
            lcopy.append(each)
        Interpret(lcopy)                            #interpret the argument
        
def psIfElse():                                     #if else operation
    rhs = opPop()                                   #get the 2 programs
    mhs = opPop()
    lhs = opPop()

    lcopy = []
        
    if lhs == True:                                 #if true then execute the first program given
        handler.clear()
        for each1 in mhs:
            lcopy.append(each1)
        Interpret(lcopy)
        
    else:                                           #otherwise, execute the second argument
        handler.clear()
        for each in rhs:
            lcopy.append(each)
        Interpret(lcopy)
        
def psDef():                                        #define opeartion
    right = opPop()                                 #take the two values from the operand stack, and modify the first dictionary to map the variable to its value
    left = opPop()
    if dictstack == []:                             #if somehow the dictstack is empty -> create blank dictionary
        dictstack.append({})
    d = dictPop()
    d[left[1:]] = right
    dictPush(d)
    
def opPop():                                        #pop value from operator stack
    Status2()
    return opstack.pop()

def add():                                          #add 2 top opstack values
    opPush(opPop() + opPop())           
    
def sub():                              
    opPush((-1)*(opPop() - opPop()))                #subtract lhs from rhs given by top 2 stack values
     
def mul():                                          #multiply top 2 stack values
    opPush(opPop()*opPop())            
    
def div():                                          #divide top 2 stack values
    two = opPop()
    one = opPop()                       
    opPush(one/two)                     
    
def lt():                                           #check less than 
    opPush(opPop() > opPop())           
    
def gt():                                           #check greater than
    opPush(opPop() < opPop())  

def eq():                                           #check if equall
    opPush(opPop() == opPop()) 

def psand():                                        #logical and
    right = opPop()
    left = opPop()
    opPush(left and right)     
    
def psor():                                         #logical or
    right = opPop()
    left = opPop()
    opPush(left or right)      
    
def psnot():                                        #logical not
    opPush(not opPop())       

def dup():                                          #duplicate top opstack vaue
    val = opPop()
    opPush(val)
    opPush(val)

def exch():                                         #swap top 2 stack values
    val = opPop()
    val2 = opPop()
    opPush(val)
    opPush(val2)
    
def dictz():                                        #push empty dictionary onto operator stack
    d = {}       
    opstack.append(d)

def begin():                                        #move empty dictionary to dictionary stack
    d = opstack.pop()
    if d != {}:                                     #trying to call begin without dictionary on the opstack throws an error
        print("error 6 - not a dictionary");
        exit(0)
    dictstack.append(d) 
    
def end():                                          #pop dictionary from the dictioanry stack
    return dictstack.pop()

'''
These trivial print functions will
provide the contents of each
stack
'''
def printTop():                                     #top of opearator stack (the result) gets printed
    print("-----Operator Stack Top (result)------")
    tmp = opstack.pop()
    print(tmp)
    opstack.append(tmp)
    print("--------------------------------------")
    
def stack():                                        #the entire stack gets printed
    tmp = []
    print("------------Operator Stack------------")
    while opstack != []:
        tmp.append(opstack.pop())
        print(tmp[-1])
    while tmp != []:
        opstack.append(tmp.pop())
    print("--------------------------------------")
    
def dstack():                                       #this will print the contents of the dictionary stack
    tmp = []
    print("-----------Dictionary Stack-----------")
    while dictstack != []:
        tmp.append(dictstack.pop())
        print(tmp[-1])
    while tmp != []:
        dictstack.append(tmp.pop())
    print("-------------------------------------")

functionDictionary = {}                             #stores all of the functions

'''
Build Dictionary will create a dictionary of
the functions so that when a string is read
from the program -> that string will be
looked up in this function table and call the
function -> if the string is not
in this dictioanry, then an alternate function is called
'''
def BuildDictionary():
    global functionDictionary
    functionDictionary["="] = printTop
    functionDictionary["if"] = psIf     
    functionDictionary["ifelse"] = psIfElse  
    functionDictionary["pop"] = opPop
    functionDictionary["def"] = psDef
    functionDictionary["add"] = add
    functionDictionary["sub"] = sub
    functionDictionary["mul"] = mul
    functionDictionary["div"] = div
    functionDictionary["lt"] = lt
    functionDictionary["gt"] = gt
    functionDictionary["eq"] = eq   
    functionDictionary["and"] = psand
    functionDictionary["or"] = psor
    functionDictionary["not"] = psnot   
    functionDictionary["dup"] = dup
    functionDictionary["exch"] = exch
    functionDictionary["dictz"] = dictz
    functionDictionary["begin"] = begin
    functionDictionary["end"] = end
    functionDictionary["printTop"] = printTop
    functionDictionary["stack"] = stack

handler = []                                        #if an alternate function is called -> the parameters will be held in handler

def Alternate():                                    #this is the alternate function that is called if a program argument is not a post script command
    global handler
    if type(handler[0]) == str:
        
        if handler[0][0] == "/":                    #if /somevar then push it onto the operator stack
            opPush(handler[0])

        elif handler[0] == "true":                  #if it is a bool true -> push True
            opPush(True)
            
        elif handler[0] == "false":                 #if bool false -> push False
            opPush(False)
        else:
            l = lookup(handler[0])                  #look up variable name
            
            if type(l) == list:                     #if it is a function with arguments
                lcopy = []
                
                for each in l:
                    lcopy.append(each)
                    
                handler.clear()
                Interpret(lcopy)                    #execute the arguments
                return
            opPush(l)                               #push the result of the function onto the stack
                       
    elif type(handler[0]) == list:                  #if argument is a list of arguments- { 1 1 add } would be in list, so push onto stack
        opPush(handler[0])
    
    elif type(handler[0]) == int:                   #if it is a number -> push it onto stack
        opPush(handler[0])
    handler.clear()
        
def Operate(Argument):                              #operate will read all of the program arguments and execute them
    global functionDictionary
    global handler
    handler.append(Argument)
    action = Alternate
    try:
        action = functionDictionary.get(Argument, Alternate) #check to see if argument is in dictionary, if not, call different function
    except:
        pass
    action()
    handler.clear()

def Interpret(programArguments):
    while programArguments != []:
        try:
            Operate(programArguments.pop(0))                #pass each argument into operate
        except:
            Status5()

def Run(program):
    BuildDictionary()                                       #construct function dictionary
    programArguments = Tokenize(program)                    #tokenize and arrayify arguments
    Interpret(programArguments)                             #interpret the arguments

Run(program)
dstack()
stack()






