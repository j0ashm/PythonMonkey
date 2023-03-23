import pytest
import pythonmonkey as pm
import gc
import random
from datetime import datetime, timedelta

def test_passes():
    assert True

def test_eval_ascii_string_matches_evaluated_string():
    py_ascii_string = "abc"
    js_ascii_string = pm.eval(repr(py_ascii_string))
    assert py_ascii_string == js_ascii_string

def test_eval_latin1_string_matches_evaluated_string():
    py_latin1_string = "a©Ð"
    js_latin1_string = pm.eval(repr(py_latin1_string))
    assert py_latin1_string == js_latin1_string

def test_eval_null_character_string_matches_evaluated_string():
    py_null_character_string = "a\x00©"
    js_null_character_string = pm.eval(repr(py_null_character_string))
    assert py_null_character_string == js_null_character_string

def test_eval_ucs2_string_matches_evaluated_string():
    py_ucs2_string = "ՄԸՋ"
    js_ucs2_string = pm.eval(repr(py_ucs2_string))
    assert py_ucs2_string == js_ucs2_string

def test_eval_unpaired_surrogate_string_matches_evaluated_string():
    py_unpaired_surrogate_string = "Ջ©\ud8fe"
    js_unpaired_surrogate_string = pm.eval(repr(py_unpaired_surrogate_string))
    assert py_unpaired_surrogate_string == js_unpaired_surrogate_string

def test_eval_ucs4_string_matches_evaluated_string():
    py_ucs4_string = "🀄🀛🜢"
    js_utf16_string = pm.eval(repr(py_ucs4_string))
    js_ucs4_string = pm.asUCS4(js_utf16_string)
    assert py_ucs4_string == js_ucs4_string

def test_eval_latin1_string_fuzztest():
    n = 10
    for i in range(n):
        length = random.randint(0x0000, 0xFFFF)
        string1 = ''

        for i in range(length):
            codepoint = random.randint(0x00, 0xFF)
            string1 += chr(codepoint) # add random chr in latin1 range
        
        
        INITIAL_STRING = string1
        m = 10
        for j in range(m):
            string2 = pm.eval(repr(string1))
            assert len(string1) == length
            assert len(string2) == length
            assert len(string1) == len(string2)
            assert string1 == string2

            gc.collect()
            pm.collect()
            
            #garbage collection should not collect variables still in scope
            assert len(string1) == length
            assert len(string2) == length
            assert len(string1) == len(string2)
            assert string1 == string2

            string1 = string2
        assert INITIAL_STRING == string1 #strings should still match after a bunch of iterations through JS

def test_eval_ucs2_string_fuzztest():
    n = 10
    for i in range(n):
        length = random.randint(0x0000, 0xFFFF)
        string1 = ''

        for i in range(length):
            codepoint = random.randint(0x00, 0xFFFF)
            string1 += chr(codepoint) # add random chr in ucs2 range
        
        
        INITIAL_STRING = string1
        m = 10
        for j in range(m):
            string2 = pm.eval(repr(string1))
            assert len(string1) == length
            assert len(string2) == length
            assert len(string1) == len(string2)
            assert string1 == string2

            gc.collect()
            pm.collect()
            
            #garbage collection should not collect variables still in scope
            assert len(string1) == length
            assert len(string2) == length
            assert len(string1) == len(string2)
            assert string1 == string2

            string1 = string2
        assert INITIAL_STRING == string1 #strings should still match after a bunch of iterations through JS

def test_eval_ucs4_string_fuzztest():
    n = 10
    for i in range(n):
        length = random.randint(0x0000, 0xFFFF)
        string1 = ''

        for i in range(length):
            codepoint = random.randint(0x010000, 0x10FFFF)
            string1 += chr(codepoint) # add random chr outside BMP
        
        
        INITIAL_STRING = string1
        m = 10
        for j in range(m):
            utf16_string2 = pm.eval("'" + string1 + "'")
            string2 = pm.asUCS4(utf16_string2)
            assert len(string1) == length
            assert len(string2) == length
            assert len(string1) == len(string2)
            assert string1 == string2

            gc.collect()
            pm.collect()
            
            #garbage collection should not collect variables still in scope
            assert len(string1) == length
            assert len(string2) == length
            assert len(string1) == len(string2)
            assert string1 == string2

            string1 = string2
        assert INITIAL_STRING == string1 #strings should still match after a bunch of iterations through JS

def test_eval_numbers_floats():
    for i in range(10):
        py_number = random.uniform(-1000000,1000000)
        js_number = pm.eval(repr(py_number))
        assert py_number == js_number

def test_eval_numbers_integers():
    for i in range(10):
        py_number = random.randint(-1000000,1000000)
        js_number = pm.eval(repr(py_number))
        assert py_number == js_number

def test_eval_numbers_bigints():
    def test_bigint(py_number: int):
        js_number = pm.eval(f'{repr(py_number)}n')
        assert py_number == js_number

    test_bigint(0)
    test_bigint(1)
    test_bigint(-1)

    # CPython would reuse the objects for small ints in range [-5, 256] 
    # Making sure we don't do any changes on them
    def test_cached_int_object(py_number):
        # type is still int
        assert type(py_number) == int
        assert type(py_number) != pm.bigint
        test_bigint(py_number)
        assert type(py_number) == int
        assert type(py_number) != pm.bigint
        # the value doesn't change
        # TODO: Find a way to create a NEW int object with the same value, because int literals also reuse the cached int objects
    for _ in range(2):
        test_cached_int_object(0) # _PyLong_FromByteArray reuses the int 0 object,
                                  # see https://github.com/python/cpython/blob/3.9/Objects/longobject.c#L862
        for i in range(10):
            test_cached_int_object(random.randint(-5, 256))

    test_bigint(18014398509481984)      #  2**54
    test_bigint(-18014398509481984)     # -2**54
    test_bigint(18446744073709551615)   #  2**64-1
    test_bigint(18446744073709551616)   #  2**64
    test_bigint(-18446744073709551617)  # -2**64-1

    limit = 2037035976334486086268445688409378161051468393665936250636140449354381299763336706183397376
    #     = 2**300
    for i in range(10):
        py_number = random.randint(-limit, limit)
        test_bigint(py_number)

    # TODO: test -0 (negative zero)
    # There's no -0 in both Python int and JS BigInt, 
    # but this could be possible in JS BigInt's internal representation as it uses a sign bit flag.
    # On the other hand, Python int uses `ob_size` 0 for 0, >0 for positive values, <0 for negative values

def test_eval_booleans():
    py_bool = True
    js_bool = pm.eval('true')
    assert py_bool == js_bool
    py_bool = False
    js_bool = pm.eval('false')
    assert py_bool == js_bool

def test_eval_dates():
    MIN_YEAR = 100
    MAX_YEAR = 2023
    start = datetime(MIN_YEAR, 1, 1, 00, 00, 00)
    years = MAX_YEAR - MIN_YEAR + 1
    end = start + timedelta(days=365 * years)
    for i in range(10):
        py_date = start + (end - start) * random.random()
        py_date = py_date.replace(microsecond=0)
        js_date = pm.eval(f'new Date({py_date.year}, {py_date.month - 1}, {py_date.day}, {py_date.hour}, {py_date.minute}, {py_date.second}, {py_date.microsecond / 1000})')
        assert py_date == js_date

def test_eval_boxed_booleans():
    py_bool = True
    js_bool = pm.eval('new Boolean(true)')
    assert py_bool == js_bool
    py_bool = False
    js_bool = pm.eval('new Boolean(false)')
    assert py_bool == js_bool

def test_eval_boxed_numbers_floats():
    for i in range(10):
        py_number = random.uniform(-1000000,1000000)
        js_number = pm.eval(f'new Number({repr(py_number)})')
        assert py_number == js_number

def test_eval_boxed_numbers_integers():
    for i in range(10):
        py_number = random.randint(-1000000,1000000)
        js_number = pm.eval(f'new Number({repr(py_number)})')
        assert py_number == js_number

def test_eval_boxed_numbers_bigints():
    def test_boxed_bigint(py_number: int):
        # `BigInt()` can only be called without `new`
        #   https://tc39.es/ecma262/#sec-bigint-constructor
        js_number = pm.eval(f'new Object({repr(py_number)}n)')
        assert py_number == js_number

    test_boxed_bigint(0)
    test_boxed_bigint(1)
    test_boxed_bigint(-1)

    limit = 2037035976334486086268445688409378161051468393665936250636140449354381299763336706183397376
    #     = 2**300
    for i in range(10):
        py_number = random.randint(-limit, limit)
        test_boxed_bigint(py_number)

def test_eval_boxed_ascii_string_matches_evaluated_string():
    py_ascii_string = "abc"
    js_ascii_string = pm.eval(f'new String({repr(py_ascii_string)})')
    assert py_ascii_string == js_ascii_string

def test_eval_boxed_latin1_string_matches_evaluated_string():
    py_latin1_string = "a©Ð"
    js_latin1_string = pm.eval(f'new String({repr(py_latin1_string)})')
    assert py_latin1_string == js_latin1_string

def test_eval_boxed_null_character_string_matches_evaluated_string():
    py_null_character_string = "a\x00©"
    js_null_character_string = pm.eval(f'new String({repr(py_null_character_string)})')
    assert py_null_character_string == js_null_character_string

def test_eval_boxed_ucs2_string_matches_evaluated_string():
    py_ucs2_string = "ՄԸՋ"
    js_ucs2_string = pm.eval(f'new String({repr(py_ucs2_string)})')
    assert py_ucs2_string == js_ucs2_string

def test_eval_boxed_unpaired_surrogate_string_matches_evaluated_string():
    py_unpaired_surrogate_string = "Ջ©\ud8fe"
    js_unpaired_surrogate_string = pm.eval(f'new String({repr(py_unpaired_surrogate_string)})')
    assert py_unpaired_surrogate_string == js_unpaired_surrogate_string

def test_eval_boxed_ucs4_string_matches_evaluated_string():
    py_ucs4_string = "🀄🀛🜢"
    js_utf16_string = pm.eval(f'new String({repr(py_ucs4_string)})')
    js_ucs4_string = pm.asUCS4(js_utf16_string)
    assert py_ucs4_string == js_ucs4_string

def test_eval_boxed_latin1_string_fuzztest():
    n = 10
    for i in range(n):
        length = random.randint(0x0000, 0xFFFF)
        string1 = ''

        for i in range(length):
            codepoint = random.randint(0x00, 0xFF)
            string1 += chr(codepoint) # add random chr in latin1 range
        
        
        INITIAL_STRING = string1
        m = 10
        for j in range(m):
            string2 = pm.eval(f'new String({repr(string1)})')
            assert len(string1) == length
            assert len(string2) == length
            assert len(string1) == len(string2)
            assert string1 == string2

            gc.collect()
            pm.collect()
            
            #garbage collection should not collect variables still in scope
            assert len(string1) == length
            assert len(string2) == length
            assert len(string1) == len(string2)
            assert string1 == string2

            string1 = string2
        assert INITIAL_STRING == string1 #strings should still match after a bunch of iterations through JS

def test_eval_boxed_ucs2_string_fuzztest():
    n = 10
    for i in range(n):
        length = random.randint(0x0000, 0xFFFF)
        string1 = ''

        for i in range(length):
            codepoint = random.randint(0x00, 0xFFFF)
            string1 += chr(codepoint) # add random chr in ucs2 range
        
        
        INITIAL_STRING = string1
        m = 10
        for j in range(m):
            string2 = pm.eval(f'new String({repr(string1)})')
            assert len(string1) == length
            assert len(string2) == length
            assert len(string1) == len(string2)
            assert string1 == string2

            gc.collect()
            pm.collect()
            
            #garbage collection should not collect variables still in scope
            assert len(string1) == length
            assert len(string2) == length
            assert len(string1) == len(string2)
            assert string1 == string2

            string1 = string2
        assert INITIAL_STRING == string1 #strings should still match after a bunch of iterations through JS

def test_eval_boxed_ucs4_string_fuzztest():
    n = 10
    for i in range(n):
        length = random.randint(0x0000, 0xFFFF)
        string1 = ''

        for i in range(length):
            codepoint = random.randint(0x010000, 0x10FFFF)
            string1 += chr(codepoint) # add random chr outside BMP
        
        
        INITIAL_STRING = string1
        m = 10
        for j in range(m):
            utf16_string2 = pm.eval(f'new String("{string1}")')
            string2 = pm.asUCS4(utf16_string2)
            assert len(string1) == length
            assert len(string2) == length
            assert len(string1) == len(string2)
            assert string1 == string2

            gc.collect()
            pm.collect()
            
            #garbage collection should not collect variables still in scope
            assert len(string1) == length
            assert len(string2) == length
            assert len(string1) == len(string2)
            assert string1 == string2

            string1 = string2
        assert INITIAL_STRING == string1 #strings should still match after a bunch of iterations through JS
        
def test_eval_undefined():
    x = pm.eval("undefined")
    assert x == None

def test_eval_null():
    x = pm.eval("null")
    assert x == pm.null
    
def test_eval_functions():
    f = pm.eval("() => { return undefined }")
    assert f() == None

    g = pm.eval("() => { return null}")
    assert g() == pm.null

    h = pm.eval("(a, b) => {return a + b}")
    n = 10
    for i in range(n):
        a = random.randint(0, 1000)
        b = random.randint(0, 1000)
        assert h(a, b) == (a + b)
    
    for i in range (n):
        a = random.uniform(-1000.0, 1000.0)
        b = random.uniform(-1000.0, 1000.0)
        assert h(a, b) == (a + b)

def test_eval_functions_latin1_string_args():
    concatenate = pm.eval("(a, b) => { return a + b}")
    n = 10
    for i in range(n):
        length1 = random.randint(0x0000, 0xFFFF)
        length2 = random.randint(0x0000, 0xFFFF)
        string1 = ''
        string2 = ''

        for j in range(length1):
            codepoint = random.randint(0x00, 0xFFFF)
            string1 += chr(codepoint) # add random chr in ucs2 range
        for j in range(length2):
            codepoint = random.randint(0x00, 0xFFFF)
            string2 += chr(codepoint)
        
        assert concatenate(string1, string2) == (string1 + string2)

def test_eval_functions_bigints():
    ident = pm.eval("(a) => { return a }")
    add = pm.eval("(a, b) => { return a + b }")

    int1 = random.randint(-1000000,1000000)
    bigint1 = pm.bigint(int1)
    assert int1 == bigint1

    # should return pm.bigint
    assert type(ident(bigint1)) == pm.bigint
    assert ident(bigint1) is not bigint1
    # should return float (because JS number is float64)
    assert type(ident(int1)) == float
    assert ident(int1) == ident(bigint1)

    # should raise exception on ints > (2^53-1), or < -(2^53-1)
    def not_raise(num):
        ident(num)
    def should_raise(num):
        with pytest.raises(OverflowError, match="Use pythonmonkey.bigint instead"):
            ident(num)
    not_raise(9007199254740991)     #   2**53-1, 0x433_FFFFFFFFFFFFF in float64
    should_raise(9007199254740992)  #   2**53,   0x434_0000000000000 in float64
    should_raise(9007199254740993)  #   2**53+1, NOT 0x434_0000000000001 (2**53+2)
    # ident(9007199254740994)  # FIXME: Should raise exception on 2**53+2 and other large integers that can be exactly represented by a float64?
    not_raise(-9007199254740991)    # -(2**53-1)
    should_raise(-9007199254740992) # -(2**53)
    should_raise(-9007199254740993) # -(2**53+1)

    # Should raise "Use pythonmonkey.bigint" instead of `PyLong_AsLongLong`'s "OverflowError: int too big to convert" on ints larger than 64bits
    should_raise(2**65)
    should_raise(-2**65)
    not_raise(pm.bigint(2**65))
    not_raise(pm.bigint(-2**65))

def test_eval_functions_ucs2_string_args():
    concatenate = pm.eval("(a, b) => { return a + b}")
    n = 10
    for i in range(n):
        length1 = random.randint(0x0000, 0xFFFF)
        length2 = random.randint(0x0000, 0xFFFF)
        string1 = ''
        string2 = ''

        for j in range(length1):
            codepoint = random.randint(0x00, 0xFF)
            string1 += chr(codepoint) # add random chr in latin1 range
        for j in range(length2):
            codepoint = random.randint(0x00, 0xFF)
            string2 += chr(codepoint)
        
        assert concatenate(string1, string2) == (string1 + string2)

def test_eval_functions_ucs4_string_args():
    concatenate = pm.eval("(a, b) => { return a + b}")
    n = 10
    for i in range(n):
        length1 = random.randint(0x0000, 0xFFFF)
        length2 = random.randint(0x0000, 0xFFFF)
        string1 = ''
        string2 = ''

        for j in range(length1):
            codepoint = random.randint(0x010000, 0x10FFFF)
            string1 += chr(codepoint) # add random chr outside BMP
        for j in range(length2):
            codepoint = random.randint(0x010000, 0x10FFFF)
            string2 += chr(codepoint)
        
        assert pm.asUCS4(concatenate(string1, string2)) == (string1 + string2)

def test_eval_functions_pyfunctions_ints():
    caller = pm.eval("(func, param1, param2) => { return func(param1, param2) }")
    def add(a, b):
        return a + b
    n = 10
    for i in range(n):
        int1 = random.randint(0x0000, 0xFFFF)
        int2 = random.randint(0x0000, 0xFFFF)
        assert caller(add, int1, int2) == int1 + int2

def test_eval_functions_pyfunctions_strs():
    caller = pm.eval("(func, param1, param2) => { return func(param1, param2) }")
    def concatenate(a, b):
        return a + b
    n = 10
    for i in range(n):
        length1 = random.randint(0x0000, 0xFFFF)
        length2 = random.randint(0x0000, 0xFFFF)
        string1 = ''
        string2 = ''

        for j in range(length1):
            codepoint = random.randint(0x0000, 0xFFFF)
            string1 += chr(codepoint) # add random chr
        for j in range(length2):
            codepoint = random.randint(0x0000, 0xFFFF)
            string2 += chr(codepoint)
        assert caller(concatenate, string1, string2) == string1 + string2