import random

def roll_dice(num_dice: int = 2) -> list[int]:
    if num_dice < 2:
        raise ValueError

    rolls: list[int] = []
    for i in range(num_dice):
        random_number = random.randint(1,6)
        rolls.append(random_number)
    
    return rolls

def main():
    while True:
        try:
            user_input: str = input("enter the number of dice you want to roll:")

            if user_input.lower() == "exit":
                print("thank you for playing!")
                break 

            print(roll_dice(int(user_input)))

        except ValueError:
            print("please enter a valid number")
        
if __name__ == "__main__":
    main()


  

        


