# kubec2metadata
Provides mock EC2 metadata to Kubernetes pods for local development.

# RUN
kubectl delete deployments kubec2metadata
kubectl run kubec2metadata --image kubec2metadata_kubec2metadata --image-pull-policy IfNotPresent
