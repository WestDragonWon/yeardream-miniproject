kubectl get configmap kube-proxy -n kube
system -o yaml | \
 sed -e "s/strictARP: false/strictARP: true/" | \
 kubectl apply -f --n kube-system

명령어사용하여 strictARP를 true로 설정
