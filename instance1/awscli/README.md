# AWS CLI 사용 설명서

## 목차
1. [개요](#개요)
2. [AWS CLI가 필요한 이유](#aws-cli가-필요한-이유)
3. [설치 방법](#설치-방법)
   - [의존성 설치](#의존성-unzip-설치)
   - [AWS CLI 설치](#aws-cli-설치)

## 개요
AWS CLI(Amazon Web Services Command Line Interface)는 AWS 서비스와 상호작용할 수 있는 명령줄 도구입니다. 이 도구를 사용하면 AWS의 다양한 서비스(Amazon S3, EC2, RDS 등)를 손쉽게 관리하고 자동화할 수 있으며, 콘솔을 사용하는 대신 스크립트를 통해 일관되고 효율적인 워크플로우를 만들 수 있습니다.

## AWS CLI가 필요한 이유

1. **자동화된 작업 관리**:
   AWS CLI를 통해 AWS 서비스 작업을 명령어로 실행할 수 있으며, 이를 스크립트화하여 반복적이고 일상적인 작업을 자동화할 수 있습니다. 예를 들어, S3에 데이터를 업로드하거나 EC2 인스턴스를 생성하고 종료하는 등의 작업을 명령어로 쉽게 처리할 수 있습니다.

2. **멀티플랫폼 지원**:
   AWS CLI는 Linux, macOS, Windows에서 모두 사용할 수 있으며, 동일한 명령어 세트를 사용하여 다양한 플랫폼에서 일관된 작업 환경을 제공합니다.

3. **CI/CD 파이프라인 통합**:
   AWS CLI는 CI/CD 파이프라인에서 중요한 역할을 합니다. 배포 자동화 및 인프라 설정 작업을 AWS CLI를 통해 수행하여 개발과 배포 과정을 간소화할 수 있습니다. GitHub Actions, Jenkins, GitLab 등 다양한 CI/CD 도구와 통합하여 자동화를 쉽게 구현할 수 있습니다.

4. **운영 모니터링 및 관리**:
   AWS CLI를 통해 EC2, RDS, CloudWatch 등 다양한 AWS 리소스를 모니터링하고 관리할 수 있습니다. 예를 들어, EC2 인스턴스의 상태를 확인하거나 로그 데이터를 수집하는 작업을 명령줄에서 바로 처리할 수 있습니다.

5. **비용 최적화 및 리소스 관리**:
   AWS CLI를 사용하면 리소스 사용 현황을 간편하게 파악하고 불필요한 인스턴스나 서비스를 자동으로 종료하는 스크립트를 작성할 수 있어, 비용 절감과 리소스 최적화에 기여할 수 있습니다.


## 설치 방법

### 의존성 unzip 설치
sudo apt install unzip

### AWS CLI 설치

- 프로젝트 적용 버전
aws-cli/2.17.54 Python/3.12.6 Linux/6.8.0-1016-aws exe/x86_64.ubuntu.24

```
curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip"
unzip awscliv2.zip
sudo ./aws/install
aws --version

aws configure # 자격증명 
```
