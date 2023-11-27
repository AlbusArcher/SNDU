# SNDU
A simple namesilo's dns update dockerfile. The name, SNDU is frist letter of "Simple Namesilo's DNS Update"

# How to use
## Build docker image
Download the source code. Change into the folder where the source code is placed and execute the below command in the terminal

`docker build --no-cache -t dns_update:1.0 .`
## Create a container to update the DNS record
Execute the below command in the terminal to create a container and run the update

`docker run -d --name dns_update --env API_KEY="your namesilo API KEY" --env DOMAIN_NAME="your namesilo's domain name" --env HOST_NAME="domain hostname" dns_update:1.0`

### Environment args explanation
- API_KEY: Your namesilo's account API Key, ps: Don't apply or use a read-only key for this env variable
- DOMAIN_NAME: A namesilo's domain name you want to update
- HOST_NAME: Maybe you want a different hostname of a domain name that has a different IP address
- CHECK_INTERVAL: The interval second of the main script to check and update WAN IP, default is 300 seconds

