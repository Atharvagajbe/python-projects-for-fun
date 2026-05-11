from random import randint 

lower_number , higher_number = 1, 10
random_number = randint(lower_number, higher_number)
print(f"Guess a number between {lower_number} and {higher_number}")

while True:
    try :
        user_input = int(input("Enter your guess:"))
    except ValueError as e :
        print("Please enter a valid nunber")
        continue

    if user_input < random_number : 
        print("the number is greater than your guess")
    elif user_input > random_number :
        print("the number is less than your guess")
    else : 
        print("COngratulations! you guessed the number")
        break 