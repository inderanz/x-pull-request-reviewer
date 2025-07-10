import os

def insecure_function(user_input):
    # Command injection vulnerability
    os.system("echo " + user_input)

def unused_function():
    pass

def bad_style():
    print(  "Hello, world!"  ) # Extra spaces
    x=1
    y =2
    if x==y:
        print("Equal")
    else:
        print( "Not equal" )

# No docstrings, no type hints, bad naming, unused imports, no error handling
