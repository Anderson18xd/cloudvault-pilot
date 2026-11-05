# 🛡️ CloudVault Pilot — Cloud Infrastructure & Audit Log

Microservicio de auditoría de archivos desplegado en **AWS** con **Docker Compose**, **NGINX**, **Flask (Gunicorn)**, **Amazon RDS (PostgreSQL)** y **Amazon S3**.

## 🏗️ Arquitectura del Sistema

```mermaid
graph LR
    User([Usuario / Browser]) -->|HTTP :80| NGINX[NGINX Reverse Proxy]
    subgraph VPC [AWS VPC]
        subgraph PublicSubnet [EC2 Ubuntu 24.04 - Docker Compose]
            NGINX -->|Bridge DNS :5000| Flask[Flask + Gunicorn]
        end
        subgraph PrivateSG [RDS Security Group]
            RDS[(Amazon RDS PostgreSQL)]
        end
        Flask -->|SSL TCP :5432| RDS
    end
    Flask -->|IAM Role + SigV4| S3[(Amazon S3 Bucket Privado)]