eksctl create iamserviceaccount \
  --name streamlit-app-sa \
  --namespace default \
  --cluster sas-6881323-eks \
  --attach-policy-arn arn:aws:iam::248189947068:policy/dataiesb-s3-read \
  --approve \
  --override-existing-serviceaccounts
