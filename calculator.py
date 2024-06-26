import json
from os import path, mkdir, name, system
from configparser import ConfigParser, NoOptionError, NoSectionError
from math import sin, cos, tan, radians, sqrt

VERSION = "1.1"

class ConfigManager:
    '''
    Class that implements default methods to manage calculator configs
    '''

    def __init__(self) -> None:
        '''
        Class constructor that inits config files
        '''
        self.__path = "calc_data/settings.ini"
        self.__default_savepath = "\"calc_data/saved_actions.json\""
        self.__config = ConfigParser()  

        self.__initconfig()  

    def __ensureoption(self, option: str, default: str) -> str:
        '''
        Ensures that a config option exists in Calculator section, if not, creates it with default value
        :param config: ConfigParser object
        :param option: field to check
        :param default: default value for the field
        :return: value of the option
        '''
        try:
            return self.__config.get("Calculator", option)
        except (NoSectionError, NoOptionError):
            if not self.__config.has_section("Calculator"):
                self.__config.add_section("Calculator")
            self.__config.set("Calculator", option, default)
            return default

    def __initconfig(self) -> None:
        '''
        Creates calc_data folder if it doesn't exist, and fills config at default __CONFIG_PATH with 
        default template if it's empty
        '''
        if not path.exists('calc_data'): mkdir('calc_data')

        self.__config.read(self.__path)

        self.__ensureoption("showhistory", str(True))
        self.__ensureoption("savepath", self.__default_savepath)
        self.__ensureoption("showentrysum", str(True))

        with open(self.__path, 'w') as ini:
            self.__config.write(ini)
 
    def getconfigfield(self, field: str) -> str:
        '''
        Reads field of config of calculator at default __CONFIG_PATH
        :param field: field to read
        :return: read data in string format
        '''
        try:
            self.__config.get("Calculator", field)
        except (NoOptionError, NoSectionError):
            print(f"Failed to read field '{field}' in {self.__path}")
            return None
        
        return self.__config.get("Calculator", field).replace('"', '')

class SaveManager:
    '''
    Class that has methods to manage calculator saves
    '''
    def __init__(self, configs: ConfigManager) -> None:
        '''
        Class constructor that initialises saves
        :param config: ConfigManager object to get configs from
        '''
        self.__config = configs

        self.__initsaves()


    def __initsaves(self) -> None:
        '''
        Creates save file at path in config file if it isn't present
        '''
        try:
            self.__path = self.__config.getconfigfield("savepath")
        except NoOptionError:
            print(f"Failed to read config path")
            quit()
        except NoSectionError:
            self.__path = self.__config.getconfigfield("savepath")

        if not path.exists(self.__path):
            with open(self.__path, 'a', encoding='utf-8'): pass
        
        with open(self.__path, 'r+', encoding='utf-8') as save:
            if len(save.read()) == 0: json.dump({"actions": []}, save, indent=4)

    def saveaction(self, action: str, result: float) -> None:
        '''
        Saves a calculator action in json file with format {"action": result}
        :param action: action to save
        :param result: result of action to save in float
        '''
        with open(self.__path, 'r', encoding='utf-8') as rsave:
            actionlist: list = json.load(rsave)["actions"]
            actionlist.append({action: result})

        with open(self.__path, 'w', encoding='utf-8') as wsave:
            json.dump({"actions": actionlist}, wsave, indent=4)
    
    def getentries(self, number: int) -> list[dict]:
        '''
        Gets last N of entries from json save file
        :param number: number of entries to get
        :return: list of entries in string
        '''
        with open(self.__path, 'r', encoding='utf-8') as rsave:
            actionlist: list = json.load(rsave)["actions"]
        
        return actionlist[-number:]
    
    def clear(self) -> None:
        '''
        Clears the save file
        '''
        with open(self.__path, 'w', encoding='utf-8') as wsave:
            json.dump({"actions": []}, wsave, indent=4)

class CalculatorMethods:
    '''
    Class that implements calculator methods
    '''

    def __init__(self, saves: SaveManager, configs: ConfigManager) -> None:
        '''
        Class constructor
        :param saves: SaveManager object
        :param configs: ConfigManager object
        '''
        self.__saves = saves
        self.__configs = configs

        self.__actionsigns = {'+': self.__add, '-': self.__subtract, '/': self.__divide, '*': self.__multiply, 
                              'sin': self.__sin, 'cos': self.__cos, 'tan': self.__tan, 
                              'sqrt': self.__sqrt, 'stop': None, 'clear history': None}

    def __add(self, *args: float) -> float:
        '''
        Adds two numbers
        :param 1: first number to add
        :param 2: second number to add
        :return: sum of param 1 and param 2
        '''
        return args[0] + args[1]

    def __subtract(self, *args: float) -> float:
        '''
        Subtracts two numbers
        :param 1: first number to subtract
        :param 2: second number to subtract
        :return: difference of param 1 and param 2
        '''
        return args[0] - args[1]

    def __divide(self, *args: float) -> float:
        '''
        Divides two numbers
        :param 1: first number to divide
        :param 2: second number to divide
        :return: quotient of param 1 and param 2
        '''
        return args[0] / args[1]

    def __multiply(self, *args: float) -> float:
        '''
        Multiplies two numbers
        :param 1: first number to multiply
        :param 2: second number to multiply
        :return: product of param 1 and param 2
        '''
        return args[0] * args[1]
    
    def __sin(self, *args: float) -> float:
        '''
        Calculates the sine of a number
        :param 1: number to calculate the sine of (in degrees)
        :return: sine of param 1
        '''
        return sin(radians(args[0]))
    
    def __cos(self, *args: float) -> float:
        '''
        Calculates the cosine of a number
        :param 1: number to calculate the cosine of (in degrees)
        :return: cosine of param 1
        '''
        return cos(radians(args[0]))
    
    def __tan(self, *args: float) -> float:
        '''
        Calculates the tangent of a number
        :param 1: number to calculate the tangent of (in degrees)
        :return: tangent of param 1
        '''
        return tan(radians(args[0]))
    
    def __sqrt(self, *args: float) -> float:
        '''
        Calculates the square root of a number
        :param 1: number to calculate the square root of
        :return: square root of param 1
        '''
        return sqrt(args[0])

    def process(self) -> None:
        '''
        Gets user input, and then executes the calculator action and then saves it into json file
        '''
        print('=============================')
        print(f'   WARDEN-CALCULATOR V {VERSION}   ')
        print('=============================')

        print("\nAvailable actions:\n")
        for i in self.__actionsigns.keys():
            print(f"> {i}")

        print("\nWARNING! sin, cos, tan are in degrees")

        if self.__configs.getconfigfield("showhistory").capitalize() == str(True):
            print("\nCalculator History (last 5 entries):")
            for i in self.__saves.getentries(5):
                print(f"{list(i.keys())[0]} = {list(i.values())[0]}")

            if self.__configs.getconfigfield("showentrysum").capitalize() == str(True):
                print(f"\nSum of entry results: {sum([list(d.values())[0] for d in self.__saves.getentries(5)])}")

        action: str = input("\nEnter the action(num action num / action num / action): ").lower()
        actionsplit = action.split(' ')
        result = 0.0
        try:
            if len(actionsplit) == 3 and all(not part.isalpha() for part in (actionsplit[0], actionsplit[2])) and actionsplit[1] \
                in self.__actionsigns.keys():
                if actionsplit[2] == "0": raise ZeroDivisionError()
                result = self.__actionsigns[actionsplit[1]](float(actionsplit[0]), float(actionsplit[2]))
            elif len(actionsplit) == 2 and actionsplit[0] in self.__actionsigns.keys() and not actionsplit[1].isalpha():
                result = self.__actionsigns[actionsplit[0]](float(actionsplit[1]))     
            elif len(actionsplit) == 1:  
                if actionsplit[0] == 'stop':
                    print("\nStopping the program...\n")
                    exit()
                elif actionsplit[0].strip().lower() in ['clear', 'clearhistory']:
                    print("\nCleared calculator history")
                    self.__saves.clear()
                    input("Press Enter to continue...")
                    return
                else:
                    raise ValueError("\nInvalid input, enter the action in format (num action num / action num / action)!")
            else: raise ValueError("\nInvalid input, enter the action in format (num action num / action num / action)!")
        except (ValueError, KeyError) as e:
            print(str(e))
            input("Press Enter to continue...")
            return
        except ZeroDivisionError:
            print("\nMath Error: Division by 0")
            input("Press Enter to continue...")
            return
        
        self.__saves.saveaction(action, result)

        print(f"\nThe result is {result}")
        input("Press Enter to continue...")

        return None

class Main:
    configs = ConfigManager()
    saves = SaveManager(configs)
    calculator = CalculatorMethods(saves, configs)

    while True:
        system('cls' if name == 'nt' else 'clear')
        calculator.process()