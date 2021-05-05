# Python LMC
Version of the little man computer, in Python, that also supports a superset of instruction(s) (handlers) and interfacing with external components.

## Running
(This will improve later)

```bash
# To run a file on normal LMC
py -m lmc file_name.txt

# To run with a file handler where device 0 is the target_file
py -m lmc file_name.txt target_file.txt --write-files
```

## Examples
- `cat.txt` Uses file handler superset to cat to a given file
- `run-unicode.txt` Prints unicode characters from U0 onwards (also uses superset to write to given file)