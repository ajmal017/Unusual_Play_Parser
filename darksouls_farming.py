def level_up(x):
    # print("\nLevel -> ", x, end='\n')
    return round(0.02 * (x * x * x) + 3.06 * (x * x) + 105.6 * x - 895)


def soul_farm(bool, soul_count):
    if(bool == 0):
        print("Die.")

        return;

    else:
        collected = (int)(input("How many souls are collected in one round?: "))
        time_minutes = (int)(input("How many minutes does it take?: "))
        time_seconds = (int)(input("How many seconds does it take?: "))
        farm_rounds = (int)(soul_count / collected)

        print("Souls needed:", soul_count, end = '\n')
        print("Rounds needed:", farm_rounds, end = '\n')

        new_minutes = (int)((time_seconds * farm_rounds) / 60) + (time_minutes * farm_rounds)
        new_seconds = (time_seconds * farm_rounds) % 60

        print("In order to collect,", soul_count, "souls, it will take", farm_rounds, "rounds. \nTotaling", new_minutes, "minutes and", new_seconds, "seconds.")
        return


soul_count = 0

current_level = (int)(input("What level are you now?: "))

desired_level = (int)(input("What level would you like to get to?: "))

for i in range((current_level + 1), (desired_level) + 1):
    soul_count = soul_count + level_up(i)

print("To get from level", current_level, "to level", desired_level, ", you will need", soul_count, "souls.")

answer = (int)(input("Perform soul farming calculations: "))

soul_farm(answer, soul_count)
