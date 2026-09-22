param(
    [Parameter(Mandatory = $true)][string]$AwsAccountId,
    [Parameter(Mandatory = $true)][string]$Region,
    [Parameter(Mandatory = $true)][string]$RepositoryName
)

$ImageUri = "$AwsAccountId.dkr.ecr.$Region.amazonaws.com/$RepositoryName`:latest"

aws ecr get-login-password --region $Region | docker login --username AWS --password-stdin "$AwsAccountId.dkr.ecr.$Region.amazonaws.com"
docker build -t $RepositoryName .
docker tag "$RepositoryName`:latest" $ImageUri
docker push $ImageUri

Write-Host "Pushed $ImageUri"
