"""
Code2Flow - Multi-Language Demonstration Sample Programs
Curated educational sample programs covering Python, JavaScript, Java, and C++.
"""

from typing import Dict, Any

SAMPLES: Dict[str, Dict[str, Any]] = {
    # ==================== PYTHON SAMPLES ====================
    "python": {
        "flowchart": {
            "if_else": {
                "title": "Branching: Pass/Fail Grading",
                "category": "Conditional",
                "code": """score = int(input("Enter student score: "))

if score >= 90:
    grade = "A"
    print("Excellent work!")
elif score >= 75:
    grade = "B"
    print("Good job!")
elif score >= 50:
    grade = "C"
    print("You passed.")
else:
    grade = "F"
    print("Needs improvement.")

print("Final Grade:", grade)
"""
            },
            "loops_nested": {
                "title": "Loops: Prime Number Finder with Break",
                "category": "Loops",
                "code": """limit = 20
print("Finding primes up to", limit)

for num in range(2, limit + 1):
    is_prime = True
    for i in range(2, int(num ** 0.5) + 1):
        if num % i == 0:
            is_prime = False
            break
    if is_prime:
        print(num, "is prime")
    else:
        continue

print("Search complete.")
"""
            },
            "try_except": {
                "title": "Exception Handling: Safe Integer Division",
                "category": "Exceptions",
                "code": """def safe_divide():
    try:
        a = int(input("Enter numerator: "))
        b = int(input("Enter denominator: "))
        result = a / b
    except ZeroDivisionError as err:
        print("Cannot divide by zero!")
        result = None
    else:
        print("Division successful.")
    finally:
        print("Execution finished.")
    return result

res = safe_divide()
print("Result:", res)
"""
            }
        },
        "oop": {
            "composition_car": {
                "title": "Composition & Aggregation: Car & Engine",
                "code": """class Engine:
    def __init__(self, horsepower: int):
        self.horsepower = horsepower

    def start(self):
        print("Engine started!")

class Car:
    def __init__(self, model: str, horsepower: int):
        self.model = model
        self.engine = Engine(horsepower)

    def drive(self):
        self.engine.start()
        print(f"{self.model} driving.")

my_car = Car("Sedan", 180)
my_car.drive()
"""
            },
            "inheritance_shapes": {
                "title": "Polymorphism: Shape & Circle",
                "code": """class Shape:
    def __init__(self, name: str):
        self.name = name
    def area(self):
        return 0.0

class Circle(Shape):
    def __init__(self, radius: float):
        super().__init__("Circle")
        self.radius = radius

    def area(self):
        return 3.14159 * (self.radius ** 2)

c = Circle(5.0)
print("Area:", c.area())
"""
            }
        },
        "traceback": {
            "zero_division": {
                "title": "ZeroDivisionError in Calculator",
                "code": """def calculate_average(total_score, count):
    print("Calculating average...")
    avg = total_score / count
    return avg

scores = 450
students = 0
result = calculate_average(scores, students)
print("Average score is:", result)
""",
                "traceback": """Traceback (most recent call last):
  File "<code2flow>", line 8, in <module>
    result = calculate_average(scores, students)
  File "<code2flow>", line 3, in calculate_average
    avg = total_score / count
ZeroDivisionError: division by zero
"""
            }
        }
    },

    # ==================== JAVASCRIPT SAMPLES ====================
    "javascript": {
        "flowchart": {
            "if_else": {
                "title": "JS: Grade Calculation",
                "code": """const score = 85;

if (score >= 90) {
    console.log("Grade A");
} else if (score >= 75) {
    console.log("Grade B");
} else {
    console.log("Grade C");
}

console.log("Evaluation complete.");
"""
            },
            "loops_nested": {
                "title": "JS: Loop with Break & Continue",
                "code": """for (let i = 1; i <= 10; i++) {
    if (i % 2 === 0) {
        continue;
    }
    if (i > 7) {
        break;
    }
    console.log("Odd number:", i);
}
console.log("Finished loop.");
"""
            }
        },
        "oop": {
            "composition_car": {
                "title": "JS: Car & Engine Composition",
                "code": """class Engine {
    constructor(horsepower) {
        this.horsepower = horsepower;
    }
    start() {
        console.log("Engine running.");
    }
}

class Car {
    constructor(brand, horsepower) {
        this.brand = brand;
        this.engine = new Engine(horsepower);
    }
    drive() {
        this.engine.start();
        console.log(this.brand + " moving.");
    }
}

const car = new Car("Toyota", 150);
car.drive();
"""
            }
        },
        "traceback": {
            "type_error": {
                "title": "JS: TypeError Undefined Property",
                "code": """function getUserData(user) {
    console.log("Fetching profile...");
    const email = user.profile.email;
    return email;
}

const currentUser = null;
getUserData(currentUser);
""",
                "traceback": """TypeError: Cannot read properties of null (reading 'profile')
    at getUserData (app.js:3:24)
    at app.js:7:1
"""
            }
        }
    },

    # ==================== JAVA SAMPLES ====================
    "java": {
        "flowchart": {
            "if_else": {
                "title": "Java: Number Evaluation",
                "code": """int score = 88;

if (score >= 90) {
    System.out.println("Distinction");
} else if (score >= 50) {
    System.out.println("Pass");
} else {
    System.out.println("Fail");
}

System.out.println("Done.");
"""
            },
            "while_loop": {
                "title": "Java: While Loop with Counter",
                "code": """int counter = 0;
while (counter < 5) {
    System.out.println("Count: " + counter);
    counter++;
}
System.out.println("Loop terminated.");
"""
            }
        },
        "oop": {
            "inheritance_shapes": {
                "title": "Java: Inheritance & Composition",
                "code": """class Engine {
    int horsepower;
    public Engine(int hp) {
        this.horsepower = hp;
    }
}

class Vehicle {
    String brand;
    public void move() {
        System.out.println("Moving");
    }
}

class Car extends Vehicle {
    Engine engine;
    public Car(String brand, int hp) {
        this.brand = brand;
        this.engine = new Engine(hp);
    }
}
"""
            }
        },
        "traceback": {
            "null_pointer": {
                "title": "Java: NullPointerException",
                "code": """public class Main {
    public static void printLength(String text) {
        System.out.println("Text length: " + text.length());
    }

    public static void main(String[] args) {
        String msg = null;
        printLength(msg);
    }
}
""",
                "traceback": """Exception in thread "main" java.lang.NullPointerException: Cannot invoke "String.length()" because "text" is null
    at Main.printLength(Main.java:3)
    at Main.main(Main.java:8)
"""
            }
        }
    },

    # ==================== C / C++ SAMPLES ====================
    "cpp": {
        "flowchart": {
            "if_else": {
                "title": "C++: Branching with cout",
                "code": """int temp = 32;

if (temp > 30) {
    cout << "Hot weather" << endl;
} else if (temp > 15) {
    cout << "Moderate weather" << endl;
} else {
    cout << "Cold weather" << endl;
}

cout << "Forecast done." << endl;
"""
            },
            "for_loop": {
                "title": "C++: For Loop Prime Check",
                "code": """int n = 7;
bool isPrime = true;

for (int i = 2; i * i <= n; i++) {
    if (n % i == 0) {
        isPrime = false;
        break;
    }
}

cout << "Check complete" << endl;
"""
            }
        },
        "oop": {
            "inheritance_car": {
                "title": "C++: Inheritance & Composition",
                "code": """class Engine {
public:
    int hp;
    Engine(int h) : hp(h) {}
};

class Vehicle {
public:
    void drive();
};

class Car : public Vehicle {
public:
    Engine* engine;
    Car(int hp) {
        this->engine = new Engine(hp);
    }
};
"""
            }
        },
        "traceback": {
            "compiler_error": {
                "title": "C++: Array Out of Bounds / Compiler Error",
                "code": """int main() {
    int arr[3] = {1, 2, 3};
    int bad_val = arr[10];
    cout << bad_val << endl;
    return 0;
}
""",
                "traceback": """main.cpp:3:19: warning: array index 10 is past the end of the array (which contains 3 elements)
main.cpp:4:5: error: 'cout' was not declared in this scope; did you mean 'std::cout'?
"""
            }
        }
    }
}
