#!/bin/bash

kubectl delete pod -n $NAMESPACE --field-selector=status.phase==Succeeded
kubectl delete pod -n $NAMESPACE --field-selector=status.phase==Failed



