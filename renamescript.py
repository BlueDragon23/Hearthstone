import os


for file in os.listdir('./cards'):
    tokens = file.split("-")
    if tokens[0].isdigit():
        try:
            os.rename(file, "-".join(tokens[1:]))
        except Exception as e:
            print(e)
