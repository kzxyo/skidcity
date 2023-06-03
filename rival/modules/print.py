from time import sleep

def progress(percent=0, width=30):
    # The number of hashes to show is based on the percent passed in. The
    # number of blanks is whatever space is left after.
    hashes = width * percent // 100
    blanks = width - hashes

    print('\r[', hashes*'#', blanks*' ', ']', f' {percent:.0f}%', sep='',
        end='', flush=True)

print('This will take a moment')
for i in range(101):
    progress(i)
    sleep(0.1)

# Newline so command prompt isn't on the same line
print()