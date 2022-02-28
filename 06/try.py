def decimal_to_binary_str(num) -> str:
    temp_bin_str = bin(num)
    temp_bin_str = temp_bin_str[2:]
    n = 15 - len(temp_bin_str)
    return ('0' * n) + temp_bin_str

def main():
    print(decimal_to_binary_str(11))

main()