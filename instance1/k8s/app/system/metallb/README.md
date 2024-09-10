kubectl get configmap kube-proxy -n kube-system -o yaml | \
 sed -e "s/strictARP: false/strictARP: true/" | \
 kubectl apply -f --n kube-system

명령어사용하여 strictARP를 true로 설정

## role 권한 문제로 실행안됨

- role.yml 권한 수정후 정



## crd가 없어서 안됨

- 


