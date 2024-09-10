from importlib.metadata import distributions
import sys

sys.path.append('/home/ubuntu/.pyenv/shims/python3')

# 현재 설치된 패키지 목록을 가져옵니다.
installed_packages = {dist.metadata['Name']: dist.version for dist in distributions()}

# requirements.txt 파일 경로를 설정합니다.
requirements_file = '/home/ubuntu/yeardream-miniproject/instance1/requirements.txt'

try:
    # 설치된 패키지를 requirements.txt에 덮어씁니다.
    with open(requirements_file, 'w') as f:
        for package, version in installed_packages.items():
            f.write(f"{package}=={version}\n")
    print(f"{requirements_file}가 성공적으로 업데이트되었습니다.")
except Exception as e:
    print(f"오류 발생: {e}")
