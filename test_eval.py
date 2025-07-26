user_input = input("Enter math expression: ")
result = eval(user_input)  # INSECURE
print("Result:", result)