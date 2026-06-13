import os

def show_tree(start_path, indent=""):
    for item in os.listdir(start_path):
        path = os.path.join(start_path, item)
        print(indent + "|-- " + item)
        if os.path.isdir(path):
            show_tree(path, indent + "   ")

show_tree("app")  # starting folder
