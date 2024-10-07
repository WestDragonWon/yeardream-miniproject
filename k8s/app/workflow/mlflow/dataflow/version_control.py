from datetime import datetime
import os

def generate_model_version():
    # Step 1: Head Version
    head_version = 1  # 수동으로 수정 가능

    # Step 2: Year and Week Number (ISO)
    current_date = datetime.now()
    yearweek = current_date.strftime("%y%U")

    # Step 3: Build Version
    build_file = "/home/ubuntu/mlops/models/iris/.build_version.txt"
    if os.path.exists(build_file):
        with open(build_file, "r") as f:
            last_version = f.read().strip()
            last_build_version = int(last_version.split(".b")[1])
            build_version = last_build_version + 1
    else:
        build_version = 1

    version = f"{head_version}.{yearweek}.b{build_version}"

    # Save the build version
    with open(build_file, "w") as f:
        f.write(str(version))

    return version
