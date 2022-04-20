# CloudComputingA3

Assignment 3 for ECE 1779

Projet uses: Lambda, DynamoDb, EC2, RDS, S3, EventBridge

### Group Contributions
![group_contributions](https://github.com/Josh-Abraham/CloudComputingA3/blob/main/contrib.JPG?raw=true)

ML Model designed by Vishal

### System Description 
The purpose of this application is to allow users to submit images, and have them classified as either a cat or a dog. They can then show all images by classification, search for a specific image by the submitted key, or list all stored images details.

The manager application allows the system administrator the ability to view and search images. Additionally, the admin can label images submitted by users, which can then be used to trigger a round of additional model training to update the classification model being used.

### System Architecture
![system architecture](https://github.com/Josh-Abraham/CloudComputingA3/blob/main/design.png?raw=true)

This system can be broken down by the various AWS components used, and their interactions are described in the above diagram. 

#### Lambda Functions
  User Application: The main hosted application accessible via an API gateway

  Manager Application: The manager hosted app, that is accessible via the api gateway, connected to AWS Cognito  
  Background Application: Standalone process that is triggered from EventBridge

#### DynamoDB
  Image Store: The storage location for data about images submitted by users, including their S3 key
  Manager Mode: Maintains the current mode of training set by the manager

#### S3
  Image: Stores all the images submitted by users, with keys stored in Image Store DynamoDB
  Model: Stores the current model used for classification, and the metrics
  Static: Stores static content used within the UI, such as icons and CSS files

#### EC2
  Run: The EC2 instance that runs classifications for users, and pulls images and the model from S3 Image and Model respectively
  Train: The EC2 instance that only is in use when the system is training a new model, either triggered by the manager or automatically. The new model is store in S3 Model

#### Cognito
  ManagerLogin: The User Pool that contains the login credentials and requirements to access the manager Lambda function

#### CloudWatch
  A3Logs: The CloudWatch Log session that tracks logs within the background Lambda process, and the EC2 instances

#### EventBridge
  Autorun-A3: The rule that defines triggering the background process check every 3 minutes

#### API Gateway
  Used for both public facing Lambda functions
