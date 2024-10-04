#!/bin/sh
DASHBOARD_PORT_FORWARDING="8443:443"
DASHBOARD_PROXY="kubectl proxy"

if ! pgrep -f "$DASHBOARD_PORT_FORWARDING" > /dev/null; then
    echo "Starting port-forwarding for dashboard"
    nohup kubectl port-forward -n system service/dashboard-kong-proxy 8443:443 --address 0.0.0.0 > /home/ubuntu/yeardream-miniproject/instance1/k8s/system/dashboard/port-forward.log 2>&1 & \
    PORT_FORWARD_PID=$!

    sleep 5
fi

#if ! pgrep -f "$DASHBOARD_PROXY" > /dev/null; then
#    echo "Starting proxy"
#    nohup kubectl proxy > /home/ubuntu/yeardream-miniproject/instance1/k8s/app/system/dashboard/proxy.log 2>&1 & PROXY_PID=$!
#fi

#echo "Applying admin user"

#kubectl apply -f /home/ubuntu/yeardream-miniproject/instance1/k8s/app/system/dashboard/dashboard-adminuser.yaml

if ! kubectl get secret $SECRET_NAME -n $NAMESPACE > /dev/null 2>&1; then
    kubectl apply -f /home/ubuntu/yeardream-miniproject/instance1/k8s/system/dashboard/secret.yaml
    echo "Creating token for admin user"
    TOKEN=$(kubectl get secret admin-user -n system -o jsonpath={".data.token"} | base64 -d)
fi

echo "PORTFORWARD PID: $PORT_FORWARD_PID"
echo "PROXY_PID: $PROXY_PID"
echo "token:"
echo "$TOKEN">/home/ubuntu/yeardream-miniproject/instance1/k8s/system/dashboard/.env
cat /home/ubuntu/yeardream-miniproject/instance1/k8s/system/dashboard/.env
