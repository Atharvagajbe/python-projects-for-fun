# Dice Roll

A simple Python command-line program that rolls multiple dice and prints the results.

## What It Does

- Asks the user how many dice they want to roll
- Rolls that many six-sided dice
- Prints the result as a list of numbers
- Lets the user type `exit` to quit the program

## How To Run

Open PowerShell in the `dice_roll` folder and run:

```powershell
python main.py
```

## Example

```text
enter the number of dice you want to roll:4
[2, 6, 1, 5]
enter the number of dice you want to roll:exit
thank you for playing!
```

## Rules

The program only allows rolling 2 or more dice. If the user enters a number less than 2, or enters something that is not a number, the program shows an error message.

## Files

- `main.py` - contains the dice rolling program
- `README.md` - explains how the project works
