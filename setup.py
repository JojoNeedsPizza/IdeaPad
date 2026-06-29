import os
import shutil
import winreg as reg


def setup_and_move():
    # 1. Dynamically find the path to the current user's Documents folder
    user_profile = os.environ.get("USERPROFILE")
    target_dir = os.path.join(user_profile, "Documents", "IdeaPad")

    target_file_name = "main.py"
    destination_path = os.path.join(target_dir, target_file_name)

    # 2. Find where main.py is right now (next to this setup script)
    current_dir = os.path.dirname(os.path.abspath(__file__))
    source_path = os.path.join(current_dir, target_file_name)

    # Check if the main file actually exists before proceeding
    if not os.path.exists(source_path):
        print(f"Error: Could not find '{target_file_name}' in this folder.")
        input("\nPress Enter to close...")
        return

    try:
        # 3. Create the Documents\IdeaPad folder if it doesn't exist
        if not os.path.exists(target_dir):
            os.makedirs(target_dir)
            print(f"Created folder: {target_dir}")

        # 4. Copy the file to the new Documents folder
        shutil.copy(source_path, destination_path)
        print(f"Successfully copied program to: {destination_path}")

        # 5. Register the NEW Documents path in the Windows Registry for autostart
        key_path = r"Software\Microsoft\Windows\CurrentVersion\Run"
        app_name = "IdeaPadDocumentsApp"

        key = reg.OpenKey(reg.HKEY_CURRENT_USER, key_path, 0, reg.KEY_ALL_ACCESS)
        reg.SetValueEx(key, app_name, 0, reg.REG_SZ, f'"{destination_path}"')
        reg.CloseKey(key)

        print("\nSuccess! Everything is set up safely.")
        print("Your program will now start from your Documents folder upon boot.")

    except Exception as e:
        print(f"\nAn error occurred: {e}")

    input("\nPress Enter to close...")


if __name__ == "__main__":
    setup_and_move()