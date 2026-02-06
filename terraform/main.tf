terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}

provider "aws" {
  region     = var.aws_region
  access_key = var.AWS_ACCESS_KEY
  secret_key = var.AWS_SECRET_KEY
}

resource "aws_s3_bucket" "data_lake" {
  bucket        = var.bucket_name
  force_destroy = true
}

output "bucket_name" {
  value = aws_s3_bucket.data_lake.id
}

resource "aws_iam_role" "glue_crawler_role" {
  name = "c21-nathan-t3-glue-crawler-role"
  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Action    = "sts:AssumeRole"
      Effect    = "Allow"
      Principal = { Service = "glue.amazonaws.com" }
    }]
  })
}

resource "aws_iam_role_policy_attachment" "glue_service_policy" {
  role       = aws_iam_role.glue_crawler_role.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AWSGlueServiceRole"
}

resource "aws_iam_role_policy" "glue_s3_policy" {
  role = aws_iam_role.glue_crawler_role.id
  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect   = "Allow"
        Action   = ["s3:GetObject", "s3:PutObject", "s3:DeleteObject"]
        Resource = ["${aws_s3_bucket.data_lake.arn}/*"]
      },
      {
        Effect   = "Allow"
        Action   = ["s3:ListBucket"]
        Resource = [aws_s3_bucket.data_lake.arn]
      }
    ]
  })
}

resource "aws_glue_catalog_database" "t3_data_lake_db" {
  name = "c21_nathan_t3_food_trucks_db"
}

resource "aws_glue_crawler" "transactions_crawler" {
  name          = "c21-nathan-t3-transactions-crawler"
  role          = aws_iam_role.glue_crawler_role.arn
  database_name = aws_glue_catalog_database.t3_data_lake_db.name

  s3_target {
    path = "s3://${aws_s3_bucket.data_lake.id}/inputs/transactions/"
  }
}

resource "aws_glue_crawler" "dimensions_crawler" {
  name          = "c21-nathan-t3-dimensions-crawler"
  role          = aws_iam_role.glue_crawler_role.arn
  database_name = aws_glue_catalog_database.t3_data_lake_db.name

  s3_target {
    path = "s3://${aws_s3_bucket.data_lake.id}/inputs/dimensions/"
  }
}

output "glue_database_name" {
  value = aws_glue_catalog_database.t3_data_lake_db.name
}

output "glue_crawler_transactions" {
  value = aws_glue_crawler.transactions_crawler.name
}

output "glue_crawler_dimensions" {
  value = aws_glue_crawler.dimensions_crawler.name
}

resource "aws_ecr_repository" "dashboard" {
  name                 = "c21-nathan-t3-dashboard-ecr"
  image_tag_mutability = "MUTABLE"
  force_delete         = true

  image_scanning_configuration {
    scan_on_push = true
  }
}

output "dashboard_ecr_url" {
  value       = aws_ecr_repository.dashboard.repository_url
  description = "Dashboard ECR repository URL"
}

resource "aws_ecr_repository" "report_lambda" {
  name                 = "c21-nathan-t3-report-lambda-ecr"
  image_tag_mutability = "MUTABLE"
  force_delete         = true

  image_scanning_configuration {
    scan_on_push = true
  }
}

output "report_lambda_ecr_url" {
  value       = aws_ecr_repository.report_lambda.repository_url
  description = "Report Lambda ECR repository URL"
}

data "aws_ecs_cluster" "existing_cluster" {
  cluster_name = "c21-ecs-cluster"
}

resource "aws_cloudwatch_log_group" "etl_logs" {
  name              = "/ecs/c21-nathan-t3-etl-pipeline"
  retention_in_days = 7
}

resource "aws_cloudwatch_log_group" "dashboard_logs" {
  name              = "/ecs/c21-nathan-t3-dashboard"
  retention_in_days = 7
}

resource "aws_iam_role" "ecs_task_execution_role" {
  name = "c21-nathan-t3-ecs-task-execution-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Action = "sts:AssumeRole"
      Effect = "Allow"
      Principal = {
        Service = "ecs-tasks.amazonaws.com"
      }
    }]
  })
}

resource "aws_iam_role_policy_attachment" "ecs_task_execution_policy" {
  role       = aws_iam_role.ecs_task_execution_role.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AmazonECSTaskExecutionRolePolicy"
}

resource "aws_iam_role" "ecs_task_role" {
  name = "c21-nathan-t3-ecs-task-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Action = "sts:AssumeRole"
      Effect = "Allow"
      Principal = {
        Service = "ecs-tasks.amazonaws.com"
      }
    }]
  })
}

resource "aws_iam_role_policy" "ecs_task_s3_policy" {
  name = "c21-nathan-t3-ecs-s3-policy"
  role = aws_iam_role.ecs_task_role.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "s3:GetObject",
          "s3:PutObject",
          "s3:DeleteObject",
          "s3:ListBucket"
        ]
        Resource = [
          "${aws_s3_bucket.data_lake.arn}",
          "${aws_s3_bucket.data_lake.arn}/*"
        ]
      }
    ]
  })
}

resource "aws_iam_role_policy" "ecs_task_glue_athena_policy" {
  name = "c21-nathan-t3-ecs-glue-athena-policy"
  role = aws_iam_role.ecs_task_role.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "glue:GetDatabase",
          "glue:GetTable",
          "glue:GetPartitions",
          "athena:StartQueryExecution",
          "athena:GetQueryExecution",
          "athena:GetQueryResults"
        ]
        Resource = "*"
      }
    ]
  })
}

resource "aws_ecs_task_definition" "etl_pipeline" {
  family                   = "c21-nathan-t3-etl-pipeline"
  requires_compatibilities = ["FARGATE"]
  network_mode             = "awsvpc"
  cpu                      = "512"
  memory                   = "1024"
  execution_role_arn       = aws_iam_role.ecs_task_execution_role.arn
  task_role_arn            = aws_iam_role.ecs_task_role.arn

  container_definitions = jsonencode([
    {
      name  = "etl-container"
      image = "${var.ecr_repository_url}:latest"

      environment = [
        {
          name  = "DB_HOST"
          value = var.db_host
        },
        {
          name  = "DB_PORT"
          value = var.db_port
        },
        {
          name  = "DB_USER"
          value = var.db_user
        },
        {
          name  = "DB_PASSWORD"
          value = var.db_password
        },
        {
          name  = "DB_NAME"
          value = var.db_name
        },
        {
          name  = "S3_BUCKET_NAME"
          value = aws_s3_bucket.data_lake.id
        },
        {
          name  = "AWS_DEFAULT_REGION"
          value = var.aws_region
        }
      ]

      logConfiguration = {
        logDriver = "awslogs"
        options = {
          "awslogs-group"         = aws_cloudwatch_log_group.etl_logs.name
          "awslogs-region"        = var.aws_region
          "awslogs-stream-prefix" = "ecs"
        }
      }

      essential = true
    }
  ])
}

resource "aws_ecs_task_definition" "dashboard" {
  family                   = "c21-nathan-t3-dashboard"
  requires_compatibilities = ["FARGATE"]
  network_mode             = "awsvpc"
  cpu                      = "256"
  memory                   = "512"
  execution_role_arn       = aws_iam_role.ecs_task_execution_role.arn
  task_role_arn            = aws_iam_role.ecs_task_role.arn

  container_definitions = jsonencode([
    {
      name  = "dashboard-container"
      image = "${aws_ecr_repository.dashboard.repository_url}:latest"

      portMappings = [
        {
          containerPort = 8501
          protocol      = "tcp"
        }
      ]

      environment = [
        {
          name  = "AWS_DEFAULT_REGION"
          value = var.aws_region
        }
      ]

      logConfiguration = {
        logDriver = "awslogs"
        options = {
          "awslogs-group"         = aws_cloudwatch_log_group.dashboard_logs.name
          "awslogs-region"        = var.aws_region
          "awslogs-stream-prefix" = "ecs"
        }
      }

      essential = true
    }
  ])
}

resource "aws_ecs_service" "dashboard" {
  name            = "c21-nathan-t3-dashboard-service"
  cluster         = data.aws_ecs_cluster.existing_cluster.id
  task_definition = aws_ecs_task_definition.dashboard.arn
  launch_type     = "FARGATE"
  desired_count   = 1

  network_configuration {
    subnets          = data.aws_subnets.default.ids
    assign_public_ip = true
  }
}

resource "aws_iam_role" "eventbridge_scheduler_role" {
  name = "c21-nathan-t3-eventbridge-scheduler-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Action = "sts:AssumeRole"
      Effect = "Allow"
      Principal = {
        Service = "scheduler.amazonaws.com"
      }
    }]
  })
}

resource "aws_iam_role_policy" "eventbridge_scheduler_policy" {
  name = "c21-nathan-t3-eventbridge-scheduler-policy"
  role = aws_iam_role.eventbridge_scheduler_role.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "ecs:RunTask"
        ]
        Resource = [
          aws_ecs_task_definition.etl_pipeline.arn
        ]
      },
      {
        Effect = "Allow"
        Action = [
          "iam:PassRole"
        ]
        Resource = [
          aws_iam_role.ecs_task_execution_role.arn,
          aws_iam_role.ecs_task_role.arn
        ]
      }
    ]
  })
}

data "aws_vpc" "default" {
  default = true
}

data "aws_subnets" "default" {
  filter {
    name   = "vpc-id"
    values = [data.aws_vpc.default.id]
  }
}

resource "aws_scheduler_schedule" "etl_schedule" {
  name       = "c21-nathan-trucks-schedule"
  group_name = "default"

  flexible_time_window {
    mode = "OFF"
  }

  schedule_expression = var.schedule_expression

  target {
    arn      = data.aws_ecs_cluster.existing_cluster.arn
    role_arn = aws_iam_role.eventbridge_scheduler_role.arn

    ecs_parameters {
      task_definition_arn = aws_ecs_task_definition.etl_pipeline.arn
      launch_type         = "FARGATE"
      task_count          = 1

      network_configuration {
        subnets          = data.aws_subnets.default.ids
        assign_public_ip = true
      }
    }
  }
}

resource "aws_iam_role" "lambda_report" {
  name = "c21-nathan-t3-lambda-report-role"
  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Action    = "sts:AssumeRole"
      Effect    = "Allow"
      Principal = { Service = "lambda.amazonaws.com" }
    }]
  })
}

resource "aws_iam_role_policy_attachment" "lambda_basic" {
  role       = aws_iam_role.lambda_report.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole"
}

resource "aws_iam_role_policy" "lambda_report" {
  role = aws_iam_role.lambda_report.id
  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "s3:GetObject",
          "s3:PutObject",
          "s3:ListBucket",
          "s3:GetBucketLocation",
          "s3:GetBucketVersioning"
        ]
        Resource = [
          "${aws_s3_bucket.data_lake.arn}",
          "${aws_s3_bucket.data_lake.arn}/*"
        ]
      },
      {
        Effect = "Allow"
        Action = [
          "athena:StartQueryExecution",
          "athena:GetQueryExecution",
          "athena:GetQueryResults",
          "athena:GetWorkGroup",
          "glue:GetTable",
          "glue:GetDatabase",
          "glue:GetPartitions"
        ]
        Resource = "*"
      }
    ]
  })
}

resource "aws_lambda_function" "report_generator" {
  function_name = "c21-nathan-t3-daily-report"
  role          = aws_iam_role.lambda_report.arn
  package_type  = "Image"
  image_uri     = "${aws_ecr_repository.report_lambda.repository_url}:latest"
  timeout       = 300
  memory_size   = 512

  environment {
    variables = {
      S3_BUCKET_NAME  = aws_s3_bucket.data_lake.id
      ATHENA_DATABASE = aws_glue_catalog_database.t3_data_lake_db.name
    }
  }
}

resource "aws_cloudwatch_event_rule" "lambda_daily" {
  name                = "c21-nathan-daily-report-trigger"
  description         = "Triggers Step Functions to generate and email daily report at 9:30 AM UTC"
  schedule_expression = "cron(30 9 * * ? *)"
}

resource "aws_ses_email_identity" "sender" {
  email = var.ses_sender_email
}

resource "aws_ses_email_identity" "recipient" {
  email = var.ses_recipient_email
}

resource "aws_iam_role" "step_functions" {
  name = "c21-nathan-t3-step-functions-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          Service = "states.amazonaws.com"
        }
      }
    ]
  })
}

resource "aws_iam_role_policy" "step_functions_policy" {
  name = "c21-nathan-t3-step-functions-policy"
  role = aws_iam_role.step_functions.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "lambda:InvokeFunction"
        ]
        Resource = aws_lambda_function.report_generator.arn
      },
      {
        Effect = "Allow"
        Action = [
          "ses:SendEmail",
          "ses:SendRawEmail"
        ]
        Resource = "*"
      },
      {
        Effect = "Allow"
        Action = [
          "s3:GetObject"
        ]
        Resource = "${aws_s3_bucket.data_lake.arn}/reports/*"
      }
    ]
  })
}

resource "aws_sfn_state_machine" "report_pipeline" {
  name     = "c21-nathan-t3-report-pipeline"
  role_arn = aws_iam_role.step_functions.arn

  definition = jsonencode({
    Comment = "Daily report generation and email pipeline"
    StartAt = "GenerateReport"
    States = {
      GenerateReport = {
        Type     = "Task"
        Resource = "arn:aws:states:::lambda:invoke"
        Parameters = {
          FunctionName = aws_lambda_function.report_generator.function_name
          Payload = {
            "executionId.$" = "$$.Execution.Id"
          }
        }
        ResultPath = "$.reportResult"
        Next       = "SendEmail"
        Catch = [
          {
            ErrorEquals = ["States.ALL"]
            Next        = "ReportGenerationFailed"
          }
        ]
      }
      SendEmail = {
        Type     = "Task"
        Resource = "arn:aws:states:::aws-sdk:sesv2:sendEmail"
        Parameters = {
          Destination = {
            ToAddresses = [var.ses_recipient_email]
          }
          Content = {
            Simple = {
              Body = {
                Html = {
                  "Data.$" = "$.reportResult.Payload.html_content"
                }
              }
              Subject = {
                "Data.$" = "States.Format('Daily Food Trucks Report - {}', $.reportResult.Payload.date)"
              }
            }
          }
          FromEmailAddress = var.ses_sender_email
        }
        ResultPath = "$.emailResult"
        End        = true
      }
      ReportGenerationFailed = {
        Type  = "Fail"
        Cause = "Report generation failed"
        Error = "ReportGenerationError"
      }
    }
  })
}

resource "aws_cloudwatch_event_target" "step_functions" {
  rule      = aws_cloudwatch_event_rule.lambda_daily.name
  target_id = "step-functions-report-target"
  arn       = aws_sfn_state_machine.report_pipeline.arn
  role_arn  = aws_iam_role.eventbridge_step_functions.arn
}

resource "aws_iam_role" "eventbridge_step_functions" {
  name = "c21-nathan-t3-eventbridge-step-functions-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          Service = "events.amazonaws.com"
        }
      }
    ]
  })
}

resource "aws_iam_role_policy" "eventbridge_step_functions_policy" {
  name = "c21-nathan-t3-eventbridge-step-functions-policy"
  role = aws_iam_role.eventbridge_step_functions.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect   = "Allow"
        Action   = "states:StartExecution"
        Resource = aws_sfn_state_machine.report_pipeline.arn
      }
    ]
  })
}

output "ecs_cluster_name" {
  value       = data.aws_ecs_cluster.existing_cluster.cluster_name
  description = "Name of the ECS cluster"
}

output "ecs_task_definition_arn" {
  value       = aws_ecs_task_definition.etl_pipeline.arn
  description = "ARN of the ECS task definition"
}

output "cloudwatch_log_group" {
  value       = aws_cloudwatch_log_group.etl_logs.name
  description = "CloudWatch log group for ECS tasks"
}

output "eventbridge_schedule_name" {
  value       = aws_scheduler_schedule.etl_schedule.name
  description = "Name of the EventBridge Schedule"
}

output "dashboard_service_name" {
  value       = aws_ecs_service.dashboard.name
  description = "Name of the dashboard ECS service"
}

output "lambda_function_name" {
  description = "Name of the report generator Lambda function"
  value       = aws_lambda_function.report_generator.function_name
}

output "lambda_function_arn" {
  description = "ARN of the report generator Lambda function"
  value       = aws_lambda_function.report_generator.arn
}

output "step_functions_state_machine_arn" {
  description = "ARN of the Step Functions state machine"
  value       = aws_sfn_state_machine.report_pipeline.arn
}

output "step_functions_state_machine_name" {
  description = "Name of the Step Functions state machine"
  value       = aws_sfn_state_machine.report_pipeline.name
}

output "ses_sender_email" {
  description = "SES sender email address"
  value       = aws_ses_email_identity.sender.email
}

output "ses_recipient_email" {
  description = "SES recipient email address"
  value       = aws_ses_email_identity.recipient.email
}