from functools import wraps

def test(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        pass

    return wrapper

@test
def num1():
    pass

@test
def num2():
    pass

if __name__ == '__main__':
    print(num1.__name__)
    print(num2.__name__)